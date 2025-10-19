from typing import Any, List
from fastapi.security import HTTPBearer
from fastapi.exceptions import HTTPException
from fastapi import status, Request, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.redis import token_in_blocklist
from src.db.main import get_session

from .service import AuthService
from .utils import decode_token
from .models import User

auth_service = AuthService()

class TokenBearer(HTTPBearer):
    '''Customized parent JWT token class with error handling'''
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        # Token not provided
        if not creds:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "Token not provided",
                    "resolution": "Please get a new token"
                }
            )
        
        token = creds.credentials
        token_data = decode_token(token)

        # Invalid or expired token
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Invalid or expired token",
                    "resolution": "Please get a new token"
                }
            )
        
        # Blocklisted token
        if (await token_in_blocklist(token_data["jti"])):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Invalid or revoked token",
                    "resolution": "Please get a new token"
                }
            )

        # Verify a valid access/refresh token
        self.verify_token_data(token_data)

        # Return decoded token
        return token_data
    
    def verify_token_data(self, token_data: dict):
        '''Check for valid token and make sure it's overriden in child classes'''
        raise NotImplementedError("Please override this method in child class")

class AccessTokenBearer(TokenBearer):
    '''Custom access JWT token'''
    def verify_token_data(self, token_data: dict) -> None:
        '''Verify a valid access JWT token'''
        # Check if it's a refresh token (should be access token)
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token"
            )

class RefreshTokenBearer(TokenBearer):
    '''Custom refresh JWT token'''
    def verify_token_data(self, token_data: dict) -> None:
        '''Verify a valid refresh JWT token'''
        # Check if it's a access token (should be refresh token)
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an refresh token"
            )

async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(AccessTokenBearer())
):
    '''Get current user data (username) based on their access token'''
    username = token_details["user"]["username"]
    user = await auth_service.get_user_by_username(username, session)
    return user

class RoleChecker():
    '''Role-based access control implentation'''
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles
        
    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        '''Validate verified and permitted user role'''
      
        # Unverified user
        if not current_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account not verified"
        )
      
        # Permitted role
        if current_user.role in self.allowed_roles:
            return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to perform this action"
        )
  