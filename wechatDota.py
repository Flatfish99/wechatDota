import json
import plugins
import requests
from common.log import logger
from common import const
from config import conf, get_appdata_dir
from bridge.reply import Reply, ReplyType
from bridge.context import ContextType
from bridge.bridge import Bridge
from plugins import *
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
        try:
            self.config = super().load_config()
            if not self.config:
                self.config = self._load_config_template()

            logger.info(f"[{__class__.__name__}] initialized")
        except Exception as e:
            logger.error(f"[wechatDota]初始化异常：{e}")
            raise "[wechatDota] init failed, ignore "

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
                reply.content = "❌ 缺少玩家ID参数"
            if not args_str.isdigit():
                reply.contnet = "❌ 比赛ID必须为数字"
            else:
                # 调用实际功能函数
                reply.contnet = "比赛详情功能开发中..."
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
                # player_data = fetch_player_stats(int(args_str))
                # reply.content = format_player(player_data)
                reply.content = f"玩家 {args_str} 数据功能开发中..."

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
                reply.content = "订阅功能开发中..."

            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return
        elif command == "取消订阅":
            if not args_str:
                reply.content = "❌ 请输入要取消订阅的玩家ID"
            elif not args_str.isdigit():
                reply.content = "❌ 玩家ID必须为数字"
            else:
                # if unsubscribe_user(e_context, int(args_str)):
                #     reply.content = "✅ 已取消订阅"
                reply.content = "取消订阅功能开发中..."

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
