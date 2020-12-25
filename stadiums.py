import json

done_stadium_ids = []
grounds_data = []

for year in range(2000, 2020):
    with open('data/' + str(year) + '_all_matches.json', 'r') as fin:
        yearly_data = json.load(fin)
        for match_data in yearly_data:
            stadium_info = {}
            if match_data['stadium_id'] not in done_stadium_ids:
                done_stadium_ids.append(match_data['stadium_id'])
                stadium_info['stadium_id'] = match_data['stadium_id']
                stadium_info['stadium_name'] = match_data['stadium_name']
                stadium_info['stadium_place'] = match_data['stadium_place']
                grounds_data.append(stadium_info)
    print(len(grounds_data))
    print("Done - Year : ", str(year))

with open('data/grounds_data.json', 'w+') as fout:
    json.dump(grounds_data, fout)