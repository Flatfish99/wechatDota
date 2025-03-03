from .opendota.DotaAPI import DotaAPI
from datetime import datetime
import json
class App():
    def __init__(self):
        self.api = DotaAPI()
    def getPlayerInfo(self, playerId) -> str:
        try:
            result = self.api.get_player(playerId)
            # 尝试格式化玩家信息
            formatted_result = self.format_player_info(result)
            return formatted_result
        except Exception as e:
            # 捕获异常并返回错误信息
            error_message = f"玩家信息不存在"
            return error_message
    def getMatchInfo(self, matchId) -> str:
        try:
            result = self.api.get_match_details(matchId)
            formatted_result = self.format_match_info(result)
            return formatted_result
        except:
            # 捕获异常并返回错误信息
            error_message = f"比赛信息不存在"
            return error_message
    def getRecentMatches(self, playerId) -> str:
        try:
            result = self.api.get_player_recent_matches(playerId)
            formatted_result = self.format_recent_match_info(result[0])
            #result = self.format_match_info(result[0], playerId)
            return formatted_result
        except:
            # 捕获异常并返回错误信息
            error_message = f"玩家信息不存在"
            return error_message
    def format_player_info(self, info):
        profile = info['profile']
        formatted_string = (
            "玩家信息：\n"
            f"  - 账号ID: {profile['account_id']}\n"
            f"  - 昵称: {profile['personaname']}\n"
            f"  - Steam ID: {profile['steamid']}\n"
            f"  - 国家代码: {profile['loccountrycode']}\n"
            f"  - 头像: {profile['avatarfull']}\n"
            f"  - 个人主页: {profile['profileurl']}\n"
            f"  - 是否Plus会员: {'是' if profile['plus'] else '否'}\n"
            f"  - 等级: {info['rank_tier']}\n"
            f"  - 排行榜排名: {'无' if info['leaderboard_rank'] is None else info['leaderboard_rank']}\n"
        )
        return formatted_string


    def format_match_info(self, match_info, playerId=None):
        # 提取基本信息
        match_id = match_info.get('match_id')
        duration = match_info.get('duration')
        radiant_win = match_info.get('radiant_win')
        radiant_score = match_info.get('radiant_score')
        dire_score = match_info.get('dire_score')
        start_time = match_info.get('start_time')

        # 格式化时间
        duration_minutes = duration // 60
        duration_seconds = duration % 60
        formatted_duration = f"{duration_minutes} 分钟 {duration_seconds} 秒"
        formatted_start_time = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')

        # 格式化比赛结果
        result = "Radiant 胜利" if radiant_win else "Dire 胜利"
        score = f"Radiant {radiant_score} : {dire_score} Dire"
        #英雄编号名称对应字典
        hero_id_to_name = {int(hero_id): self.api.heroes_data[hero_id]['localized_name'] for hero_id, hero_data in self.api.heroes_data.items()}
        # 格式化玩家信息
        players = match_info.get('players', [])
        radiant_players = []
        dire_players = []
        for player in players:
            player_name = player.get('personaname', '未知玩家')
            hero_id = player.get('hero_id')
            hero_name = hero_id_to_name.get(hero_id, f"未知英雄 (ID: {hero_id})")  # 获取英雄名称
            kills = player.get('kills')
            deaths = player.get('deaths')
            assists = player.get('assists')
            net_worth = player.get('net_worth')
            # # 如果传入了 playerId 并且当前玩家是查询的玩家，则突出显示
            # if playerId is not None and player.get('account_id') == playerId:
            #     player_name = f"**{player_name}**"  # 用 ** 标注查询的玩家
            #     hero_name = f"**{hero_name}**"
            #     kills = f"**{kills}**"
            #     deaths = f"**{deaths}**"
            #     assists = f"**{assists}**"
            #     net_worth = f"**{net_worth}**"
            player_info = f"  - {player_name} (英雄: {hero_name}): {kills}/{deaths}/{assists} (K/D/A), 经济: {net_worth}"
            if player.get('isRadiant', False):
                radiant_players.append(player_info)
            else:
                dire_players.append(player_info)

        # 构建最终字符串
        formatted_string = (
                f"比赛信息：\n"
                f"  - 比赛ID: {match_id}\n"
                f"  - 结果: {result}\n"
                f"  - 比分: {score}\n"
                f"  - 持续时间: {formatted_duration}\n"
                f"  - 开始时间: {formatted_start_time}\n"
                f"Radiant 队伍玩家：\n"
                + "\n".join(radiant_players) +
                f"\n------------------------\n"
                f"Dire 队伍玩家：\n"
                + "\n".join(dire_players)
        )
        return formatted_string
    from datetime import datetime

    def format_recent_match_info(self, match_info):
        #英雄编号名称对应字典
        hero_id_to_name = {int(hero_id): self.api.heroes_data[hero_id]['localized_name'] for hero_id, hero_data in self.api.heroes_data.items()}
        # 提取基本信息
        match_id = match_info.get('match_id')
        duration = match_info.get('duration')
        radiant_win = match_info.get('radiant_win')
        start_time = match_info.get('start_time')
        hero_id = match_info.get('hero_id')
        hero_name = hero_id_to_name.get(hero_id, f"未知英雄 (ID: {hero_id})")  # 获取英雄名称
        kills = match_info.get('kills')
        deaths = match_info.get('deaths')
        assists = match_info.get('assists')
        xp_per_min = match_info.get('xp_per_min')
        gold_per_min = match_info.get('gold_per_min')
        hero_damage = match_info.get('hero_damage')
        tower_damage = match_info.get('tower_damage')
        hero_healing = match_info.get('hero_healing')
        last_hits = match_info.get('last_hits')

        # 格式化时间
        duration_minutes = duration // 60
        duration_seconds = duration % 60
        formatted_duration = f"{duration_minutes} 分钟 {duration_seconds} 秒"
        formatted_start_time = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')

        # 格式化比赛结果
        result = "Radiant 胜利" if radiant_win else "Dire 胜利"

        # 构建最终字符串
        formatted_string = (
            f"比赛信息：\n"
            f"  - 比赛ID: {match_id}\n"
            f"  - 结果: {result}\n"
            f"  - 持续时间: {formatted_duration}\n"
            f"  - 开始时间: {formatted_start_time}\n"
            f"玩家表现：\n"
            f"  - 英雄: {hero_name}\n"
            f"  - K/D/A: {kills}/{deaths}/{assists}\n"
            f"  - 经验/分钟: {xp_per_min}\n"
            f"  - 金钱/分钟: {gold_per_min}\n"
            f"  - 英雄伤害: {hero_damage}\n"
            f"  - 塔伤害: {tower_damage}\n"
            f"  - 英雄治疗: {hero_healing}\n"
            f"  - 补刀数: {last_hits}"
        )
        return formatted_string
if __name__ == "__main__":
    app = App()
    print(app.getRecentMatches("123"))


