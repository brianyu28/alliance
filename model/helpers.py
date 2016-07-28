from werkzeug.security import generate_password_hash, check_password_hash

def get_hashed_password(plain_text_password):
    return generate_password_hash(plain_text_password)

def check_password(plain_text_password, hashed_password):
    return check_password_hash(hashed_password, plain_text_password)
