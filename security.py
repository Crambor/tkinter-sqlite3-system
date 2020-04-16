# base imports
import os
import hashlib
import binascii


# This function hashes a given password using the sha512 hash function.
def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')
 

# This function uses the same 'salt' as the previous password to compare
# a provided password with the stored password and say whether they match
def verify_password(stored_password, provided_password):
    if not stored_password:
        return False
    
    salt = stored_password[0][0][:64]
    stored_password = stored_password[0][0][64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')

    return pwdhash == stored_password
