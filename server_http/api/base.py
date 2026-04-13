import re
import uuid
from passlib.hash import bcrypt
from pydantic import BaseModel, Field
from dataclasses import dataclass
from fastapi import FastAPI, Request, HTTPException, Header, Response, Depends, Security
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from user_agents import parse
import aiomysql
from config import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DB,
    ACCESS_TOKEN_EXPIRE_DAYS
)
from redis_client import get_redis, init_redis
from captcha import random_code, generate_captcha_image
from aliyun import SMS
from jwt import create_access_token, decode_access_token

EXAMPLE_PHONE = "18712341234"
DESCRIPTION_PHONE = "手机号"
EXAMPLE_SMS_CODE = "1234"
DESCRIPTION_SMS_CODE = "短信验证码"
EXAMPLE_PASSWORD = "sg2465fdAs"
DESCRIPTION_PASSWORD = "密码，长度为[10, 20]，可以是大小写字母和数字"

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    app.state.mysql_pool = await aiomysql.create_pool(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        db=MYSQL_DB,
        minsize=0,
        #maxsize=10,
        pool_recycle=300
    )
    yield
    app.state.mysql_pool.close()
    await app.state.mysql_pool.wait_closed()

app = FastAPI(lifespan=lifespan)

async def get_mysql_pool(request: Request):
    return request.app.state.mysql_pool

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/user/login")

@dataclass
class CurrentUser:
    id: int
    device_type: str | None

async def get_current_user(
    token: str = Security(oauth2_scheme),
    pool=Depends(get_mysql_pool)
) -> CurrentUser:
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    device_type = payload.get("device_type")
    redis_jti = await get_redis().get(f"jti:{user_id}:{device_type}")
    jti = payload.get("jti")
    if jti != redis_jti:
        raise HTTPException(401, "该Token已被弃用")
    return CurrentUser(
        id=user_id,
        device_type=device_type)

CAPTCHA_EXPIRE = 120        # 2分钟
RATE_LIMIT = 10             # 每分钟最多10次

@app.get("/api/captcha",
    summary="获取图形验证码图片",
    description="有效期2分钟，每分钟最多请求10次",
    responses={
        200: {
            "content": {
                "image/png": {}}}},
    response_class=StreamingResponse)
async def get_captcha(request: Request) -> StreamingResponse:
    redis = get_redis()

    # 获取客户端IP
    ip = request.client.host

    # 防刷 key
    rate_key = f"captcha:rate:{ip}"
    count = await redis.incr(rate_key)
    if count == 1:
        await redis.expire(rate_key, 60)
    if count > RATE_LIMIT:
        raise HTTPException(429, "请求过于频繁")

    # 生成验证码
    code = random_code()
    captcha_id = str(uuid.uuid4())

    # 存 Redis（只存小写，避免大小写问题）
    await redis.setex(
        f"captcha:{captcha_id}",
        CAPTCHA_EXPIRE,
        code.lower()
    )

    # 生成图片
    img = generate_captcha_image(code)

    # 返回图片 + header带captcha_id
    return StreamingResponse(
        img,
        media_type="image/png",
        headers={"X-Captcha-Id": captcha_id}
    )

class SmsCodeRequest(BaseModel):
    phone: str = Field(..., example=EXAMPLE_PHONE, description=DESCRIPTION_PHONE)
    code: str = Field(..., example="g1h2", description="图形验证码，不区分大小写")

@app.post("/api/sms/code",
    summary="请求发送短信验证码",
    description="图形验证码不区分大小写",
    response_class=Response)
async def send_sms_code(
    data: SmsCodeRequest,
    request: Request,
    x_captcha_id: str=Header(..., examples={
        "default": {
            "summary": "验证码ID示例",
            "value": "d0e9ff04-9603-47e7-a024-e657829ed6fd"
        }},
        example="d0e9ff04-9603-47e7-a024-e657829ed6fd"
    )
) -> Response:
    phone = data.phone
    user_input_code = data.code
    captcha_id = x_captcha_id

    if not re.match(r"^1\d{10}$", phone):
        raise HTTPException(400, "手机号格式错误")

    redis = get_redis() 

    key = f"captcha:{captcha_id}"
    real_code = await redis.get(key)

    if not real_code:
        raise HTTPException(400, "验证码已过期")

    # 用完即删（防止重放攻击）
    await redis.delete(key)

    if real_code != user_input_code.lower():
        raise HTTPException(400, "验证码错误")

    # 限流 key
    limit_key = f"sms:limit:{phone}"
    if await redis.exists(limit_key):
        raise HTTPException(429, "发送过于频繁")

    # 发短信
    status = await SMS.sendSmsVerifyCodeRequest(phone)
    if not status:
        raise HTTPException(500, "发送验证码失败")

    # 限流（60秒）
    await redis.set(limit_key, 1, ex=60)

    return Response()

