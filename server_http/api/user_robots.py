from typing import List
from pydantic import BaseModel, Field
from fastapi import Response, Depends, HTTPException
from .base import app, get_mysql_pool, CurrentUser, get_current_user

class Robots(BaseModel):
    robots: List[int] = Field(
        ...,
        example=[1],
        description="机器人ID列表")

@app.post("/api/usr/robots",
    summary="上传用户的机器人",
    description="机器人为数组",
    response_class=Response)
async def post_user_robots(
    data: Robots,
    user: CurrentUser = Depends(get_current_user),
    pool=Depends(get_mysql_pool)
):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await conn.begin()
            try:
                sql = """
                SELECT `robot_id` FROM `user_robot`
                WHERE `user_id`=%s
                """
                await cursor.execute(sql, user.id)
                rows = await cursor.fetchall()
                old_robots = {row[0] for row in rows}
                new_robots = set(data.robots)

                # add robots
                robots = new_robots - old_robots
                if robots:
                    args = [(user.id, robot) for robot in robots]
                    sql = """
                    INSERT INTO `user_robot`
                    (`user_id`, `robot_id`) VALUES (%s, %s)
                    """
                    await cursor.executemany(sql, args)

                # delete robots
                robots = old_robots - new_robots
                if robots:
                    args = [(user.id, robot) for robot in robots]
                    sql = """
                    DELETE FROM `user_robot`
                    WHERE `user_id`=%s AND `robot_id`=%s
                    """
                    await cursor.executemany(sql, args)
                await conn.commit()
            except Exception as e:
                await conn.rollback()
                raise HTTPException(400, ';'.join(map(str, e.args)))
    return Response()

@app.get("/api/user/robots",
    summary="获取机器人列表",
    description="机器人为数组")
async def get_user_robots(
    user: CurrentUser = Depends(get_current_user),
    pool=Depends(get_mysql_pool)
) -> Robots:
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = """
            SELECT `robot_id` FROM `user_robot`
            WHERE `user_id`=%s
            """
            await cursor.execute(sql, user.id)
            rows = await cursor.fetchall()
            robots = [row[0] for row in rows]
            return {"robots": robots}
