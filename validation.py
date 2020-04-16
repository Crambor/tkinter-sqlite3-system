# base imports
import re
import datetime

# modules
import SQL
import security


# User validation
def verify_login(username, password):
    pwdhash = SQL.users.find_hash(username)
    return pwdhash and security.verify_password(pwdhash, password)


def user_exists(username):
    return bool(SQL.users.find_hash(username))


# Employees validation
def employee_exists(employee_id):
    return bool(SQL.employees.get_employee(employee_id))


def check_employee_id(employee_id):
    return bool(re.match(r'^E[0-9]{4}$', employee_id))


# Payments validation
def check_payment_id(payment_id):
    return bool(re.match(r'^P[0-9]{4}$', payment_id))


# Tenants validation
def check_tenant_id(tenant_id):
    return bool(re.match(r'^T[0-9]{4}$', tenant_id))


def tenant_exists(tenant_id):
    return bool(SQL.tenants.get_tenant(tenant_id))


def apartments_exist():
    return bool(SQL.apartments.get_addresses())


# Apartments validation
def check_apartment_id(apartment_id):
    return bool(re.match(r'A[0-9]{4}$', apartment_id))


def apartment_exists(apartment_id):
    return bool(SQL.apartments.get_apartment(apartment_id))


# Flats validation
def apartment_flat_exists(apartment_id, flat_number):
    return bool(SQL.flats.get_flat_id(apartment_id, flat_number))


# Generic multi-table validation
def check_contact(contact):
    return bool(re.match(r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}", contact))


def check_postcode(postcode):
    return bool(re.match(r"^([a-zA-Z]{1,2}\d{1,2})\s(\d[a-zA-Z]{2})$", postcode))


def is_float(amount):
    try:
        float(amount)
    except ValueError:
        return False
    else:
        return True


def check_date(date):
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return False
    else:
        return True


def check_time(time):
    try:
        datetime.datetime.strptime(time, "%H:%M")
    except ValueError:
        return False
    else:
        return True
