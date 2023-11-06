


import base64
import os
import random
import re
import shutil
import string

import requests
import xmltodict

from helpers.azure_helpers import upload_file_input


def is_valid_email(email):
    # Regular expression for a basic email validation
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def get_random_string(length):
    # choose from all lowercase letter
    sletters = string.ascii_lowercase
    uletters =  string.ascii_uppercase
    digits = string.digits
    symbols = "#$@!"
    letters = sletters+""+uletters+""+digits+""+symbols
    result_str = ''.join(random.choice(letters) for i in range(length))
    print("Random string of length", length, "is:", result_str)
    return result_str

def get_otp(length):
    # choose from all lowercase letter
    digits = string.digits
    result_str = ''.join(random.choice(digits) for i in range(length))
    print("Random string of length", length, "is:", result_str)
    return result_str

def uploadFile(file, file_name, folder_path):
    if os.path.exists(folder_path) == False:
        os.makedirs(folder_path)

    if file is not None:
        contents = file.read()
        image_path = os.path.join(folder_path, file_name)
        with open(image_path, 'wb') as f:
            f.write(contents)
            
        _, file_path = upload_file_input(image_path, image_path)
        return file_path

    return None

def uploadBase64(file, file_name, folder_path):
    if os.path.exists(folder_path) == False:
        os.makedirs(folder_path)

    if file is not None:
        image_path = os.path.join(folder_path, file_name)
        base64Image = base64.decodebytes(file.encode())
        with open(image_path, "wb") as fh:
            fh.write(base64Image)

        _, file_path = upload_file_input(image_path, image_path)
        return file_path

    return None


def removeDirectory(folder):
    
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            print("Deleting {} from {}".format(filename, folder))
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        shutil.rmtree(folder)
    return True


def getIPDetails(ipAddress):
    try:

        url = f'http://www.geoplugin.net/xml.gp?ip={ipAddress}'
        response = requests.get(url)
        data = xmltodict.parse(response.content)
        return data['geoPlugin']

    except Exception as e:
        print(str(e))
        return {}