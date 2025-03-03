import json
import plugins
import os
import requests
from common.log import logger
from common import const
from config import conf
from bridge.reply import Reply, ReplyType
from bridge.context import ContextType
from bridge.bridge import Bridge
from plugins import *
import schedule
import time
from .app import App

import sqlite3

DATABASE = "./data/matches.db"

@plugins.register(
    name="wechatDota",
    desc="基于OpenDota API的信息查询插件",
    version="1.0.0",
    author="flatfish99",
    desire_priority=100
)
class wechatDota(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        self.gewechat_config = self._load_root_config()
        if self.gewechat_config:
            self.app_id = self.gewechat_config.get("gewechat_app_id")
            self.base_url = self.gewechat_config.get("gewechat_base_url")
            self.token = self.gewechat_config.get("gewechat_token")
        else:
            logger.error("[myDota] 无法加载根目录的 config.json 文件，GewechatClient 初始化失败")
        try:
            self.config = super().load_config()
            if not self.config:
                self.config = self._load_config_template()
                self.towxid = self.config.get("towxid")
        except Exception as e:
            logger.error(f"[myDota]初始化异常：{e}")
        logger.info(f"[{__class__.__name__}] initialized")
        self._init_database()
        self.api = App()

    def _load_root_config(self):
        """加载根目录的 config.json 文件"""
        try:
            root_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
            if os.path.exists(root_config_path):
                with open(root_config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                logger.error(f"[myDota] 根目录的 config.json 文件不存在: {root_config_path}")
                return None
        except Exception as e:
            logger.error(f"[myDota] 加载根目录的 config.json 文件失败: {e}")
            return None
    def _init_database(self):
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
    def get_recent_match(self, player_id):
        try:
            res = self.api.api.get_player_recent_matches(player_id)
            startTime = res[0]["start_time"]
            matchId = res[0]["match_id"]
        except:
            startTime = 0
            matchId = 0
        return startTime, matchId
    def update_player_match(self, player_id, player_name, last_match_time, last_match_id):
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
    def check_and_update_matches(self):
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT player_id, player_name, last_match_time, last_match_id FROM player_matches")
            players = cursor.fetchall()

            for player_id, player_name, db_last_match_time, last_match_id in players:
                # 获取最近的比赛时间
                recent_match_time, recent_match_id = self.get_recent_match(player_id)

                # 如果接口返回的时间晚于数据库中的时间
                if recent_match_time > db_last_match_time:
                    print(f"玩家 {player_name} 的比赛时间已更新: {recent_match_time}")

                    # 更新数据库中的比赛时间
                    self.update_player_match(player_id, player_name, recent_match_time, recent_match_id)

                    # 执行 POST 请求
                    self.send_post_request(player_id, player_name, recent_match_id)

    # 执行 POST 请求
    def send_post_request(self, player_id, player_name, recent_match_id):
        content1 = f"{player_name} 最新战报！\n"
        content1 += self.api.getRecentMatches(player_id)
        content2 = self.api.getMatchInfo(recent_match_id)
        url = f"{self.base_url}/message/postText"
        headers = {
            "Content-Type": "application/json",
            "X-GEWE-TOKEN": f"{self.token}",
        }
        data1 = {
            "appId": f"{self.app_id}",
            "toWxid": f"{self.towxid}",
            "ats": "",
            "content": f"{content1}",
        }
        data2 = {
            "appId": f"{self.app_id}",
            "toWxid": f"{self.towxid}",
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
    def run_scheduler(self):
        schedule.every(10).seconds.do(self.check_and_update_matches)  # 每 10 秒执行一次
        while True:
            schedule.run_pending()
            time.sleep(1)


    def on_handle_context(self, e_context: plugins.EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return
        content = e_context["context"].content
        trigger_prefix = conf().get("plugin_trigger_prefix", "$")
        full_prefix = f"{trigger_prefix}dota"
        if not content.startswith(full_prefix):
            e_context.action = EventAction.CONTINUE
            return
        logger.debug("[wechatDota] on_handle_context. content: %s" % content)
        reply = Reply()
        reply.type = ReplyType.TEXT
        parts = content[len(full_prefix):].strip().split(maxsplit=1)
        command = parts[0].lower() if len(parts) > 0 else ""
        args_str = parts[1] if len(parts) > 1 else ""
        if command == "查看比赛":
            # 参数校验
            if not args_str:
                reply.content = "❌ 缺少比赛ID参数"
            elif not args_str.isdigit():
                reply.contnet = "❌ 比赛ID必须为数字"
            else:
                # 调用实际功能函数
                reply.contnet = self.api.getPlayerInfo(args_str)
                #reply = get_match_info(match_id=int(args_str))
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return
        elif command == "查看玩家":
            if not args_str:
                reply.content = "❌ 缺少玩家ID参数"
            elif not args_str.isdigit():
                reply.content = "❌ 玩家ID必须为数字"
            else:

                reply.contnet = self.api.getPlayerInfo(args_str)

            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return
        elif command == "订阅":
            if not args_str:
                reply.content = "❌ 请输入要订阅的玩家ID"
            elif not args_str.isdigit():
                reply.content = "❌ 玩家ID必须为数字"
            else:
                # if subscribe_user(e_context, int(args_str)):
                #     reply.content = "✅ 订阅成功"
                try:
                    playerName = self.api.api.get_player(args_str)['profile']['personaname']
                    self.update_player_match(args_str, playerName, 0, 0)
                    reply.content = "✅ 订阅成功"
                except:
                    reply.content = "❌ 订阅失败"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return
        elif command == "取消订阅":
            if not args_str:
                reply.content = "❌ 请输入要取消订阅的玩家ID"
            elif not args_str.isdigit():
                reply.content = "❌ 玩家ID必须为数字"
            else:
                try:
                    with sqlite3.connect(DATABASE) as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            DELETE FROM player_matches
                            WHERE player_id = ?
                        """, (args_str,))
                        conn.commit()
                    reply.content = "✅ 取消订阅成功"
                except:
                    reply.content = "❌ 取消订阅失败"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return
        else:  # 未知命令
            help_text = self.get_help_text(verbose=True)
            reply.content = f"⚠️ 未知指令\n{help_text}"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return


    def get_help_text(self, verbose=False, **kwargs):
        help_text = "dota2信息获取。"
        trigger_prefix = conf().get("plugin_trigger_prefix", "$")
        if not verbose:
            return help_text
        help_text += "\n使用说明：\n"
        help_text += f"{trigger_prefix}dota 查看比赛 [match id] :获取[match id]比赛信息\n"
        help_text += f"{trigger_prefix}dota 查看玩家 [player id] :获取[player id]玩家信息\n"
        help_text += f"{trigger_prefix}dota 订阅 [player ID]: 订阅[player id]玩家战报。\n"
        help_text += f"{trigger_prefix}dota 取消订阅 [player ID]: 取消订阅[player id]玩家战报。\n"
        return help_text
