import datetime
from functools import wraps
import json
import os
from sys import platform
import pdfkit

from flask import jsonify, redirect, render_template, request, send_from_directory
from flask_cors import CORS
from flask_openapi3 import HTTPBearer, Info, OpenAPI, Server, Tag
from flask_openapi3.models.security import HTTPBearer
from jsonschema import ValidationError
from cruds.employees import count_employees, create_employees, delete_employee, get_employee, list_employees, update_profile_image
from cruds.logs import list_logs, saveChangeLog
from helpers.mail_helpers import sendEmailOtp, sendForgetPasswordOtp
from helpers.response_helpers import EXCEPTION_ERROR_CODE, RESULT_ERROR_CODE, VALIDATION_ERROR_CODE, CustomResponseHelper, DataResponseHelper, ErrorResponseHelper, ListResponseHelper, MessageResponseHelper
from models.response_model import CheckSessionResponseModel, DataResponseModel, ListResponseModel, Unauthorized

from helpers.extra_helpers import get_otp, removeDirectory, uploadFile
from cruds.users import UserCreate, UserLogin, change_password, getUser, getUserByEmail, update_email, update_email_otp, update_forgot_password, update_forgot_password_otp, update_profile, verify_otp_and_time

from models.route_model import BasicQueryString, ChangePasswordModel, EmpCreate, EmpData, EmpIdModel, ForgotPasswordModel, ResetPasswordModel, UpdateEmail, UpdateProfile, UploadModel, UserModel, VerifyEmail
from cruds.users import login as login_user
from cruds.users import register as register_user

import jwt

from dotenv import load_dotenv
load_dotenv()

from queue import Queue
# Create a task queue
task_queue = Queue()

# openapi configuartion
info = Info(title="Flask-SQLAlchemy-MVC API", version="0.0.1")

servers = [
    Server(url="http://localhost:5000")
]

# security scehema
jwtBearer = HTTPBearer(bearerFormat="JWT")
security_schemes = {"jwt": jwtBearer}

app = OpenAPI(__name__, info=info,
              security_schemes=security_schemes, servers=servers, doc_ui=True)
app.config["VALIDATE_RESPONSE"] = True
app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY')
CORS(app)



# Decorators example to check login session
def token_required(f):
    @wraps(f)
    def token_decorator(*args, **kwargs):
        token = None

        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return Unauthorized(message="token is missing").dict(), 401
        try:
            decode_data = jwt.decode(token, app.config['SECRET_KEY'])
            if decode_data is None:
                return Unauthorized(message="token is missing").dict(), 401

            reqData = None
            if request.is_json:
                if "user_id" in request.json:
                    reqData = request.json["user_id"]
            elif request.form is not None:
                if "user_id" in request.form:
                    reqData = request.form["user_id"]

            if reqData is None:
                return Unauthorized(message="token is invalid").dict(), 401
            
            if decode_data["public_id"].lower() != reqData.lower():
                return Unauthorized(message="token is invalid").dict(), 401
            
            '''
            # write you validation logic here
            elif decode_data["public_id"].lower() == reqData.lower():
                if validateUserToken(reqData, token) == False:
                    return Unauthorized(message="token is expired").dict
            else:
                return Unauthorized(message="token is invalid").dict(), 401
            '''
        except Exception as ex:
            return Unauthorized(message="token is invalid").dict(), 401
        return f(*args, **kwargs)

    return token_decorator

# Decorators example to create logs
def data_changes_log(action):
    def inner_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                user_id = None
                emp_id = None
                req_data = None
                if request.is_json:
                    if "user_id" in request.json:
                        user_id = request.json["user_id"]
                    if "emp_id" in request.json:
                        emp_id = request.json["emp_id"]

                    req_data = json.dumps(request.json)

                elif request.form is not None:
                    if "user_id" in request.form:
                        user_id = request.form["user_id"]
                    if "emp_id" in request.form:
                        emp_id = request.form["emp_id"]

                platform = request.headers.get('Sec-Ch-Ua-Platform', '-').replace("\"", "")
                user_agent = request.headers.get('User-Agent', '-').replace("\"", "")
                if platform.lower() == '-':
                    if 'iphone'.lower() in user_agent.lower():
                        platform = 'iphone'
                    elif 'android'.lower() in user_agent.lower():
                        platform = 'android'
                    else:
                        platform = 'browser'

                brw_platform = 'chrome'
                if user_agent.lower() != '-':
                    if platform.lower() == 'iphone' and 'crios' in user_agent.lower():
                        brw_platform = 'chrome'
                    if platform.lower() == 'iphone' and 'crios' not in user_agent.lower():
                        brw_platform = 'safari'
                
                # you can add more logic as per your requirements

                saveChangeLog(
                    user_id = user_id,
                    action = action,
                    ip_address = request.headers.get('X-Real-Ip', '-'),
                    request_header = str(request.headers),
                    browser = brw_platform,
                    platform = platform,
                    mobile = request.headers.get('Sec-Ch-Ua-Mobile', '-').replace("\"", ""),
                    referer = request.headers.get('Referer', '-'),
                    called_api = request.url,
                    emp_id = emp_id,
                    req_data = req_data
                )
                return f(*args, **kwargs)
            except Exception as ex:
                print(str(ex))
                #return Unauthorized(message="Exception: {}".format(str(ex))).dict(), 401
        # Renaming the function name:
        wrapper.__name__ = f.__name__
        return wrapper
    return inner_decorator