EXAMPLE_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozLCJkZXZpY2VfdHlwZS"
    "I6InBjIiwianRpIjoiYzQzZjk5ZGItZWI5NC00MWUzLWI3MTUtZjhjYzUxMDk3MDk2IiwiZ"
    "XhwIjoxNzc4MjMwODYxLCJpYXQiOjE3NzU2Mzg4NjEsInR5cGUiOiJhY2Nlc3MifQ.AhYlt"
    "IRcCmoBo_v2LjI6y3lgCvDVDUh-R-WpP0taH6Y")

@app.post("/api/user/login",
    summary="用户登陆",
    description="使用手机号和密码登陆，返回Token。有效时间：30天",
    responses={
        200: {
            "description": "登陆成功",
            "content": {
                "application/json": {
                    "example": {"access_token": EXAMPLE_TOKEN}}}}})
async def login(
    request: Request,
    auth: OAuth2PasswordRequestForm = Depends(),
    pool=Depends(get_mysql_pool)
):
    ua = parse(request.headers.get("user-agent"))
    device_type = "pc" if ua.is_pc else "mobile"
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = """
            SELECT `id`, `password` FROM `user`
            WHERE `phone`=%s
            FOR UPDATE
            """

            # 查询是否存在
            await cursor.execute(sql, auth.username)
            row = await cursor.fetchone()

            if not row:
                raise HTTPException(404, "用户不存在")

            user_id, password_hash = row

            # 校验密码
            if not bcrypt.verify(auth.password, password_hash):
                raise HTTPException(400, "密码不正确")

    # 生成 Token
    jti = str(uuid.uuid4())
    token = create_access_token({
        "user_id": user_id,
        "device_type": device_type,
        "jti": jti})
    redis = get_redis()
    await redis.set(f"jti:{user_id}:{device_type}", jti, ex=ACCESS_TOKEN_EXPIRE_DAYS*24*60*60)

    return {"access_token": token}

class UserResgister(BaseModel):
    phone: str = Field(
        ...,
        example=EXAMPLE_PHONE,
        decription=DESCRIPTION_PHONE)
    sms_code: str = Field(
        ...,
        example=EXAMPLE_SMS_CODE,
        description=DESCRIPTION_SMS_CODE)
    password: str = Field(
        ...,
        example=EXAMPLE_PASSWORD,
        description=DESCRIPTION_PASSWORD)

@app.post("/api/user/me",
    summary="注册用户信息",
    description=("用户注册。提供手机号等信息，其中手机号必须有。"),
    response_class=Response)
async def add_user_me(
    data: UserResgister,
    pool=Depends(get_mysql_pool)
) -> Response:
    # 1. 校验验证码
    status = await SMS.checkSmsVerifyCodeRequest(data.phone, data.sms_code)
    if not status:
        raise HTTPException(400, "短信验证码错误")

    # 2. 检验密码格式
    pattern = r'^[A-Za-z0-9]{10,20}$'
    if not re.fullmatch(pattern, data.password):
        raise HTTPException(400, "密码格式错误")
    password_hash = bcrypt.hash(data.password)

    # 3. 注册数据库
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                sql = """
                INSERT INTO `user`
                (`phone`, `password`) VALUES (%s, %s)
                """
                await cursor.execute(sql, (
                    data.phone,
                    password_hash))
            await conn.commit()
        return Response()
    except Exception as e:
        if e.args[0] == 1062:
            raise HTTPException(400, "手机号已注册")

class UserGet(BaseModel):
    id: int = Field(
        ...,
        example=2134,
        description="用户 ID")
    phone: str = Field(
        ...,
        example=EXAMPLE_PHONE,
        decription=DESCRIPTION_PHONE)

@app.get("/api/user/me",
    summary="获取用户信息",
    description=("用户ID, 手机号。"))
