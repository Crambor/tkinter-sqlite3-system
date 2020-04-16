from .main import process_sql


# This function gets all of the tenant records from the database
# and is used to handle searching and sorting so that only the records the user wants to see are fetched.
def get_free_tenant_id():
    tenant_ids = (record[0] for record in process_sql("SELECT TenantID FROM TenantTbl ORDER BY TenantID"))

    index = -1
    for index, tenant_id in enumerate(tenant_ids):
        if f"T{index:04}" != tenant_id:
            return f"T{index:04}"
    return f"T{index+1:04}"


def get_flat_id(address, flat_number):
    sql = """SELECT FlatApartmentTbl.FlatID
             FROM (FlatApartmentTbl INNER JOIN ApartmentTbl
             ON FlatApartmentTbl.ApartmentID = ApartmentTbl.ApartmentID)
             WHERE (ApartmentTbl.ApartmentAddress = ? AND FlatApartmentTbl.FlatNumber = ?)"""

    try:
        return process_sql(sql, parameters=(address, flat_number))[0][0]
    except IndexError:
        return False


def get_postcode(address):
    sql = "SELECT ApartmentPostcode FROM ApartmentTbl WHERE ApartmentAddress = ?"

    return process_sql(sql, parameters=(address,))


def get_tenants(sort_field, search_field, search_term):
    sql = f"""SELECT TenantID, TenantForename, TenantSurname, TenantContact, 
                    ApartmentAddress, FlatNumber, ApartmentPostcode 
              FROM ((TenantTbl 
              LEFT JOIN FlatApartmentTbl ON TenantTbl.FlatID = FlatApartmentTbl.FlatID)
              LEFT JOIN ApartmentTbl ON FlatApartmentTbl.ApartmentID = ApartmentTbl.ApartmentID)"""

    params = tuple()
    if search_term not in ("*", ""):
        params = (f"{search_term}%",)
        sql += f"\nWHERE {search_field} LIKE ? COLLATE NOCASE"
    sql += f"\nORDER BY {sort_field}"

    return process_sql(sql, parameters=params)


def get_tenant(tenant_id):
    sql = """SELECT TenantForename, TenantSurname, TenantContact, 
                    ApartmentAddress, FlatNumber, TenantDescription FROM ((TenantTbl 
             LEFT JOIN FlatApartmentTbl ON TenantTbl.FlatID = FlatApartmentTbl.FlatID)
             LEFT JOIN ApartmentTbl ON FlatApartmentTbl.ApartmentID = ApartmentTbl.ApartmentID)
             WHERE TenantID = ?"""

    return process_sql(sql, parameters=(tenant_id,))


def add_tenant(record):
    sql = """INSERT INTO TenantTbl(TenantID, FlatID, 
                                   TenantForename, TenantSurname, 
                                   TenantContact, TenantDescription)
             VALUES (?, ?, ?, ?, ?, ?)"""
    process_sql(sql, parameters=record)


def edit_tenant(tenant_id, record):
    sql = """UPDATE TenantTbl SET
             FlatID = ?,
             TenantForename = ?,
             TenantSurname = ?,
             TenantContact = ?,
             TenantDescription = ?
             WHERE TenantID = ?"""
    process_sql(sql, parameters=(*record, tenant_id))


def delete_tenant(tenant_id):
    sql = "DELETE FROM TenantTbl WHERE TenantID = ?"
    process_sql(sql, parameters=(tenant_id,))
