import pandas as pd
import csv

file_name = 'FB_Fanpage_ID_and_Name_3_new.csv'

with open(file_name) as f:
    reader = csv.reader(f)
    search_keys = []
    for row in reader:
        s_key = row[0]
        s_content = row[2]
        s_symbol = row[3]
        search_keys.append([s_key, s_content, s_symbol])

search_key_list = pd.DataFrame(search_keys)
search_key_list.to_csv('search_keys_list_2.csv', index=False, header=False, encoding='utf-8')