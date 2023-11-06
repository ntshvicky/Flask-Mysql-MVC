
# Import necessary modules
import logging
from helpers.db_helper import DatabaseHelpers
from helpers.extra_helpers import getIPDetails

# save log
def saveChangeLog(
        user_id: str,
        action: str,
        ip_address: str,
        request_header: dict,
        browser: str,
        platform: str,
        mobile: str,
        referer: str,
        called_api: str,
        emp_id: str,
        req_data: str
):
    try:
        gloc = getIPDetails(ip_address)
        logs = {
            "user_id": user_id,
            "action": action,
            "ip_address": ip_address,
            "req_header": request_header,
            "browser": browser,
            "platform": platform,
            "referer": referer,
            "mobile": mobile,
            "city": None if 'geoplugin_city' not in gloc else gloc['geoplugin_city'],
            "country": None if 'geoplugin_countryName' not in gloc else gloc['geoplugin_countryName'],
            "region": None if 'geoplugin_continentName' not in gloc else gloc['geoplugin_continentName'],
            "latitude": None if 'geoplugin_latitude' not in gloc else gloc['geoplugin_latitude'],
            "longitude": None if 'geoplugin_longitude' not in gloc else gloc['geoplugin_longitude'],
            "timezone": None if 'geoplugin_timezone' not in gloc else gloc['geoplugin_timezone'],
            "called_api": called_api,
            "emp_id": emp_id,
            "req_data": req_data
        }
        dbHelpers = DatabaseHelpers()
        return dbHelpers.Insert("logs", logs)
    except Exception as e:
        logging.error(f"Integrity Error: {e}")
        return None



# example of list all logs
def list_logs(offset: int = 0, limit: int = 10, order_by: str = None, order_direction: str = None, search_term: str = None):
    columns = ["*"]
    where_clause = "1 = %s"
    where_values = (1,)

    if search_term is not None:
        where_clause += " AND (action LIKE %s OR called_api LIKE %s)"
        where_values += ("%"+search_term+"%","%"+search_term+"%")

    dbHelpers = DatabaseHelpers()
    #read total number of customers based on where_clause
    logs_count = dbHelpers.getCount("logs", "id", where_clause, where_values)
    logs_record = dbHelpers.getRows("logs", columns, where_clause, where_values, offset, limit, order_by, order_direction)
    if logs_record is None:
        return 0, []

    
    return logs_count, logs_record
