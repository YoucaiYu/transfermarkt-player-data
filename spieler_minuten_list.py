from bs4 import BeautifulSoup
import pandas as pd
# import time
import requests
import re

headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}

def get_normal_minuten_data(year):
    source_name = "players_data_" + str(year) + ".csv"
    source_table = pd.read_csv(source_name)
    normal_player_table = source_table[source_table.Position != 'Torwart']
    normal_player_link_list = normal_player_table['Player Link']
    minuten_list_normal = []

    for player_link in normal_player_link_list:
        player_main_link = re.sub(r"profil", "leistungsdatendetails", player_link)
        plus_season = '/saison/'
        performance_link_tail = '/verein/0/liga/0/wettbewerb//pos/0/trainer_id/0/plus/1'
        player_performance_link = player_main_link + plus_season + str(year) + performance_link_tail

        # player ID
        player_id = re.search(r"\d+", player_link).group()

        try:

            # get the performance data of normal player
            page_player = requests.get(player_performance_link, headers=headers).content
            player_soup = BeautifulSoup(page_player, 'html.parser')
            table_player = player_soup.find('table', {'class': 'items'})
            table_foot_player = table_player.find('tfoot')
            tds_player = table_foot_player.find_all('td')

            # Minuten pro tor
            minuten_pro_tor_player = tds_player[15].text
            #try:
                #minuten_pro_tor_player = re.sub(r"\'","", minuten_pro_tor_player)
                #minuten_pro_tor_player = int(minuten_pro_tor_player)
            #except ValueError:
                #minuten_pro_tor_player = 0

            minuten_list_normal.append({
                "Player ID": player_id,
                "Minuten pro Tor": minuten_pro_tor_player
            })

            # time.sleep(1)
        except AttributeError:
            pass
    normal_performance_csv = "minuten_normal_" + str(year) + ".csv"
    df_normal = pd.DataFrame(minuten_list_normal)
    df_normal.to_csv(normal_performance_csv, index=False, header=True, encoding='utf-8')
    print("Normal player at ", str(year), " finished")

get_normal_minuten_data(2017)
#seasons = [2016, 2017]

#for season in seasons:
#   get_normal_minuten_data(season)