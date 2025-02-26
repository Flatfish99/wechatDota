import json
import plugins
import requests
from common.log import logger
from config import conf
from plugins import *
@plugins.register(
    name="wechatDota",
    desc="基于OpenDota API的信息查询插件",
    version="1.0.0",
    author="flatfish99",
    desire_priority=0
)
class wechatDota(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] initialized")


    def get_help_text(self, **kwargs):
        """获取插件帮助信息"""
        help_text = """dota2比赛信息获取
        指令：
        1. 输入 $dota {match ID} 获取某场比赛信息
        2. 输入 $dota {player ID} 获取某玩家信息
        3. 输入 $dota 订阅 {player ID} 订阅某玩家战报
        4. 输入 $dota 取消订阅 {player ID} 取消订阅某玩家战报
        """
        return help_text