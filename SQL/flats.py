from .main import process_sql


# This function gets the next free flat ID so that the Add frame
# can automatically fill the ID when the user wants to create a new flat.
def get_free_flat_id():
    flat_ids = (record[0] for record in process_sql("SELECT FlatID FROM FlatApartmentTbl ORDER BY FlatID"))

    index = -1
    for index, flat_id in enumerate(flat_ids):
        if f"F{index:04}" != flat_id:
            return f"F{index:04}"
    return f"F{index+1:04}"


# This function gets all of the flat records from the database
# and is used to handle searching and sorting so that only the records the user wants to see are fetched.
def get_flats(apartment_id, sort_field, search_field, search_term):
    parameters = (apartment_id,)
    search = ''
    if search_term not in ('*', '') and search_field not in ("Tenants", "WeeklyRent"):
        parameters = (apartment_id, search_term)
        search = f'AND {search_field} LIKE ? COLLATE NOCASE'

    sql = f"""SELECT FlatApartmentTbl.FlatID, FlatNumber, 
              COUNT(TenantTbl.TenantID) AS NumTenants, WeeklyRent
              FROM (FlatApartmentTbl LEFT JOIN TenantTbl
                    ON FlatApartmentTbl.FlatID = TenantTbl.FlatID)
              WHERE ApartmentID = ? {search}
              GROUP BY FlatApartmentTbl.FlatID
              ORDER BY {sort_field}"""

    records = []
    for record in process_sql(sql, parameters=parameters):
        if search_term not in ('*', '') and search_field == "WeeklyRent":
            if not f"{record[3]:.2f}".startswith(search_term):
                continue

        sql = f"""SELECT TenantForename || ' ' || TenantSurname
                  FROM TenantTbl
                  WHERE FlatID = ?"""
        names = [name[0] for name in process_sql(sql, parameters=(record[0],))]
        if search_term not in ('*', '') and search_field == "Tenants":
            # This handles the searching for flats that have the specified tenants linked to them
            if not all(any(record_name.lower().startswith(name.strip()) for record_name in names)
                       for name in search_term.lower().split(',')):
                continue

        record = (*record[1:3], ', '.join(names) or None, record[3])
        records.append(record)
    return records


def get_flat_id(apartment_id, flat_number):
    sql = """SELECT FlatID FROM FlatApartmentTbl
             WHERE ApartmentID = ? AND FlatNumber = ?"""
    return process_sql(sql, parameters=(apartment_id, flat_number))


def add_flat(record):
    sql = """INSERT INTO FlatApartmentTbl(FlatID, ApartmentID, FlatNumber, 
                                          WeeklyRent, FlatDescription)
             VALUES (?, ?, ?, ?, ?)"""
    process_sql(sql, parameters=record)


def edit_flat(flat_id, record):
    sql = """UPDATE FlatApartmentTbl SET
             FlatNumber = ?,
             WeeklyRent = ?,
             FlatDescription = ?
             WHERE FlatID = ?"""
    process_sql(sql, parameters=(*record, flat_id))


# This function deletes a flat from the database, as well as
# unbinding all of its corresponding tenants that have that flat ID as a foreign key.
def delete_flat(flat_id):
    process_sql("UPDATE TenantTbl SET FlatID = NULL WHERE FlatID = ?", parameters=(flat_id,))
    process_sql("DELETE FROM FlatApartmentTbl WHERE FlatID = ?", parameters=(flat_id,))
