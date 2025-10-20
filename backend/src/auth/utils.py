import re
import uuid
import logging
from datetime import datetime, timezone, timedelta
from itsdangerous import URLSafeTimedSerializer
import bcrypt
import jwt

from src.config import Config
from .models import domain_of_college

def generate_hashed_pwd(password: str) -> str:
    '''Hash password to make it secure in DB'''
    # Hashing the password
    hashed_pw = bcrypt.hashpw(
        password.encode('utf-8'), 
        bcrypt.gensalt()
    )

    return hashed_pw

def verify_passsword(plain_password: str, hashed_password: bytes) -> bool:
    '''Compare plain and hashed password'''
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password
    )

REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
def get_email_domain(email: str):
    '''Separate the email domain after @'''
    at_sign = email.index('@')
    domain = email[at_sign + 1:]
    return domain

def get_college_by_email(email: str):
    '''Return the college that connects with the email domain'''
    domain = get_email_domain(email)
    return domain_of_college[domain]

def check_valid_email(email: str):
    '''Check to see if email address is valid + has a partner school domain'''
    # Pass the regular expression and the string into the fullmatch() method
    if not (re.fullmatch(REGEX, email)):
        return False
        
    if get_email_domain(email) not in domain_of_college:
        return False

    return True

def create_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
    '''Create an access token for an user based on their data and expiration time'''
    to_encode = {}
    to_encode['user'] = user_data
    to_encode['exp'] = datetime.now(timezone.utc) + (expiry if expiry else timedelta(minutes=Config.ACCESS_TOKEN_EXPIRY))
    to_encode['jti'] = str(uuid.uuid4())
    to_encode['refresh'] = refresh

    token = jwt.encode(
        payload=to_encode,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM,
    )

    return token

def decode_token(token: str) -> dict:
    '''Get user data based on JWT token'''
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )

        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None

serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET,
    salt="email-configuration"
)
def create_url_safe_token(data: dict):
    '''Create a safe URL with user token to verify their student status'''
    token = serializer.dumps(data, salt="email-configuration")
    return token

def decode_url_safe_token(token: str):
    '''Decode and verify the token received from the user request'''
    try:
        token_data=serializer.loads(token)
        return token_data
    except Exception as e:
        logging.error(str(e))
