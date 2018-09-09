from bs4 import BeautifulSoup
from urllib.request import urljoin
import pandas as pd
import time
import requests
import re

# crawler testing
main_url = "https://www.transfermarkt.de"

# get the link of the five main football leagues of europe
urls = ['https://www.transfermarkt.de/1-bundesliga/startseite/wettbewerb/L1/plus/?saison_id=',
        'https://www.transfermarkt.de/premier-league/startseite/wettbewerb/GB1/plus/?saison_id=',
        'https://www.transfermarkt.de/laliga/startseite/wettbewerb/ES1/plus/?saison_id=',
        'https://www.transfermarkt.de/serie-a/startseite/wettbewerb/IT1/plus/?saison_id=',
        'https://www.transfermarkt.de/ligue-1/startseite/wettbewerb/FR1/plus/?saison_id=']

# the header must be used, otherwise get 404 error
headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}


# define a function, to get the club list
def get_club_link_by_season(year):
    # define two lists to save the name and link later
    clubs_name = []
    clubs_link = []

    # get the name and link, then save them into the lists
    for url in urls:

        lega_url = url + str(year)
        page_liga_2016 = requests.get(lega_url, headers=headers).content
        soup = BeautifulSoup(page_liga_2016, 'html.parser')
        club_table = soup.find('table', attrs={'class': 'items'})

        all_club = club_table.find_all('td', attrs={'class': 'hauptlink no-border-links show-for-small show-for-pad'})

        for club in all_club:
            name = club.text
            link = urljoin(main_url, club.a['href'])

            clubs_name.append(name)
            clubs_link.append(link)

        time.sleep(1)

    # combine the list into a dictionary and save all information into the csv-file
    club_infor = {'name': clubs_name, 'link': clubs_link}
    infor_list = pd.DataFrame(club_infor)
    club_file_name = 'club_' + str(year) + '.csv'
    infor_list.to_csv(club_file_name, index=False, header=False, encoding='utf-8')


# define a function, to get the player chracter and link
def get_player_data(year):
    # read the csv file
    club_table_name = 'club_' + str(year) + '.csv'
    link_needed = pd.read_csv(club_table_name, header=None)
    link_needed.columns = ['Link', 'Club']

    # rebuild the club link list to get the player detail information link
    player_list = []
    for club_link in link_needed['Link']:
        club_main_link = re.sub(r"startseite", "kader", club_link)
        club_link_tail = "/plus/1"
        club_player_link = club_main_link + club_link_tail
        player_list.append(club_player_link)

    # get the player chractristics
    player_data_list = []

    for player_link in player_list:

        # get all player link row by row
        club_page = requests.get(player_link, headers=headers).content
        club_soup = BeautifulSoup(club_page, 'html.parser')
        club_table = club_soup.find('table', attrs={'class': 'items'})
        club_table_body = club_table.find('tbody')

        # get player information of odd rows
        trs = club_table_body.find_all('tr', {'class': 'odd'})
        for tr in trs:
            tds = tr.find_all('td')

            # name_td = tds[1]
            pp_name_infor = tds[1].find('span', attrs={'class': 'show-for-small'})
            player_name = pp_name_infor.find('a').text

            # replace the birthday to age
            player_birth = tds[5].text
            age_split = re.split(r" ", player_birth)
            new_age = age_split[1]
            new_age = re.sub(r"\(", "", new_age)
            new_age = re.sub(r"\)", "", new_age)
            try:
                player_age = int(new_age)
            except ValueError:
                player_age = new_age

            # player link, used to get the performance data later
            player_link = pp_name_infor.find('a')['href']
            player_link = urljoin(main_url, player_link)

            # player ID
            player_id = re.search(r"\d+", player_link).group()

            # transfer the height data from string to float data
            player_height = tds[8].text
            player_height_new = re.sub(r" m", "", player_height)
            try:
                player_height_new = float(re.sub(r",", ".", player_height_new))
            except ValueError:
                continue

            # transfer the value data from string to integer
            player_value = tds[13].text
            if "Mio." in player_value:

                player_value_new = re.sub(r" Mio. €  ", "", player_value)
                player_value_new = float(re.sub(r",", ".", player_value_new))
                player_value_new = int(player_value_new * 1000000)

            elif "Tsd." in player_value:

                player_value_new = re.sub(r" Tsd. €  ", "", player_value)
                player_value_new = float(re.sub(r",", ".", player_value_new))
                player_value_new = int(player_value_new * 1000)

            else:
                player_value_new = re.sub(r"- ", "", player_value)

            player_data_list.append({
                'Position': tds[0]['title'],
                'Player': player_name,
                'Player ID': player_id,
                'Age': player_age,
                "Height in meter": player_height_new,
                'Foot': tds[9].text,
                'Market Value in Euro': player_value_new,
                'Player Link': player_link
            })

        # get player information of even rows
        trs = club_table_body.find_all('tr', {'class': 'even'})
        for tr in trs:
            tds = tr.find_all('td')

            # name_td = tds[1]
            pp_name_infor = tds[1].find('span', attrs={'class': 'show-for-small'})
            player_name = pp_name_infor.find('a').text

            # replace the birthday to age
            player_birth = tds[5].text
            age_split = re.split(r" ", player_birth)
            new_age = age_split[1]
            new_age = re.sub(r"\(", "", new_age)
            new_age = re.sub(r"\)", "", new_age)
            try:
                player_age = int(new_age)
            except ValueError:

                player_age = new_age

            # player link, used to get the performance data later
            player_link = pp_name_infor.find('a')['href']
            player_link = urljoin(main_url, player_link)

            # player ID
            player_id = re.search(r"\d+", player_link).group()

            # transfer the height data from string to float data
            player_height = tds[8].text
            player_height_new = re.sub(r" m", "", player_height)
            try:
                player_height_new = float(re.sub(r",", ".", player_height_new))
            except ValueError:
                continue

            # transfer the value data from string to integer
            player_value = tds[13].text
            if "Mio." in player_value:

                player_value_new = re.sub(r" Mio. €  ", "", player_value)
                player_value_new = float(re.sub(r",", ".", player_value_new))
                player_value_new = int(player_value_new * 1000000)

            elif "Tsd." in player_value:
                player_value_new = re.sub(r" Tsd. €  ", "", player_value)
                player_value_new = float(re.sub(r",", ".", player_value_new))
                player_value_new = int(player_value_new * 1000)

            else:
                player_value_new = re.sub(r"- ", "", player_value)

            player_data_list.append({
                'Position': tds[0]['title'],
                'Player': player_name,
                'Player ID': player_id,
                'Age': player_age,
                "Height in meter": player_height_new,
                'Foot': tds[9].text,
                'Market Value in Euro': player_value_new,
                'Player Link': player_link
            })

        time.sleep(2)

    # all informations in the data-frame saved
    df = pd.DataFrame(player_data_list)
    player_chracter_list_name = 'players_data_' + str(year) + '.csv'
    df.to_csv(player_chracter_list_name, index=False, header=True, encoding='utf-8')
    print(str(year), " finished.")


seasons = [2013, 2014, 2015, 2016, 2017]

for season in seasons:

    #club_link_list = get_club_link_by_season(season)
    player_chractristic_list = get_player_data(season)