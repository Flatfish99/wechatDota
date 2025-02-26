from OpenDotaClient import *
import json
import emoji

class DotaAPI(OpenDotaClient):
    def __init__(self):
        super().__init__()
    def get_match_details(self, match_id):
        """获取比赛详情[1](@ref)"""
        return self._get(f"matches/{match_id}")

    def get_player_recent_matches(self, player_id):
        """获取玩家最近比赛记录"""
        return self._get(f"players/{player_id}/recentMatches")

    def get_hero_stats(self):
        """获取英雄统计数据"""
        return self._get("heroStats")

    def search_players(self, name):
        """搜索玩家（需OpenDota高级权限）"""
        return self._get("search", params={"q": name})


if __name__ == "__main__":
    api = DotaAPI()

    # 示例1：获取TI10决赛数据（实际ID需替换）
    # results = api.get_match_details('8190615849')
    # for i in results['players']:
    #     if i['account_id'] == '127824480':
    #         slotPlay = i['player_slot']
    #         playergameslot = i
    # matchidNeed = matchid
    # print(results)

    res = api.get_player_recent_matches('127824480')
    matchidNeed = res[0]['match_id']
    id_hero = res[0]['hero_id']
    h = requests.get('https://raw.githubusercontent.com/odota/dotaconstants/refs/heads/master/build/heroes.json')
    hero = h.json()[str(id_hero)]["localized_name"]
    print(hero, matchidNeed)
