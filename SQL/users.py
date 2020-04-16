import security
from .main import process_sql


def find_hash(username):
    sql = "SELECT PasswordHash FROM LoginTbl WHERE Username=?"
    return process_sql(sql, parameters=(username,))


def get_num_users():
    sql = "SELECT COUNT(*) FROM LoginTbl"
    return process_sql(sql)[0][0]


def get_users():
    sql = "SELECT Username FROM LoginTbl"
    return process_sql(sql)


def add_user(username, password):
    pwdhash = security.hash_password(password)
    sql = "INSERT INTO LoginTbl (Username, PasswordHash) VALUES (?, ?)"
    process_sql(sql, parameters=(username, pwdhash))
    

def del_user(username):
    sql = "DELETE FROM LoginTbl WHERE Username=?"
    process_sql(sql, parameters=(username,))


def change_password(username, password):
    pwdhash = security.hash_password(password)
    sql = "UPDATE LoginTbl SET PasswordHash = ? WHERE Username=?"
    process_sql(sql, parameters=(pwdhash, username))
