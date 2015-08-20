from bs4 import BeautifulSoup
from decimal import Decimal
from time import gmtime, strftime
from operator import itemgetter
import requests
import re
import sys

def get_top_player_info(mode):
    rank = []
    name = []
    pp = []
    link = []
    top50 = (rank, name, pp, link)
    cnt = 0
    SITE = "https://osu.ppy.sh/p/pp/?m="+mode
    res = requests.get(SITE)
    entire_page = BeautifulSoup(res.text,"lxml")
    rank_list = entire_page.table

    for player_info in rank_list.find_all('tr'):
        for info in player_info.find_all('td'):
            try:
                top50[0].append(info.b.text)
            except:
                pass
        for info in player_info.find_all('td'):
            cnt+=1
            if cnt%2 != 0:
                try:
                    top50[1].append(info.span.text)
                except:
                    pass
        for info in player_info.find_all('td'):
            try:
                top50[2].append(info.a.text)
                top50[3].append(info.a['href'])
            except:
                pass
    return zip(top50[0], top50[1], top50[2], top50[3])

def calc_top_player_bonus_pp(top50_player, mode):
    players = []
    scores = []
    bonuses = []
    result = (players, scores, bonuses)
    for player in top50_player:
        uid = player[3].split('/')[2]
        PP1 = "https://osu.ppy.sh/pages/include/profile-leader.php?u="+uid+"&m="+mode+"&pp=0"
        PP2 = "https://osu.ppy.sh/pages/include/profile-leader.php?u="+uid+"&m="+mode+"&pp=1"
        res_pp1 = requests.get(PP1)
        res_pp2 = requests.get(PP2)
        bs1 = BeautifulSoup(res_pp1.text,"lxml")
        bs2 = BeautifulSoup(res_pp2.text,"lxml")
        score_with_bonus = player[1]
        score_with_bonus = re.sub('pp', '', score_with_bonus)
        score_with_bonus = re.sub(',', '', score_with_bonus)
        score_with_bonus = int(score_with_bonus)
        score = 0
        for item in bs1.select(".pp-display-weight"):
            score += int(item.text.split(" ")[2].split("pp")[0][1:])
        for item in bs2.select(".pp-display-weight"):
            score += int(item.text.split(" ")[2].split("pp")[0][1:])
        result[0].append(player[2])
        result[1].append(score_with_bonus)
        result[2].append(score_with_bonus-score)
    return zip(result[0],result[1],result[2])

if __name__ == "__main__":
    try:
        mode = sys.argv[1]
    except:
        mode = 0
    if mode == "0":
        prefix = "osu"
    elif mode == "1":
        prefix = "taiko"
    elif mode == "2":
        prefix = "ctb"
    elif mode == "3":
        prefix = "mania"

    hidepp = 44

    top50_player = get_top_player_info(mode)
    result = calc_top_player_bonus_pp(top50_player, mode)

    cnt = 0
    tmp = []
    f = open(strftime("log/"+prefix+"_%Y-%m-%d", gmtime())+'_by_rank.log', 'w')
    for item in result:
        cnt += 1
        f.write(str(cnt) + " " + str(item[0]) + " => \n\tpp: " +str(item[1]) + ", bonus pp: " +str(item[2]-hidepp) + "\n")
        tmp.append(item)           

    cnt = 0
    sort_result = sorted(tmp, key=lambda t:t[2])
    f = open(strftime("log/"+prefix+"_%Y-%m-%d", gmtime())+'_by_bonus.log', 'w')
    for item in sort_result:
        cnt += 1
        f.write(str(cnt) + " " + str(item[0]) + " => \n\tpp: " +str(item[1]) + ", bonus pp: " +str(item[2]-hidepp) + "\n")