async def get_user_me(
    user: CurrentUser = Depends(get_current_user),
    pool=Depends(get_mysql_pool)
) -> UserGet:
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = """
            SELECT `phone` FROM `user`
            WHERE `id`=%s
            """
            await cursor.execute(sql, user.id)
            phone = (await cursor.fetchone())[0]
            
            return {"id": user.id, "phone": phone}

class PasswordChange(BaseModel):
    old_password: str = Field(
        ...,
        example=EXAMPLE_PASSWORD,
        description=DESCRIPTION_PASSWORD)
    new_password: str = Field(
        ...,
        example="dahjg123u3",
        description=DESCRIPTION_PASSWORD)

@app.post("/api/user/password",
    summary="修改密码",
    description="用户登录后修改自己的密码",
    response_class=Response)
async def change_password(
    data: PasswordChange,
    user: CurrentUser = Depends(get_current_user),
    pool=Depends(get_mysql_pool)
):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await conn.begin()

            # 锁住当前用户密码记录
            sql = """
            SELECT `password` FROM user
            WHERE id=%s
            FOR UPDATE
            """
            await cursor.execute(sql, user.id)
            password_hash = (await cursor.fetchone())[0]

            # 校验旧密码
            if not bcrypt.verify(data.old_password, password_hash):
                await conn.rollback()
                raise HTTPException(400, "原密码错误")

            # 生成新 hash
            new_hash = bcrypt.hash(data.new_password)

            # 更新密码
            sql = """
            UPDATE `user` SET `password`=%s
            WHERE `id`=%s
            """
            await cursor.execute(sql, (new_hash, user.id))

            await conn.commit()

        return Response()

class PhoneChange(BaseModel):
    old_phone_sms_code: str = Field(
        ...,
        example=EXAMPLE_SMS_CODE,
        description=DESCRIPTION_SMS_CODE)
    new_phone: str = Field(
        ...,
        example="18712345678",
        description=DESCRIPTION_PHONE)
    new_phone_sms_code: str = Field(
        ...,
        example="5678",
        description=DESCRIPTION_SMS_CODE)

@app.post("/api/user/phone",
    summary="修改手机号",
    description="需提供短信验证码, 新旧手机号不能重复",
    response_class=Response)
async def change_phone(
    data: PhoneChange,
    user: CurrentUser = Depends(get_current_user),
    pool=Depends(get_mysql_pool)
):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await conn.begin()

            # 锁住当前用户
            sql = """
            SELECT `phone` FROM user
            WHERE `id`=%s
            FOR UPDATE
            """
            await cursor.execute(sql, user.id)
            old_phone = (await cursor.fetchone())[0]

            if old_phone == data.new_phone:
                raise HTTPException(400, "手机号重复")

            # 校验短信验证码
            status = await SMS.checkSmsVerifyCodeRequest(old_phone, data.old_phone_sms_code)
            if not status:
                await conn.rollback()
                raise HTTPException(400, "短信验证码错误")

            # 校验短信验证码
            status = await SMS.checkSmsVerifyCodeRequest(data.new_phone, data.new_phone_sms_code)
            if not status:
                await conn.rollback()
                raise HTTPException(400, "短信验证码错误")

            # 更新手机号
            sql = """
            UPDATE `user` SET `phone`=%s
            WHERE `id`=%s
            """
            await cursor.execute(sql, (data.new_phone, user.id))

            await conn.commit()

        return Response()

class UserDelete(BaseModel):
    phone: str = Field(
        ...,
        example=EXAMPLE_PHONE,
        decription=DESCRIPTION_PHONE)
    sms_code: str = Field(
        ...,
        example=EXAMPLE_SMS_CODE,
        description=DESCRIPTION_SMS_CODE)

@app.delete("/api/user/me",
    summary="注销用户信息",
    description=("用户注销。提供手机号和验证码。"),
    response_class=Response)
async def delete_user_me(
    data: UserDelete,
    pool=Depends(get_mysql_pool)
) -> Response:
    # 1. 校验验证码
    status = await SMS.checkSmsVerifyCodeRequest(data.phone, data.sms_code)
    if not status:
        raise HTTPException(400, "短信验证码错误")

    # 2. 注销数据库
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = "DELETE FROM `user` WHERE `phone` = %s"
            await cursor.execute(sql, data.phone)
            rows = cursor.rowcount
        await conn.commit()

    if rows == 0:
        raise HTTPException(404)
    return Response()
