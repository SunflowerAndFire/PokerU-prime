from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .models import User
from .schemas import UserCreateModel
from .utils import generate_hashed_pwd, get_college_by_email

class AuthService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        '''Return a user that is registered with a specific email'''
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)

        user = result.first()
        return user

    async def get_user_by_username(self, username: str, session: AsyncSession):
        '''Return a user that is registered with a specific username'''
        statement = select(User).where(User.username == username)
        result = await session.exec(statement)

        user = result.first()
        return user
    
    async def email_exists(self, email: str, session: AsyncSession):
        '''Check if user email exists in DB'''
        user = await self.get_user_by_email(email, session)
        return True if (user is not None) else False
    
    async def username_exists(self, username: str, session: AsyncSession):
        '''Check if username exists in DB'''
        user = await self.get_user_by_username(username, session)
        return True if (user is not None) else False

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        '''Add a new user to DB'''
        user_data_dict = user_data.model_dump()
        new_user = User(
            **user_data_dict
        )
        new_user.hashed_password = generate_hashed_pwd(user_data_dict["password"])
        new_user.college = get_college_by_email(user_data_dict["email"])
        new_user.role = "basic_user"

        session.add(new_user)
        await session.commit()
        session.refresh(new_user)
        return new_user

    async def update_user(self, db_user: User, user_data: dict, session: AsyncSession):
        '''Update an user based on updated fields'''
        for key, val in user_data.items():
            setattr(db_user, key, val)

        await session.commit()
        session.refresh(db_user)
        return db_user

    async def delete_user(self, user_to_delete: User, session: AsyncSession):
        if user_to_delete is not None:
            await session.delete(user_to_delete)
            await session.commit()
            return "User deleted successfully"

        return None
