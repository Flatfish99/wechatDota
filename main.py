import sqlite3
import requests
import time
from datetime import datetime
import schedule
import app
# 数据库文件路径
DATABASE = "./data/matches.db"
api = app.App()
# 创建 player_matches 表
def create_table():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_matches (
                player_id INTEGER PRIMARY KEY,
                player_name TEXT,
                last_match_time INTEGER,
                last_match_id INTEGER
            )
        """)
        conn.commit()
        print("数据表已创建或已存在。")

# 插入或更新玩家数据
def update_player_match(player_id, player_name, last_match_time, last_match_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO player_matches (player_id, player_name, last_match_time, last_match_id)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(player_id) DO UPDATE SET
                player_name = excluded.player_name,
                last_match_time = excluded.last_match_time,
                last_match_id = excluded.last_match_id
        """, (player_id, player_name, last_match_time, last_match_id))
        conn.commit()
        print(f"玩家 {player_name} 的数据已更新。")

# 获取最近的比赛时间（模拟接口）
def get_recent_match(player_id):
    # 这里模拟一个接口返回的比赛时间
    res = api.api.get_player_recent_matches(player_id)
    startTime = res[0]["start_time"]
    matchId = res[0]["match_id"]
    return startTime, matchId

# 执行 POST 请求
def send_post_request(player_id, player_name, recent_match_id):
    content1 = f"{player_name} 最新战报！\n"
    content1 += api.getRecentMatches(player_id)
    content2 = api.getMatchInfo(recent_match_id)


    url = "http://192.168.7.75:2531/v2/api/message/postText"
    headers = {
        "Content-Type": "application/json",
        "X-GEWE-TOKEN": "bf5d93989ccc479caa6ad83f659ff7c0",
    }
    data1 = {
        "appId": "wx_E-KZC19Pwid13zIKtBIMX",
        "toWxid": "wxid_thbymlghzo8112",
        "ats": "",
        "content": f"{content1}",
    }
    data2 = {
        "appId": "wx_E-KZC19Pwid13zIKtBIMX",
        "toWxid": "wxid_thbymlghzo8112",
        "ats": "",
        "content": f"{content2}",
    }
    try:
        response = requests.post(url, headers=headers, json=data1)
        response.raise_for_status()
        print(f"POST 请求成功: 玩家 {player_name}")
        response = requests.post(url, headers=headers, json=data2)
        response.raise_for_status()
        print(f"POST 请求成功: 玩家 {player_name}")
    except requests.exceptions.RequestException as e:
        print(f"POST 请求失败: {e}")

# 检查比赛时间并更新
def check_and_update_matches():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT player_id, player_name, last_match_time, last_match_id FROM player_matches")
        players = cursor.fetchall()

        for player_id, player_name, db_last_match_time, last_match_id in players:
            # 获取最近的比赛时间
            recent_match_time, recent_match_id = get_recent_match(player_id)

            # 如果接口返回的时间晚于数据库中的时间
            if recent_match_time > db_last_match_time:
                print(f"玩家 {player_name} 的比赛时间已更新: {recent_match_time}")

                # 更新数据库中的比赛时间
                update_player_match(player_id, player_name, recent_match_time, recent_match_id)

                # 执行 POST 请求
                send_post_request(player_id, player_name, recent_match_id)

# 定时任务
def run_scheduler():
    schedule.every(10).seconds.do(check_and_update_matches)  # 每 10 秒执行一次
    while True:
        schedule.run_pending()
        time.sleep(1)

# 主函数
if __name__ == "__main__":
    create_table()  # 创建表

    # 初始化一些测试数据
    update_player_match(127824480, "南昌外国语高新小学陨落的Carry", 1740713100, 8193712677)


    run_scheduler()  # 启动定时任务