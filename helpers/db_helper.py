# Database configurations
import mysql.connector
from mysql.connector import errorcode
from config.db_config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DEFUALT_OFFSET, DEFUALT_LIMIT

class DatabaseHelpers:
    db_cursor = None
    db_connection = None
    def __init__(self):
        self.db_connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        self.db_cursor = self.db_connection.cursor(dictionary=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_cursor.close()
        self.db_connection.close()

    def Insert(self, table_name, data):
        try:
            column = ','.join(data.keys())
            values = ','.join(['%s'] * len(data.values()))
            query = f"INSERT INTO {table_name} ({column}) VALUES ({values})"
            self.db_cursor.execute(query, tuple(data.values()))
            self.db_connection.commit()
            return True, self.db_cursor.lastrowid
        except mysql.connector.Error as err:
            print(err)
            if err.errno == errorcode.ER_DUP_ENTRY:
                return False, 'Duplicate record found'
            else:
                return False, 'Internal server error'
            
    def Update(self, table_name, data, where_clause, where_values):
        try:
            set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

            values = tuple(data.values()) + tuple(where_values)

            self.db_cursor.execute(query, values)
            self.db_connection.commit()
            return self.db_cursor.rowcount
        except mysql.connector.Error as err:
            print(err)
            return 0

            

    def Delete(self, table_name, where_clause, where_values):
        try:
            query = f"DELETE FROM {table_name}"
            values = tuple()
            if where_clause:
                query += f" WHERE {where_clause}"
                values = tuple(where_values)

            self.db_cursor.execute(query, values)
            self.db_connection.commit()
            return self.db_cursor.rowcount
        except mysql.connector.Error as err:
                return 0
            
    def getSingleRecord(self, table_name, columns, where_clause, where_values):
        try:
            query = f"SELECT {','.join(columns)} FROM {table_name}"
            values = tuple()
            if where_clause:
                query += f" WHERE {where_clause}"
                values = tuple(where_values)
            
            self.db_cursor.execute(query, values)
            return self.db_cursor.fetchone()
        except mysql.connector.Error as err:
                return None

    def getRows(self, table_name, columns, where_clause, where_values, offset=DEFUALT_OFFSET, limit=DEFUALT_LIMIT, sort_key=None, sort_dir=None):
        try:
            query = f"SELECT {','.join(columns)} FROM {table_name}"

            values = tuple()
            if where_clause:
                query += f" WHERE {where_clause}"
                values = tuple(where_values)

            if sort_key and sort_dir:
                query += f" ORDER BY {sort_key} {sort_dir}"

            if offset:
                query += f" OFFSET {offset}"
            if limit:
                query += f" LIMIT {limit}"

            self.db_cursor.execute(query, values)
            return self.db_cursor.fetchall()
        except mysql.connector.Error as err:
                print(err)
                return None
        
    def getCount(self, table_name, columns, where_clause, where_values):
        try:
            query = f"SELECT count({columns}) as total FROM {table_name}"

            values = tuple()
            if where_clause:
                query += f" WHERE {where_clause}"
                values = tuple(where_values)

            self.db_cursor.execute(query, values)
            return self.db_cursor.fetchone()['total']
        except mysql.connector.Error as err:
                return 0
        