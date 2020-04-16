"""
This file contains all of the SQL for the tables, as putting them aside in a separate file
makes the rest of the files far more readable and allows for potential future expansion
"""

LoginTbl_SQL = """
CREATE TABLE IF NOT EXISTS LoginTbl(
        Username              TEXT       NOT NULL    UNIQUE,
        PasswordHash          TEXT       NOT NULL,
        PRIMARY KEY(Username)
        );"""


EmployeeTbl_SQL = """
CREATE TABLE IF NOT EXISTS EmployeeTbl(
        EmployeeID              TEXT        NOT NULL    UNIQUE,
        EmployeeForename        TEXT        NOT NULL,
        EmployeeSurname         TEXT        NOT NULL,
        EmployeeContact         TEXT        NOT NULL,
        EmployeeAddress         TEXT        NOT NULL,
        EmployeePostcode        TEXT        NOT NULL,
        EmployeeDescription     TEXT,
        PRIMARY KEY(EmployeeID)
        );"""


EmployeePaymentsTbl_SQL = """
CREATE TABLE IF NOT EXISTS EmployeePaymentsTbl(
        PaymentID               INTEGER     NOT NULL,
        EmployeeID              TEXT        NOT NULL,
        FOREIGN KEY(PaymentID)  REFERENCES  PaymentsTbl(PaymentID)
        FOREIGN KEY(EmployeeID) REFERENCES  EmployeeTbl(EmployeeID)
        PRIMARY KEY(PaymentID, EmployeeID)
        );"""

PaymentsTbl_SQL = """
CREATE TABLE IF NOT EXISTS PaymentsTbl(
        PaymentID               INTEGER     PRIMARY KEY     AUTOINCREMENT   NOT NULL    UNIQUE,
        PaymentType             TEXT        NOT NULL,
        PaymentMethod           TEXT        NOT NULL,
        TotalPaid               REAL        NOT NULL,
        PaymentDate             TEXT        NOT NULL,
        PaymentTime             TEXT        NOT NULL,
        PaymentDescription      TEXT
        );"""

FlatPaymentsTbl_SQL = """
CREATE TABLE IF NOT EXISTS FlatPaymentsTbl(
        PaymentID               INTEGER     NOT NULL,
        TenantID                TEXT        NOT NULL,
        FOREIGN KEY(PaymentID)  REFERENCES  PaymentTbl(PaymentID),
        FOREIGN KEY(TenantID)   REFERENCES  TenantTbl(TenantID),
        PRIMARY KEY(PaymentID, TenantID)
        );"""


TenantTbl_SQL = """
CREATE TABLE IF NOT EXISTS TenantTbl(
        TenantID                TEXT        NOT NULL    UNIQUE,
        FlatID                  TEXT,
        TenantForename          TEXT        NOT NULL,
        TenantSurname           TEXT        NOT NULL,
        TenantContact           TEXT        NOT NULL,
        TenantDescription       TEXT,
        FOREIGN KEY(FlatID)     REFERENCES  FlatApartmentTbl(FlatID),
        PRIMARY KEY(TenantID)
        );"""

FlatApartmentTbl_SQL = """
CREATE TABLE IF NOT EXISTS FlatApartmentTbl(
        FlatID                  TEXT        NOT NULL    UNIQUE,
        ApartmentID             TEXT        NOT NULL,
        FlatNumber              INTEGER     NOT NULL,
        WeeklyRent              REAL        NOT NULL,
        FlatDescription         TEXT,
        FOREIGN KEY(ApartmentID) REFERENCES ApartmentTbl(ApartmentID),
        PRIMARY KEY(FlatID)
        );"""

ApartmentTbl_SQL = """
CREATE TABLE IF NOT EXISTS ApartmentTbl(
        ApartmentID             TEXT        NOT NULL    UNIQUE,
        ApartmentAddress        TEXT        NOT NULL,
        ApartmentPostcode       TEXT        NOT NULL,
        ApartmentDescription    TEXT,
        PRIMARY KEY(ApartmentID)
        );"""


# A list to store all of the SQL makes it a lot easier to execute in a different file
create_tables_SQL = [LoginTbl_SQL,
                     EmployeeTbl_SQL,
                     EmployeePaymentsTbl_SQL, PaymentsTbl_SQL, FlatPaymentsTbl_SQL,
                     TenantTbl_SQL, FlatApartmentTbl_SQL, ApartmentTbl_SQL]
