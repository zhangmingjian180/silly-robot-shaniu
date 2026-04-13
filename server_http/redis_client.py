import redis.asyncio as aioredis

redis = None

async def init_redis():
    global redis
    redis = await aioredis.from_url(
        "redis://localhost",
        encoding="utf-8",
        decode_responses=True
    )

def get_redis():
    return redis
