VALIDATION_ERROR_CODE = "ER001"
EXCEPTION_ERROR_CODE = "ER002"
RESULT_ERROR_CODE = "ER003"
UNAUTHORIZED_ERROR_CODE = "ER004"

def LoginResponseHelper(token, data, status=True):
    return {
        "status": status,
        "token": token,
        "user": data
    }

def MessageResponseHelper(message, status=True):
    return {
        "status": status,
        "message": message
    }

def DataResponseHelper(data, status=True):
    return {
        "status": status,
        "data":data
    }
def ListResponseHelper(data, total, status=True):
    return {
        "status": status,
        "total": total,
        "results": data
    }

def CustomResponseHelper(data):
    return data

def ErrorResponseHelper(code, error, status=False):
    return {"status": status, "code": code, "error": error}


def UnauthorizedResponseHelper(code, error, status=False):
    return {"status": status, "code": code, "error": error}

def StatusResponseHelper(flag):
    return {
            "status": flag
        }