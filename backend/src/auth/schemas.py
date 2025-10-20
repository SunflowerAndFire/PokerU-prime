from pydantic import Field, BaseModel

class UserCreateModel(BaseModel):
    '''Register form schema'''
    email: str = Field(max_length=40)
    username: str = Field(max_length=8)
    password: str = Field(min_length=6)
    confirm_password: str = Field(min_length=6)

class UserLoginModel(BaseModel):
    '''Login form schema'''
    username: str = Field(max_length=8)
    password: str = Field(min_length=6)

class PasswordResetRequestModel(BaseModel):
    '''Password reset request with email address'''
    email: str

class PasswordResetConfirmModel(BaseModel):
    '''Password reset form'''
    new_password: str = Field(min_length=6)
    confirm_new_password: str = Field(min_length=6)

class ProfileUpdateModel(BaseModel):
    '''Profile update form with username only'''
    username: str = Field(max_length=8)
