from .main import process_sql


# This function gets the next free employee ID so that the Add frame
# can automatically fill the ID when the user wants to create a new employee.
def get_free_employee_id():
    employee_ids = (record[0] for record in process_sql("SELECT EmployeeID FROM EmployeeTbl ORDER BY EmployeeID"))

    index = -1
    for index, employee_id in enumerate(employee_ids):
        if f"E{index:04}" != employee_id:
            return f"E{index:04}"
    return f"E{index+1:04}"


# This function gets all of the employee records from the database
# and is used to handle searching and sorting so that only the records the user wants to see are fetched.
def get_employees(sort_field, search_field, search_term):
    sql = f"""SELECT EmployeeID, EmployeeForename, EmployeeSurname, 
                     EmployeeContact, EmployeeAddress, EmployeePostcode
              FROM EmployeeTbl"""

    params = tuple()
    if search_term not in ("*", ""):
        params = (f"{search_term}%",)
        sql += f"\nWHERE {search_field} LIKE ? COLLATE NOCASE"
    sql += f"\nORDER BY {sort_field}"

    return process_sql(sql, parameters=params)


# This function gets a specific employee's details using the employee ID to get the record.
def get_employee(employee_id):
    sql = """SELECT EmployeeForename, EmployeeSurname, EmployeeContact, 
                    EmployeeAddress, EmployeePostcode, EmployeeDescription
             FROM EmployeeTbl
             WHERE EmployeeID = ?"""

    return process_sql(sql, parameters=(employee_id,))


def add_employee(record):
    sql = """INSERT INTO EmployeeTbl(EmployeeID, 
                                     EmployeeForename, EmployeeSurname, EmployeeContact, 
                                     EmployeeAddress, EmployeePostcode, EmployeeDescription)
             VALUES (?, ?, ?, ?, ?, ?, ?)"""
    process_sql(sql, parameters=record)


def edit_employee(employee_id, record):
    sql = """UPDATE EmployeeTbl SET
             EmployeeForename = ?,
             EmployeeSurname = ?,
             EmployeeContact = ?,
             EmployeeAddress = ?,
             EmployeePostcode = ?,
             EmployeeDescription = ?
             WHERE EmployeeID = ?"""
    process_sql(sql, parameters=(*record, employee_id))


def delete_employee(employee_id):
    sql = "DELETE FROM EmployeeTbl WHERE EmployeeID = ?"
    process_sql(sql, parameters=(employee_id,))
