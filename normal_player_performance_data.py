from bs4 import BeautifulSoup
import pandas as pd
# import time
import requests
import re

# the header must be used, otherwise get 404 error
headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}

# get the normal player performance data

def get_normal_performance_data(year):
    source_name = "players_data_" + str(year) + ".csv"
    source_table = pd.read_csv(source_name)
    normal_player_table = source_table[source_table.Position != 'Torwart']
    normal_player_link_list = normal_player_table['Player Link']
    performance_data_list_normal = []

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

            # get the amount of match that he played
            einsatz_player = tds_player[4].text
            try:
                einsatz_player = int(einsatz_player)
            except ValueError:
                einsatz_player = ""

            # get the punkte pro spiel
            pps_player = tds_player[5].text
            try:
                pps_player = re.sub(r",", ".", pps_player)
                pps_player = float(pps_player)
            except ValueError:
                pps_player = ""

            # get the goal amount
            tor_player = tds_player[6].text
            try:
                tor_player = int(tor_player)
            except ValueError:
                tor_player = 0

            # assists amount
            tovorlage_player = tds_player[7].text
            try:
                tovorlage_player = int(tovorlage_player)
            except ValueError:
                tovorlage_player = 0

            # eigentore amount
            eigentore_player = tds_player[8].text
            try:
                eigentore_player = int(eigentore_player)
            except ValueError:
                eigentore_player = 0

            # einwechslung amount
            einwechslung_player = tds_player[9].text
            try:
                einwechslung_player = int(einwechslung_player)
            except ValueError:
                einwechslung_player = ""

            # auswechslungen amount
            auswechslung_player = tds_player[10].text
            try:
                auswechslung_player = int(auswechslung_player)
            except ValueError:
                auswechslung_player = ""

            # gelb karte
            gelb_player = tds_player[11].text
            try:
                gelb_player = int(gelb_player)
            except ValueError:
                gelb_player = 0

            # from yellow to red
            gr_player = tds_player[12].text
            try:
                gr_player = int(gr_player)
            except ValueError:
                gr_player = 0

            # red card amount
            rot_player = tds_player[13].text
            try:
                rot_player = int(rot_player)
            except ValueError:
                rot_player = 0

            # elfmeter
            elfmetertore_player = tds_player[14].text
            try:
                elfmetertore_player = int(elfmetertore_player)
            except ValueError:
                elfmetertore_player = 0

            # Minuten pro tor
            minuten_pro_tor_player = tds_player[15].text
            try:
                minuten_pro_tor_player = int(minuten_pro_tor_player)
            except ValueError:
                minuten_pro_tor_player = 0

            # playing time
            eingesetzte_minuten_player = tds_player[16].text
            try:
                eingesetzte_minuten_player = re.sub(r"\'", "", eingesetzte_minuten_player)
                eingesetzte_minuten_player = int(re.sub(r"\.", "", eingesetzte_minuten_player))
            except ValueError:
                pass

            performance_data_list_normal.append({
                "Player ID": player_id,
                "Einsatz": einsatz_player,
                "PPS": pps_player,
                "Tore": tor_player,
                "Torvorlage": tovorlage_player,
                "Eigentore": eigentore_player,
                "Einwechslungen": einwechslung_player,
                "Auswechslungen": auswechslung_player,
                "Gelbe Karte": gelb_player,
                "Gelbe-Rote Karte": gr_player,
                "Rote Karte": rot_player,
                "Elfmeter": elfmetertore_player,
                "Minuten pro Tor": minuten_pro_tor_player,
                "Eingesetzte Minuten": eingesetzte_minuten_player
            })

            # time.sleep(1)
        except AttributeError:
            pass
    normal_performance_csv = "Performance_normal_" + str(year) + ".csv"
    df_normal = pd.DataFrame(performance_data_list_normal)
    df_normal.to_csv(normal_performance_csv, index=False, header=True, encoding='utf-8')
    print("Normal player at ", str(year), " finished")

seasons = [2016, 2017]

for season in seasons:
    get_normal_performance_data(season)