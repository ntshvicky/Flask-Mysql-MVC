
# Import necessary modules
from datetime import datetime, timedelta
from helpers.db_helper import DatabaseHelpers
from helpers.extra_helpers import get_random_string, is_valid_email
from helpers.mail_helpers import sendEmailOtp
from models.route_model import UpdateProfile, UserCreate, UserLogin
import bcrypt
import jwt

import os
from dotenv import load_dotenv
load_dotenv()


def register(user: UserCreate):

    user = user.dict()
    user['password'] = bcrypt.hashpw(user['password'].encode('utf-8'), bcrypt.gensalt())

    if is_valid_email(user['username']):
        if getUserByEmail(user['username']) is not None:
            return False, 'Username or email already exists'

    dbHelpers = DatabaseHelpers()
    return dbHelpers.Insert("users", user)

def login(user: UserLogin):

    columns = ["id", "username", "email", "password", "fullname", "mobile", "insert_date", "active"]
    where_clause = "username = %s or email = %s"
    where_values = (user.username, user.username, )

    dbHelpers = DatabaseHelpers()
    user_record = dbHelpers.getSingleRecord("users", columns, where_clause, where_values)
    if user_record is None:
        return None
    
    if user_record is not None and bcrypt.checkpw(user.password.encode('utf-8'), user_record["password"].encode('utf-8')):
        del user_record['password']
        token = jwt.encode({'public_id' : str(user_record['id']), 'exp' : datetime.utcnow() + timedelta(minutes=1440)}, os.getenv('APP_SECRET_KEY'), algorithm="HS256")
        if token is not None:
            user_record['token'] = token.decode('utf-8')
            res = update_token(user_record['id'], user_record['token'])
            if res > 0:
                return user_record

        return None
    else:
        return None
    

def validateUserToken(user_id: int, token: str):
    columns = ["login_token", 'login_token_date']
    where_clause = "id = %s"
    where_values = (user_id,)

    dbHelpers = DatabaseHelpers()
    user_record = dbHelpers.getSingleRecord("users", columns, where_clause, where_values)
    
    if user_record is None:
        return False
    
    if user_record['login_token'] != token:
        return False

    current_time = datetime.utcnow()
    time_difference = current_time - user_record['login_token_date']

    if time_difference < timedelta(minutes=1440):
        return True
    
    return False


def getUser(user_id: int):
    columns = ["id", "username", "email", "fullname", "mobile", "insert_date", "active"]
    where_clause = "id = %s"
    where_values = (user_id,)

    dbHelpers = DatabaseHelpers()
    user_record = dbHelpers.getSingleRecord("users", columns, where_clause, where_values)
    if user_record is None:
        return None
    
    return user_record


def getUserByEmail(email):
    columns = ["id", "username", "email", "fullname", "mobile", "insert_date", "active"]  # Add "password_reset_otp" to the list of columns
    where_clause = "email = %s"
    where_values = (email,)

    dbHelpers = DatabaseHelpers()
    user_record = dbHelpers.getSingleRecord("users", columns, where_clause, where_values)

    return user_record


def update_token(user_id: int, token: str):
    user = {"login_token": token, "login_token_date": datetime.utcnow()}
    where_clause = "id = %s"
    where_values = (user_id,)
    dbHelpers = DatabaseHelpers()
    return dbHelpers.Update("users", user, where_clause, where_values)

def update_profile(user: UpdateProfile):
    user = user.dict()
    where_clause = "id = %s"
    where_values = (user['user_id'],)
    del user['user_id']
    dbHelpers = DatabaseHelpers()
    return dbHelpers.Update("users", user, where_clause, where_values)


def forgot_password(email: str):
    try:
        user = getUserByEmail(email)
        if user is None:
            # User does not exist
            return False, "User not found"

        # Generate a random password reset OTP
        otp = get_random_string(6)

        # Send the password reset OTP to the user
        sendEmailOtp(user, email, otp)

        # Store the password reset OTP in the database
        update_forgot_password_otp(user["id"], otp)

        return True, "OTP sent successfully"
    except Exception as e:
        return False, str(e)

    
def getPasswordResetOTP(user_id: int):
    columns = ["password_reset_otp"]
    where_clause = "id = %s"
    where_values = (user_id,)

    dbHelpers = DatabaseHelpers()
    user_record = dbHelpers.getSingleRecord("users", columns, where_clause, where_values)
    
    if user_record is None:
        return None
    
    return user_record.get("password_reset_otp")

def update_email_otp(user_id , otp):
    data = dict()
    data['email_verification_otp'] = otp
    data['email_verification_date'] = datetime.utcnow()
    data['email_verification_status'] = 1
    
    where_clause = "id = %s"
    where_values = (user_id,)
    dbHelpers = DatabaseHelpers()
    return dbHelpers.Update("users", data, where_clause, where_values)


def update_email(user_id, email):
    user = {"email": email, "email_verification_status": 0}  # Creating a dictionary with the email
    where_clause = "id = %s"
    where_values = (user_id,)
    dbHelpers = DatabaseHelpers()
    return dbHelpers.Update("users", user, where_clause, where_values)

def change_password(user_id, old_password, new_password):
    try:
        dbHelpers = DatabaseHelpers()
        user = dbHelpers.getSingleRecord("users", ["password"], "id = %s", (user_id,))

        if user is None:
            return False, "User not found"

        if bcrypt.checkpw(old_password.encode('utf-8'), user["password"].encode('utf-8')):
            hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            dbHelpers.Update(
                "users",
                {"password": hashed_new_password},
                "id = %s",
                (user_id,)
            )
            return True, "Password changed successfully"
        else:
            return False, "Invalid old password"
    except Exception as e:
        return False, str(e)

def verify_otp_and_time(user_id, entered_otp, max_time_minutes, columns):

    where_clause = "id = %s"
    where_values = (user_id,)

    dbHelpers = DatabaseHelpers()
    user_record = dbHelpers.getSingleRecord("users", columns, where_clause, where_values)
    if user_record is None:
        return False

    saved_otp = user_record[columns[0]]
    verification_time = user_record[columns[1]]
    verification_status = user_record[columns[2]]
    if verification_status == 0:
        return False, 'Already used OTP'

    if int(saved_otp) == int(entered_otp):
        current_time = datetime.utcnow()
        time_difference = current_time - verification_time

        if time_difference <= timedelta(minutes=max_time_minutes):
            return True, 'Email updated successfully'
        else:
            return False, 'OTP expired'

    return False, 'Invalid OTP'

def validate_user(id: int): 
    try:
        columns = ["id"]
        where_clause = "id = %s"
        where_values = (id,)
        
        dbHelpers = DatabaseHelpers()
        user_record = dbHelpers.getSingleRecord("users", columns, where_clause, where_values)
        if user_record is None:
            return False
            
        return True
    except Exception as e:
        return False
    
def update_forgot_password_otp(user_email: str, otp: str):
    data = dict()
    data['fp_verification_otp'] = otp
    data['fp_verification_date'] = datetime.utcnow()
    data['fp_verification_status'] = 1
    
    where_clause = "email = %s"
    where_values = (user_email,)
    dbHelpers = DatabaseHelpers()
    return dbHelpers.Update("users", data, where_clause, where_values)


def update_forgot_password(user_id, new_password):
    data = dict()
    data['password'] = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    data['fp_verification_status'] = 0
    where_clause = "id = %s"
    where_values = (user_id,)
    dbHelpers = DatabaseHelpers()
    return dbHelpers.Update("users", data, where_clause, where_values)
