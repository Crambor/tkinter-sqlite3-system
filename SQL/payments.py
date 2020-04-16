from .main import process_sql


# This function gets all of the payment records from the database
# and is used to handle searching and sorting so that only the records the user wants to see are fetched.
def get_payments(type_search, datetime_sorts, search_field, search_term):
    parameters = ()
    search = ''
    # if there is a search term, add the search to the query
    if search_term not in ('*', ''):
        search = f'AND {search_field} LIKE ? COLLATE NOCASE'
        if type_search not in ('Inbound', 'Outbound'):
            parameters = (f"{search_term}%", f"{search_term}%")
        else:
            parameters = (f"{search_term}%",)

    sql_inbounds = f"""SELECT PaymentsTbl.PaymentID, PaymentType, 
                             (TenantTbl.TenantForename || ' ' || TenantTbl.TenantSurname) AS Payee,
                              PaymentMethod, CAST(TotalPaid AS REAL), PaymentDate, PaymentTime
                       FROM ((PaymentsTbl INNER JOIN FlatPaymentsTbl
                              ON PaymentsTbl.PaymentID = FlatPaymentsTbl.PaymentID)
                              INNER JOIN TenantTbl
                              ON FlatPaymentsTbl.TenantID = TenantTbl.TenantID)
                       WHERE PaymentsTbl.PaymentType = 'Inbound' {search}"""

    sql_outbounds = f"""SELECT PaymentsTbl.PaymentID, PaymentType, 
                              (EmployeeTbl.EmployeeForename || ' ' || EmployeeTbl.EmployeeSurname) AS Payee, 
                               PaymentMethod, CAST(TotalPaid AS REAL), PaymentDate, PaymentTime
                        FROM ((PaymentsTbl INNER JOIN EmployeePaymentsTbl
                               ON PaymentsTbl.PaymentID = EmployeePaymentsTbl.PaymentID)
                               INNER JOIN EmployeeTbl
                               ON EmployeePaymentsTbl.EmployeeID = EmployeeTbl.EmployeeID)
                        WHERE PaymentsTbl.PaymentType = 'Outbound' {search}"""

    if type_search == 'Inbound':
        sql = sql_inbounds
    elif type_search == 'Outbound':
        sql = sql_outbounds
    else:
        sql = f"""{sql_inbounds} 
                  UNION ALL 
                  {sql_outbounds}"""

    sql += f"""\nORDER BY PaymentDate {datetime_sorts['Date']},
                          PaymentTime {datetime_sorts['Time']}"""
    return process_sql(sql, parameters=parameters)


def get_payment(payment_id, payment_type):
    if payment_type == "Inbound":
        sql = f"""SELECT (TenantTbl.TenantID || ' ' ||
                          TenantTbl.TenantForename || ' ' || TenantTbl.TenantSurname) AS Payee,
                          PaymentMethod, TotalPaid, PaymentDate, PaymentTime, PaymentDescription
                  FROM ((PaymentsTbl INNER JOIN FlatPaymentsTbl
                         ON PaymentsTbl.PaymentID = FlatPaymentsTbl.PaymentID)
                         INNER JOIN TenantTbl
                         ON FlatPaymentsTbl.TenantID = TenantTbl.TenantID)
                  WHERE PaymentsTbl.PaymentID = ?"""
    else:
        sql = f"""SELECT (EmployeeTbl.EmployeeID || ' ' || 
                          EmployeeTbl.EmployeeForename || ' ' || EmployeeTbl.EmployeeSurname) AS Payee, 
                          PaymentMethod, TotalPaid, PaymentDate, PaymentTime, PaymentDescription
                  FROM ((PaymentsTbl INNER JOIN EmployeePaymentsTbl
                         ON PaymentsTbl.PaymentID = EmployeePaymentsTbl.PaymentID)
                         INNER JOIN EmployeeTbl
                         ON EmployeePaymentsTbl.EmployeeID = EmployeeTbl.EmployeeID)
                  WHERE PaymentsTbl.PaymentID = ?"""

    return process_sql(sql, parameters=(payment_id,))


def get_payees(payment_type):
    if payment_type == 'Inbound':
        sql = "SELECT TenantID, TenantForename, TenantSurname FROM TenantTbl"
    else:
        sql = "SELECT EmployeeID, EmployeeForename, EmployeeSurname FROM EmployeeTbl"

    return process_sql(sql)


def add_payment(record, payee_id):
    sql = """INSERT INTO PaymentsTbl(PaymentType, PaymentMethod, TotalPaid, 
                                     PaymentDate, PaymentTime, PaymentDescription)
             VALUES (?, ?, ?, ?, ?, ?)"""
    process_sql(sql, parameters=record)

    if record[0] == "Outbound":
        sql = """INSERT INTO EmployeePaymentsTbl(PaymentID, EmployeeID) 
                 VALUES (last_insert_rowid(), ?)"""
    else:
        sql = """INSERT INTO FlatPaymentsTbl(PaymentID, TenantID)
                 VALUES (last_insert_rowid(), ?)"""
    process_sql(sql, parameters=(payee_id,))


def edit_payment(payment_id, payment_type, record, payee_id):
    sql = """UPDATE PaymentsTbl SET
             PaymentMethod = ?,
             TotalPaid = ?,
             PaymentDate = ?,
             PaymentTime = ?,
             PaymentDescription = ?
             WHERE PaymentID = ?"""
    process_sql(sql, parameters=(*record, payment_id))

    if payment_type == "Inbound":
        sql = """UPDATE FlatPaymentsTbl SET
                 TenantID = ?
                 WHERE PaymentID = ?"""
    else:
        sql = """UPDATE EmployeePaymentsTbl SET
                 EmployeeID = ?
                 WHERE PaymentID = ?"""
    process_sql(sql, parameters=(payee_id, payment_id,))


# This function deletes the payments from both the link tables and the payment table
def delete_payment(payment_id, payment_type):
    sql = "DELETE FROM PaymentsTbl WHERE PaymentID = ?"
    process_sql(sql, parameters=(payment_id,))

    if payment_type == "Inbound":
        sql = "DELETE FROM FlatPaymentsTbl WHERE PaymentID = ?"
    else:
        sql = "DELETE FROM EmployeePaymentsTbl WHERE PaymentID = ?"
    process_sql(sql, parameters=(payment_id,))
