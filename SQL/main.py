import sqlite3
import security
from .tables import create_tables_SQL

# defining global connection variable for use in neighbouring methods within this module
global conn


# method to establish connection to database
def establish_connection(db_filename):
    global conn
    conn = sqlite3.connect(db_filename)
        

# method to close connection to database
def close_connection():
    conn.close()


# simple helper function for processing SQL queries
def process_sql(sql, parameters=()):
    cur = conn.cursor()
    cur.execute(sql, parameters)
    conn.commit()

    # All the records are returned even if they are not needed
    # As this makes it easier to use the data returned
    try:
        return cur.fetchall()
    finally:
        cur.close()  # The cursor is closed so that the query is processed successfully


# method to create tables if they do not exist, to be used on program startup
def create_tables():
    for sql in create_tables_SQL:
        process_sql(sql)
        
    if not process_sql("Select * FROM LoginTbl"):
        pwdhash = security.hash_password('password')
        process_sql("INSERT INTO LoginTbl VALUES (?, ?)", parameters=('admin', pwdhash))