@app.post("/api/check_available_session", security=[{'jwt': HTTPBearer()}], responses={"200": CheckSessionResponseModel}, tags=[Tag(name="USER & PROFILE - CHECK SESSION")])
@token_required
def check_available_session(body: UserModel):
    return jsonify({'status': True}), 200

"""
The documents function serves two different routes: the root URL (/) and the /docs URL. 
If the user requests the root URL, the function returns a redirect to the /openapi URL, 
which is the location of the OpenAPI documentation. If the user requests the /docs URL, 
the function returns the OpenAPI documentation itself.
"""
@app.route("/")
@app.route("/docs")
def documents():
    return redirect('/openapi')

@app.post("/api/register",
          doc_ui=True,
          responses={"200": DataResponseModel},
          tags=[Tag(name="USER & PROFILE")])
def register_users(body: UserCreate):

    try:

        flag, result = register_user(body)
        if flag == True:
            return DataResponseHelper(data=result)
        else:
            return ErrorResponseHelper(RESULT_ERROR_CODE, result)
    
    except ValidationError as err:
        return ErrorResponseHelper(VALIDATION_ERROR_CODE, err)
    except Exception as ex:
        return ErrorResponseHelper(EXCEPTION_ERROR_CODE, str(ex))
  
@app.post("/api/login",
          doc_ui=True,
          responses={"200": DataResponseModel},
          tags=[Tag(name="USER & PROFILE")])
def login(body: UserLogin):
    try:
        result = login_user(body)
        if result:
            return DataResponseHelper(data=result)
        else:
            return ErrorResponseHelper(RESULT_ERROR_CODE, "Invalid username or password.")
        
    except ValidationError as err:
        return ErrorResponseHelper(VALIDATION_ERROR_CODE, err)
    except Exception as ex:
        return ErrorResponseHelper(EXCEPTION_ERROR_CODE, str(ex))


@app.post("/api/change_password",
          doc_ui=True,
          security=[{'jwt': HTTPBearer()}],
          responses={"200": DataResponseModel},
          tags=[Tag(name="USER & PROFILE")])
@token_required
def post_change_password(body: ChangePasswordModel):
    try:
        user_id = body.user_id
        old_password = body.old_password
        new_password = body.new_password

        if not user_id or not old_password or not new_password:
            return ErrorResponseHelper(VALIDATION_ERROR_CODE, "Please provide user_id, old_password, and new_password")

        flag, message = change_password(
            user_id, old_password, new_password)
        if flag:
            return MessageResponseHelper(message="Password changed successfully")
        else:
            return ErrorResponseHelper(RESULT_ERROR_CODE, message)

    except Exception as ex:
        return ErrorResponseHelper(EXCEPTION_ERROR_CODE, str(ex))


@app.post("/api/update_profile",
          doc_ui=True,
          security=[{'jwt': HTTPBearer()}],
          responses={"200": DataResponseModel},
          tags=[Tag(name="USER & PROFILE")])
@token_required
def update_profile_data(body: UpdateProfile):
    try:
        result = update_profile(body)
        if result > 0:
            return MessageResponseHelper(message='Profile updated successfully')
        else:
            return ErrorResponseHelper(RESULT_ERROR_CODE, "Profile update failed.")

    except ValidationError as err:
        return ErrorResponseHelper(VALIDATION_ERROR_CODE, err)
    except Exception as ex:
        return ErrorResponseHelper(EXCEPTION_ERROR_CODE, str(ex))


