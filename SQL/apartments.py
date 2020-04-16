from .main import process_sql


# This function gets the next free apartment ID so that the Add frame
# can automatically fill the ID when the user wants to create a new apartment.
def get_free_apartment_id():
    apartment_ids = (record[0] for record in process_sql("SELECT ApartmentID FROM ApartmentTbl ORDER BY ApartmentID"))

    index = -1
    for index, apartment_id in enumerate(apartment_ids):
        if f"A{index:04}" != apartment_id:
            return f"A{index:04}"
    return f"A{index+1:04}"


# This function gets all of the apartment records alongside any other information required from the database
# and is used to handle searching and sorting so that only the records the user wants to see are fetched.
def get_apartments(sort_field, search_field, search_term):
    sql = f"""SELECT ApartmentID, COUNT(FlatID) AS NumFlats, COALESCE(SUM(NumFlatTenants), 0) AS NumTenants, 
                     COALESCE(SUM(WeeklyRent), 0.00) AS Upkeep, ApartmentAddress, ApartmentPostcode
              FROM (ApartmentTbl LEFT JOIN 
                   (SELECT FlatApartmentTbl.ApartmentID AS FlatApartmentID, 
                           FlatApartmentTbl.FlatID AS FlatID, 
                           COUNT(TenantTbl.TenantID) AS NumFlatTenants,
                           FlatApartmentTbl.WeeklyRent AS WeeklyRent
                    FROM (FlatApartmentTbl LEFT JOIN TenantTbl
                          ON FlatApartmentTbl.FlatID = TenantTbl.FlatID)
                    GROUP BY FlatApartmentTbl.FlatID)
                    ON ApartmentID = FlatApartmentID)"""

    params = tuple()
    if search_term not in ("*", "") and search_field not in ("NumFlats", "NumTenants", "Upkeep"):
        params = (f"{search_term}%",)
        sql += f"\nWHERE {search_field} LIKE ? COLLATE NOCASE"
    sql += f"\nGROUP BY ApartmentID" \
           f"\nORDER BY {sort_field}"

    records = process_sql(sql, parameters=params)
    if search_term in ("*", "") or search_field not in ("NumFlats", "NumTenants", "Upkeep"):
        return records

    index = {"NumFlats": 1, "NumTenants": 2, "Upkeep": 3}.get(search_field)
    return (record for record in records if f"{record[index]:.2f}".startswith(search_term))


# This function gets a specific apartment and its details using the apartment ID to get the record.
def get_apartment(apartment_id):
    sql = f"""SELECT COUNT(FlatID) AS NumFlats, COALESCE(SUM(NumFlatTenants), 0) AS NumTenants, 
                     COALESCE(SUM(WeeklyRent), 0.00) AS Upkeep, 
                     ApartmentAddress, ApartmentPostcode, ApartmentDescription
              FROM (ApartmentTbl LEFT JOIN 
                   (SELECT FlatApartmentTbl.ApartmentID AS FlatApartmentID, 
                           FlatApartmentTbl.FlatID AS FlatID, 
                           COUNT(TenantTbl.TenantID) AS NumFlatTenants,
                           FlatApartmentTbl.WeeklyRent AS WeeklyRent
                    FROM (FlatApartmentTbl LEFT JOIN TenantTbl
                          ON FlatApartmentTbl.FlatID = TenantTbl.FlatID)
                    GROUP BY FlatApartmentTbl.FlatID)
                    ON ApartmentID = FlatApartmentID)
              WHERE ApartmentID = ?
              GROUP BY ApartmentID"""

    return process_sql(sql, parameters=(apartment_id,))


def get_addresses():
    return (record[0] for record in process_sql("SELECT ApartmentAddress FROM ApartmentTbl"))


def add_apartment(record):
    sql = """INSERT INTO ApartmentTbl(ApartmentID, ApartmentAddress, 
                                      ApartmentPostcode, ApartmentDescription)
             VALUES (?, ?, ?, ?)"""
    process_sql(sql, parameters=record)


def edit_apartment(apartment_id, record):
    sql = """UPDATE ApartmentTbl SET
             ApartmentAddress = ?,
             ApartmentPostcode = ?,
             ApartmentDescription = ?
             WHERE ApartmentID = ?"""
    process_sql(sql, parameters=(*record, apartment_id))


# This function deletes an apartment from the database, as well as
# deleting all of its corresponding flats and unbinding those flats
# from the tenants that have them as a foreign key.
def delete_apartment(apartment_id):
    flat_ids = process_sql("SELECT FlatID FROM FlatApartmentTbl WHERE ApartmentID = ?",
                           parameters=(apartment_id,))
    for flat_id in flat_ids:
        sql = f"""UPDATE TenantTbl SET
                 FlatID = NULL
                 WHERE FlatID = ?"""
        process_sql(sql, parameters=flat_id)

    process_sql("DELETE FROM FlatApartmentTbl WHERE ApartmentID = ?", parameters=(apartment_id,))
    process_sql("DELETE FROM ApartmentTbl WHERE ApartmentID = ?", parameters=(apartment_id,))
