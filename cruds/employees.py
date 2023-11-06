
# Import necessary modules
from MySQLdb import IntegrityError
from models.route_model import EmpData, EmpUpdate

from helpers.db_helper import DatabaseHelpers
import logging


def create_employees(empData: dict):
    try:
        dbHelpers = DatabaseHelpers()
        return dbHelpers.Insert("employees", empData)
    except IntegrityError as e:
        logging.error(f"Integrity Error: {e}")
        return False, 'Duplicate employee code'
    except Exception as e:
        logging.error(f"Exception: {e}")
        return False, f"Exception: {e}"


def update_profile_image(emp_id: int, profile: str):
    try:
        where_clause = "id = %s"
        where_values = (emp_id,)
        columns = {'profile': profile}
        dbHelpers = DatabaseHelpers()
        res = dbHelpers.Update("employees", columns, where_clause, where_values)
        if res > 0:
            return True, 'Employee data updated successfully'
        else:
            return False, 'Employee data update failed'
    except Exception as e:
        logging.error(f"Exception: {e}")
        return False, f"Exception: {e}"

def update_employee_data(emp: EmpUpdate):
    try:
        where_clause = "id = %s"
        where_values = (emp.id,)
        columns = {
                'name': emp.name,
                'designation': emp.designation
            }
        dbHelpers = DatabaseHelpers()
        res = dbHelpers.Update("employees", columns, where_clause, where_values)
        if res > 0:
            return True, 'Employee data updated successfully'
        else:
            return False, 'Employee data update failed'
    except Exception as e:
        logging.error(f"Exception: {e}")
        return False


def delete_employee(emp_id: int):
    try:
        where_clause = "id = %s"
        where_values = (emp_id,)
        dbHelpers = DatabaseHelpers()
        res = dbHelpers.Delete("employees", where_clause, where_values)
        if res > 0:
            return True, 'Employee data deleted successfully'
        else:
            return False, 'Employee data delete failed'
    except Exception as e:
        logging.error(f"Exception: {e}")
        return False

def count_employees():
    dbHelpers = DatabaseHelpers()
    res = dbHelpers.getCount("employees", "*", None, None)
    return res

def get_employee_by_code(emp_code: str):
    columns = ["*"]
    where_clause = "emp_code = %s"
    where_values = (emp_code,)

    dbHelpers = DatabaseHelpers()
    emp_record = dbHelpers.getSingleRecord("employees", columns, where_clause, where_values)
    if emp_record is None:
        return None
    return {**emp_record}

def get_employee(emp_id: int):
    columns = ["*"]
    where_clause = "id = %s"
    where_values = (emp_id,)

    dbHelpers = DatabaseHelpers()
    emp_record = dbHelpers.getSingleRecord("employees", columns, where_clause, where_values)
    if emp_record is None:
        return None
    return {**emp_record}

def list_employees(user_id: int, offset: int = 0, limit: int = 10, order_by: str = None, order_direction: str = None, search_term: str = None):
    
    columns = ["*"]
    where_clause = "user_id = %s"
    where_values = (user_id,)

    if search_term is not None:
        where_clause += " AND (name LIKE %s OR designation LIKE %s OR emp_code LIKE %s)"
        where_values += ("%"+search_term+"%","%"+search_term+"%","%"+search_term+"%")

    dbHelpers = DatabaseHelpers()
    #read total number of customers based on where_clause
    emp_count = dbHelpers.getCount("employees", "id", where_clause, where_values)
    emp_record = dbHelpers.getRows("employees", columns, where_clause, where_values, offset, limit, order_by, order_direction)
    if emp_record is None:
        return 0, []

    
    return emp_count, emp_record