@app.post("/api/update_email",
          doc_ui=True,
          security=[{'jwt': HTTPBearer()}],
          responses={"200": DataResponseModel},
          tags=[Tag(name="USER & PROFILE")])
@token_required
def update_email_data(body: UpdateEmail):

    try:
        email = body.dict()["email"]
        user_id = body.dict()["user_id"]
        if getUserByEmail(email) is not None:
            return ErrorResponseHelper(RESULT_ERROR_CODE, "Email already exists")
        
        users = getUser(user_id=user_id)
        if users is not None:
            otp = get_otp(6)
            # update email otp and time here
            sendEmailOtp(users['fullname'], email, otp)
            res = update_email_otp(user_id, otp)
            if res > 0:
                return MessageResponseHelper(message='An OTP has been sent to your email address.')
        
        return ErrorResponseHelper(RESULT_ERROR_CODE, "Profile update failed.")

    except ValidationError as err:
        return ErrorResponseHelper(VALIDATION_ERROR_CODE, err)
    except Exception as ex:
        return ErrorResponseHelper(EXCEPTION_ERROR_CODE, str(ex))


@app.post("/api/verify_email",
          doc_ui=True,
          security=[{'jwt': HTTPBearer()}],
          responses={"200": DataResponseModel},
          tags=[Tag(name="USER & PROFILE")])
@token_required
def verify_email(body: VerifyEmail):
    try:
        email = body.dict()["email"]
        user_id = body.dict()["user_id"]
        otp = body.dict()["otp"]

        columns = ["email_verification_otp", "email_verification_date", "email_verification_status"]
        flag, msg = verify_otp_and_time(user_id, otp, 15, columns)

        if flag == True:
            res = update_email(user_id, email)
            if res > 0:
                return MessageResponseHelper(message='Email successfully changed.')
            else:
                return ErrorResponseHelper(RESULT_ERROR_CODE, "Email update failed.")
        else:
            return ErrorResponseHelper(RESULT_ERROR_CODE, msg)

    except ValidationError as err:
        return ErrorResponseHelper(VALIDATION_ERROR_CODE, err)
    except Exception as ex:
        return ErrorResponseHelper(EXCEPTION_ERROR_CODE, str(ex))


@app.post("/api/forgot_password",
          doc_ui=True,
          responses={"200": DataResponseModel},
          tags=[Tag(name="USER & PROFILE")])
def forgot_password(body: ForgotPasswordModel):
    try:
        email = body.email
        user = getUserByEmail(email=body.email)
        if user is not None:
            otp = get_otp(6)
            sendForgetPasswordOtp(user['fullname'], email, otp)
            res = update_forgot_password_otp(email, otp)
            if res > 0:
                return MessageResponseHelper(message='An OTP has been sent to your email address.')
            else:
                return ErrorResponseHelper(RESULT_ERROR_CODE, "OTP failed to send.")
            
        return ErrorResponseHelper(RESULT_ERROR_CODE, "User not found.")

    except ValidationError as err:
        return ErrorResponseHelper(VALIDATION_ERROR_CODE, err)
    except Exception as ex:
        return ErrorResponseHelper(EXCEPTION_ERROR_CODE, str(ex))


@app.post("/api/reset_password",
          doc_ui=True,
          responses={"200": DataResponseModel},
          tags=[Tag(name="USER & PROFILE")])
def reset_password(body: ResetPasswordModel):
    try:
        body = body.dict()
        email = body["email"]
        otp = body["otp"]
        new_password = body["new_password"]
        user_record = getUserByEmail(email=email)
        if user_record is None:
            return ErrorResponseHelper(RESULT_ERROR_CODE, "User not found.")
        
        columns = ["fp_verification_otp", "fp_verification_date", "fp_verification_status"]
        flag, msg = verify_otp_and_time(user_record['id'], otp, 15, columns)
        if flag == True:
            res = update_forgot_password(user_record['id'], new_password)
            if res > 0:
                return MessageResponseHelper(message='Password successfully updated.')
            else:
                return ErrorResponseHelper(RESULT_ERROR_CODE, "Password update failed.")
            
        return ErrorResponseHelper(RESULT_ERROR_CODE, msg)

    except ValidationError as err:
        return ErrorResponseHelper(VALIDATION_ERROR_CODE, err)
    except Exception as ex:
        return ErrorResponseHelper(EXCEPTION_ERROR_CODE, str(ex))


##### employees #################################################################

