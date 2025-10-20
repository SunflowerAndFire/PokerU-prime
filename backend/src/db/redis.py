import redis.asyncio as redis

from src.config import Config

# Initilize an async Redis client to revoke blocklisted tokens
token_blocklist = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=0
)

async def add_jti_to_blocklist(jti: str) -> None:
    '''Add JWT token to blocklist'''
    await token_blocklist.set(jti, "", ex=Config.JTI_EXPIRY)

async def token_in_blocklist(jti: str) -> bool:
    '''Check if JWT token is blocklisted'''
    jti_found = await token_blocklist.get(jti)
    return jti_found is not None
