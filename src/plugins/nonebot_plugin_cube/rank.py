import sqlite3


def add_point(uid, group_id, name) -> str:
    init()
    point=1
    conn = sqlite3.connect("cube.sqlite")
    cursor = conn.cursor()
    sql = f"select * from sign_in where uid={uid} and belonging_group={group_id}"
    data = cursor.execute(sql).fetchall()
    if data:
        point_now = data[0][1]+point
        sql = f'''UPDATE sign_in set points = {point_now} where uid = {uid} and belonging_group = {group_id}'''
        sql2 = f'''UPDATE sign_in set sender = "{name}" where uid = {uid} and belonging_group = {group_id}'''
        cursor.execute(sql)
        # cursor.execute(sql2)
        cursor.close()
        conn.commit()
        conn.close()
        return data
    else:
        sql = f'''INSERT INTO sign_in VALUES(null, {point}, {group_id}, {uid}, "{name}")'''
        cursor.execute(sql)
        cursor.close()
        conn.commit()
        conn.close()
        return data


def get_point(group: int, uid: int) -> int:
    init()
    conn = sqlite3.connect("cube.sqlite")
    cursor = conn.cursor()
    sql = f"select * from sign_in where belonging_group={group} and uid={uid}"
    cursor.execute(sql)
    point = int(cursor.fetchone()[1])
    cursor.close()
    conn.commit()
    conn.close()
    return point



def init():
    conn = sqlite3.connect("cube.sqlite")
    cursor = conn.cursor()
    sql = """create table if not exists sign_in(
        id integer primary key autoincrement,
        points int not null,
        belonging_group int not null,
        uid int not null,
        sender char
    )
    """
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


def get_rank(group_id):
    init()
    conn = sqlite3.connect("cube.sqlite")
    cursor = conn.cursor()
    order_sql = "SELECT * FROM sign_in ORDER BY points"
    data = cursor.execute(order_sql).fetchall()
    cursor.close()
    conn.commit()
    conn.close()
    rank_text = '本群魔方积分排名：\n获取方式：1.还原魔方\n-------------\n'
    rank_num = 1
    for i in data:
        if i[2]==group_id:
            rank_text += f"{rank_num}.{i[4]}     {i[1]}\n"
            rank_num+=1
    return rank_text
