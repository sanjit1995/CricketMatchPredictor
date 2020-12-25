import requests
import json
import os

month_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
team_dict = {1: 'England', 2: 'Australia', 3: 'South-Africa', 4: 'West-Indies', 5: 'New-Zealand',
             6: 'India', 7: 'Pakistan', 8: 'Sri-Lanka', 25: 'Bangladesh'}

for year in range(2000, 2021):
    for team_id in team_dict.keys():
        matches_list = []
        for month in month_list:
            matches_data = requests.get(r"https://hs-consumer-api.espncricinfo.com/v1/pages/team/schedule?teamId=" +
                                        str(team_id) +
                                        "&yearmm=" + str(year) + month + "&fixtures=false").json()
            for item in matches_data['content']['matches']:
                matches_list.append(item)
        if not os.path.exists('data/' + str(year) + '/' + str(team_dict[team_id])):
            os.makedirs('data/' + str(year) + '/' + str(team_dict[team_id]))
        with open('data/' + str(year) + '/' + str(team_dict[team_id]) + '/matches.json', 'w+') as fout:
            json.dump(matches_list, fout)
        print("Done - Year : ",str(year),", Team : ",str(team_dict[team_id]))
        #     # print(json.dumps(matches_data.json(), indent=2))
