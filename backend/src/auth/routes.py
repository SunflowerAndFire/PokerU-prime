from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi import status, APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import Config
from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist
from src.mail import send_message, EmailModel

from .models import User
from .service import AuthService
from .dependencies import get_current_user, RoleChecker, RefreshTokenBearer, AccessTokenBearer
from .schemas import UserCreateModel, UserLoginModel, PasswordResetRequestModel, PasswordResetConfirmModel, ProfileUpdateModel
from .utils import check_valid_email, verify_passsword, generate_hashed_pwd, create_token, create_url_safe_token, decode_url_safe_token

auth_router = APIRouter()
auth_service = AuthService()
access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()
role_checker = RoleChecker(["admin", "staff", "premium_user", "basic_user"])

@auth_router.post(
    "/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED
)
async def create_user_account(
    user_data: UserCreateModel,
    session: AsyncSession = Depends(get_session)
):
    '''Create a new user account'''
    # Validate request fields
    if not (user_data.email and user_data.username and user_data.password and user_data.confirm_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please fill in all required fields"
        )
        
    # Email already exists
    email = user_data.email
    user_exists = await auth_service.email_exists(email, session)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with email already exists"
        )
    
    # Username already exists
    username = user_data.username
    user_exists = await auth_service.username_exists(username, session)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with username already exists"
        )

    # Mismatching passwords
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Validate partner college email
    if not check_valid_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is invalid or your college hasn\'t partnered with us"
        )
    
    # Save new user to DB
    new_user = await auth_service.create_user(user_data, session)

    return new_user

@auth_router.post("/login")
async def login_user(
    login_data: UserLoginModel,
    session: AsyncSession = Depends(get_session)
):
    '''Grant access token to successfully logged-in user'''
    # Validate request fields
    if not (login_data.username and login_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please fill in all required fields"
        )
        
    username = login_data.username
    password = login_data.password
    db_user = await auth_service.get_user_by_username(username, session)

    # Invalid username
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid username"
        )
    
    # Invalid password
    valid_password = verify_passsword(password, db_user.hashed_password)
    if not valid_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid password"
        )
    
    # Handle unverified account
    if not db_user.is_verified:
        # Create the token to include in the URL of verification email
        user_email = db_user.email
        token = create_url_safe_token({"email": user_email})
        link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"
        html_message = f"""
            <h1>Verify Your Email</h1>
            <p>Please click <a href='{link}'>this link</a>to verify your email</p>
        """
                
        # Send verification email
        recipients = [user_email]
        subject = "Thanks for Joining PokerU! Verify Your Email Here!"
        await send_message(recipients, subject, html_message)

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your account through the email we sent you before logging in"
        )
    
    # Generate access & refresh tokens
    access_token = create_token(
        user_data = {
            "username": username,
            "user_uid": str(db_user.uid),
            "role": db_user.role, 
        }
    )

    refresh_token = create_token(
        user_data = {
            "username": username,
            "user_uid": str(db_user.uid),
            "role": db_user.role,
        },
        refresh=True,
        expiry=timedelta(days=Config.REFRESH_TOKEN_EXPIRY)
    )

    return JSONResponse(
        content={
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "username": db_user.username,
                "user_uid": str(db_user.uid)
            }
        }
    )

@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(access_token_bearer)):
    '''Revoke access token to log out user properly'''
    jti = token_details["jti"]
    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={
            "message": "Logged out successfully"
        },
        status_code=status.HTTP_200_OK
    )

@auth_router.get("/verify/{token}")
async def verify_user_account(
    token: str,
    session: AsyncSession = Depends(get_session)
):
    '''Verify student status through the token param in URL'''
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")

    if user_email:
        user = await auth_service.get_user_by_email(user_email, session)

        # User not in db
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
                
        await auth_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Account verified successfully"}
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Error occured during verification"}
    )

@auth_router.get("/me", response_model=User)
async def get_active_user(
    user_details: dict = Depends(get_current_user)
):
    '''Get current active user's data'''
    return user_details

@auth_router.post("/password-reset-request")
async def request_password_reset(email_data: PasswordResetRequestModel):
    '''Send a password reset link to the user email'''
    # Get user email and init the mail's recipients + subject
    user_email = email_data.email
    recipients = [user_email]
    subject = "Reset Your Password"

    # Create the token to include in the URL of password reset email
    token = create_url_safe_token({"email": user_email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
    html_message = f"""
        <h1>Reset Your Password</h1>
        <p>Please click <a href='{link}'>this link</a>to reset your password</p>
    """
                
    # Send password reset email
    await send_message(recipients, subject, html_message)
        
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Please check your email for instructions to reset your password",
        }
    )

@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    password_form: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session)
):
    '''Confirm reset account password through the URL with token'''
    # Empty fields in form
    if not (password_form.new_password and password_form.confirm_new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please fill in all required fields"
        )
        
    # Passwords do not match
    password = password_form.new_password
    cf_password = password_form.confirm_new_password
    if password != cf_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    # Get user email from the token
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")

    # Find the user in DB by email
    if user_email:
        user = await auth_service.get_user_by_email(user_email, session)

        # User not in db
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
                
        # Update user new password with hased value
        await auth_service.update_user(user, {"hashed_password": generate_hashed_pwd(password)}, session)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Password reset successfully"}
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Error occured during password reset"}
    )

@auth_router.patch(
    "/edit-profile",
    dependencies=[Depends(role_checker)]
)
async def update_profile(
    new_profile: ProfileUpdateModel,
    session: AsyncSession = Depends(get_session),
    user_details: dict = Depends(get_current_user)
):
    '''Update profile only when user is verified and permitted'''
    # Empty fields in form
    if not (new_profile.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please fill in all required fields"
    )
        
    # Username is not unique
    new_username = new_profile.username
    user_exists = await auth_service.username_exists(new_username, session)
    if user_exists and new_username != user_details.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User with username already exists'
        )

    # Find user in DB
    user = await auth_service.get_user_by_email(user_details.email, session)

    # User not found in db
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    # Update user profile with new field value (username, etc.)
    await auth_service.update_user(
        user,
        {
            "username": new_username
        },
        session
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Profile update successfully"}
    )

@auth_router.delete(
    "/delete-account",
    dependencies=[Depends(role_checker)]
)
async def delete_user_account(
    session: AsyncSession = Depends(get_session),
    user_details: dict = Depends(get_current_user)
):
    '''Delete user account'''
    user_to_delete = await auth_service.delete_user(user_details, session)

    # User not found in db
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Account deleted successfully"}
    )

@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(refresh_token_bearer)):
    '''Generate a new access token once session is refreshed'''
    expiry_timestamp = token_details["exp"]
        
    # Create a new access token once previous refresh token is expired
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_token(
            user_data=token_details["user"]
        )
                
        return JSONResponse(content={
            "access_token": new_access_token
        })

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired token"
    )

@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    '''Send email with custom message to selected users'''
    recipients = emails.addresses
    subject = "Welcome to PokerU"
    html = "<h1>Welcome to PokerU</h1>"

    await send_message(recipients, subject, html)
    return {"message": "Email sent successfully"}

# delete user account