@app.post("/api/add_employee",
          doc_ui=True,
          responses={"200": DataResponseModel},
          security=[{'jwt': HTTPBearer()}],
          tags=[Tag(name="EMPLOYEES")])
@token_required # checking user is authorized
@data_changes_log('employee_added') #creating logs
def add_eployee(body: EmpCreate):
    try:
        user_id = body.dict()['user_id']
        name = body.dict()['name']
        designation = body.dict()['designation']

        emp_code = f"{count_employees():05d}" #str(uuid.uuid4())
        image_dir = f"uploads/{emp_code}"
        os.makedirs(image_dir, exist_ok=True) # create a dierctory for employee

        emp = {
            'emp_code': emp_code,
            'user_id': user_id,
            'name': name.strip(),
            'designation': designation.strip()
        }

        f, res = create_employees(emp)
        if f == True:
            return MessageResponseHelper(message="Employee data saved")
        else:
            return ErrorResponseHelper(RESULT_ERROR_CODE, "Employee data save failed")                      
    except ValidationError as err:
        return ErrorResponseHelper(VALIDATION_ERROR_CODE, err)
    except Exception as ex:
        return ErrorResponseHelper(EXCEPTION_ERROR_CODE, str(ex))


@app.delete("/api/employee/delete",
          doc_ui=True,
          responses={"200": DataResponseModel},
          security=[{'jwt': HTTPBearer()}],
          tags=[Tag(name="EMPLOYEES")])
@token_required # checking user is authorized
@data_changes_log('employee_deleted') #creating logs
def delete_employee_data(body: EmpIdModel):
    try:
        emp_id = body.dict()['emp_id']
        
        # read project data
        emp_data = get_employee(emp_id)
        if emp_data == None:
            return ErrorResponseHelper(RESULT_ERROR_CODE, "Employee record not found")
        
        flag = delete_employee(emp_id)
        if flag == True:
            image_dir = f"uploads/{emp_data['emp_code']}/"
            removeDirectory(image_dir)
            return MessageResponseHelper(message="Employee records deleted successfully")
        else:
            return ErrorResponseHelper(RESULT_ERROR_CODE, "Employee records deletion failed")
                                     
    except ValidationError as err:
        return ErrorResponseHelper(VALIDATION_ERROR_CODE, err)
    except Exception as ex:
        return ErrorResponseHelper(EXCEPTION_ERROR_CODE, str(ex))
    

@app.post("/api/employee/upload_image",
          doc_ui=True,
          responses={"200": DataResponseModel},
          security=[{'jwt': HTTPBearer()}],
          tags=[Tag(name="EMPLOYEES")])
@token_required # checking user is authorized
@data_changes_log('profile_image_update') #creating logs
def post_upload_image(form: UploadModel):
    try:
        emp_id = form.dict()['emp_id']
        file = form.dict()['file']
        
        emp_data = get_employee(emp_id)
        if emp_data == None:
            return ErrorResponseHelper(RESULT_ERROR_CODE, "Employee record not found")

        emp_code = emp_data['emp_code']
        image_dir = f"uploads/{emp_code}/"
        os.makedirs(image_dir, exist_ok=True)

        #upload images
        file_extension = file.filename.split('.')[-1]
        file_filename = f"{emp_code+'.'+file_extension}"
        
        file_path = uploadFile(file, file_filename, image_dir)
        if file_path == None:
            return MessageResponseHelper(message="File uploading failed. Please try again or contact support.")
    
        flag = update_profile_image(emp_id, file_path)
        if flag == True:
            return MessageResponseHelper(message="Image uploaded successfully")
        else:
            return ErrorResponseHelper(RESULT_ERROR_CODE, "Image upload failed")
                                     
    except ValidationError as err:
        return ErrorResponseHelper(VALIDATION_ERROR_CODE, err)
    except Exception as ex:
        return ErrorResponseHelper(EXCEPTION_ERROR_CODE, str(ex))
    


@app.post("/api/employee/print_logs",
          doc_ui=True,
          responses={"200": DataResponseModel},
          security=[{'jwt': HTTPBearer()}],
          tags=[Tag(name="EMPLOYEES")])
def print_pdf_logs(body: EmpIdModel):
    try:
        emp_id = body.dict()['emp_id']
        emp_data = get_employee(emp_id)
        if emp_data == None:
            return ErrorResponseHelper(RESULT_ERROR_CODE, "Employee record not found")
        
        emp_code = emp_data['emp_code']
        pdf_dir = f"uploads/{emp_code}/"
        os.makedirs(pdf_dir, exist_ok=True)
        pdfpath = pdf_dir + "{}.pdf".format(emp_code)
        
        pdf_url = generatePdf(emp_data, pdfpath)
        if pdf_url == None:
            return ErrorResponseHelper(RESULT_ERROR_CODE, "PDF generation failed")
        else:
            '''
            # code for azure storage
            flag, cloud_url = upload_file_input(pdf_url, pdf_url, 'application/pdf')
            if flag == True:
                removeDirectory(pdf_dir)
                return CustomResponseHelper({'url': cloud_url, 'status': True})
            else:
                return ErrorResponseHelper(RESULT_ERROR_CODE, "PDF failed to upload in cloud. Please try again or contact support.")
            '''          
            return CustomResponseHelper({'url': pdf_url, 'status': True})    
    except ValidationError as err:
        return ErrorResponseHelper(VALIDATION_ERROR_CODE, err)
    except Exception as ex:
        return ErrorResponseHelper(EXCEPTION_ERROR_CODE, str(ex))

def generatePdf(res, pdfpath):
    try:
        print("Generating PDF")
        options = {
            'page-size': 'Letter',
            'footer-right': '[page] of [topage]',
        }

        '''
        # code to generate base64 encoded image for logo and background
        with open("static/img/Logo.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            data["logo"] = "data:image/png;base64," + encoded_string.decode("utf-8")
        '''

        #code for read data
        res['print_date'] = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

        nCnt, log_arr = list_logs(offset = 0, limit = 10, order_by = None, order_direction = None, search_term = None)
        res['logs'] = log_arr

        renderr = render_template("report.html", data=res)
        
        if platform.lower() == "linux" or platform.lower() == "linux2" or platform.lower() == "darwin":
            config = pdfkit.configuration(wkhtmltopdf="/usr/local/bin/wkhtmltopdf")
            pdfkit.from_string(renderr, pdfpath, options=options, configuration=config)
        else:
            pdfkit.from_string(renderr, pdfpath, options=options)
        return pdfpath
    except Exception as ex:
        print(str(ex))
        return None


@app.post("/api/employee/list",
          doc_ui=True,
          responses={"200": ListResponseModel},
          security=[{'jwt': HTTPBearer()}],
          tags=[Tag(name="EMPLOYEES")])
@token_required
def get_employees_list(query: BasicQueryString, body: UserModel):
    try:
        user_id = body.dict()['user_id']
        offset = int(query.dict()['offset'])
        limit = int(query.dict()['limit'])
        order_by = query.dict()['order_by']
        order_direction = query.dict()['order_direction']
        search_term = query.dict()['search_term']
        
        # just an example
        nCnt, data = list_employees(user_id, offset, limit, order_by, order_direction, search_term)
        return ListResponseHelper(data=data, total=nCnt)
                                     
    except ValidationError as err:
        return ErrorResponseHelper(VALIDATION_ERROR_CODE, err)
    except Exception as ex:
        return ErrorResponseHelper(EXCEPTION_ERROR_CODE, str(ex))
    


@app.post("/api/employee",
          doc_ui=True,
          responses={"200": DataResponseModel},
          security=[{'jwt': HTTPBearer()}],
          tags=[Tag(name="EMPLOYEES")])
@token_required
def get_employee_data(body: EmpIdModel):
    try:
        emp_id = body.dict()['emp_id']
        data = get_employee(emp_id)
        return DataResponseHelper(data=data)
                                     
    except ValidationError as err:
        return ErrorResponseHelper(VALIDATION_ERROR_CODE, err)
    except Exception as ex:
        return ErrorResponseHelper(EXCEPTION_ERROR_CODE, str(ex))

# -------------------------- Uploaded file API ---------------------------------
# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<new_folder_name>/<new_folder_name2>/<new_folder_name3>/<filename>')
def uploaded_file3(new_folder_name, new_folder_name2, new_folder_name3, filename):
    return send_from_directory(os.path.join("../uploads", new_folder_name, new_folder_name2, new_folder_name3),
                               filename)


@app.route('/uploads/<new_folder_name>/<new_folder_name2>/<filename>')
def uploaded_file2(new_folder_name, new_folder_name2, filename):
    return send_from_directory(os.path.join("../uploads", new_folder_name, new_folder_name2),
                               filename)


@app.route('/uploads/<new_folder_name>/<filename>')
def uploaded_file1(new_folder_name, filename):
    return send_from_directory(os.path.join("../uploads", new_folder_name),
                               filename)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory("../uploads",
                               filename)

