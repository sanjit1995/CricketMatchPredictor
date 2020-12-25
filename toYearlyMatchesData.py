import json
import psycopg2
import pandas as pd
import requests

team_dict = {1: 'England', 2: 'Australia', 3: 'South-Africa', 4: 'West-Indies', 5: 'New-Zealand',
             6: 'India', 7: 'Pakistan', 8: 'Sri-Lanka', 25: 'Bangladesh'}

conn = psycopg2.connect(
    host="localhost",
    database="cricket_data",
    user="postgres",
    password="Sonu#1105")

# cur = conn.cursor()
# cur.execute("select * from teams")
# all_teams = cur.fetchall()

done_uids = []

for year in range(2002, 2003):
    matches_list = []
    for team in team_dict.values():
        with open('data/' + str(year) + '/' + team + '/matches.json', 'r') as fin:
            matches_data = json.load(fin)
        for match in matches_data:
            matches = {}
            invalidTeam = False
            if match['format'] != 'ODI':
                continue
            teams = match['teams']
            for match_team in teams:
                if match_team['team']['id'] not in team_dict.keys():
                    invalidTeam = True
            if invalidTeam:
                continue
            if match['isCancelled']:
                continue
            if match['resultStatus'] > 3:
                continue
            if match['_uid'] in done_uids:
                continue
            if 'internationalClassId' not in match or not match['internationalClassId']:
                continue

            done_uids.append(match['_uid'])

            # Save data for Db insertion
            matches['uid'] = match['_uid']
            matches['odi_type'] = match['floodlit']
            if match['winnerTeamId']:
                matches['winner_id'] = match['winnerTeamId']
                matches['winner_team'] = team_dict[match['winnerTeamId']]
            else:
                matches['winner_id'] = None
            matches['status'] = match['statusText']
            if match['tossWinnerTeamId']:
                matches['toss_winner_id'] = team_dict[match['tossWinnerTeamId']]
            else:
                matches['toss_winner_id'] = None
            matches['toss_choice'] = 'bat' if match['tossWinnerChoice'] == 1 else 'bowl'
            matches['match_tied'] = 1 if match['resultStatus'] == 3 else 0
            matches['series_name'] = match['series']['name']
            if match['series']['objectId']:
                matches['series_id'] = match['series']['objectId']
            else:
                matches['series_id'] = None
            if match['objectId']:
                matches['match_id'] = match['objectId']
            else:
                matches['match_id'] = None
            matches['match_date'] = str(pd.to_datetime(match['startTime']))
            matches['stadium_id'] = match['ground']['id']
            matches['stadium_obj_id'] = match['ground']['objectId']
            matches['stadium_name'] = match['ground']['name']
            matches['stadium_place_id'] = match['ground']['town']['id']
            matches['stadium_place'] = match['ground']['town']['name']
            matches['stadium_country_id'] = match['ground']['country']['id']
            for match_team in teams:
                inn_num = match_team['inningNumbers'][0]
                if inn_num == 1:
                    matches['inning_1_team_id'] = match_team['team']['id']
                    matches['inning_1_team_score'] = match_team['score']
                    if 'scoreInfo' in match_team and match_team['scoreInfo']:
                        matches['inning_1_team_score_info'] = match_team['scoreInfo']
                    else:
                        matches['inning_1_team_score_info'] = None
                else:
                    matches['inning_2_team_id'] = match_team['team']['id']
                    matches['inning_2_team_score'] = match_team['score']
                    if 'scoreInfo' in match_team and match_team['scoreInfo']:
                        matches['inning_2_team_score_info'] = match_team['scoreInfo']
                    else:
                        matches['inning_2_team_score_info'] = None
            if matches['series_id'] and matches['match_id']:
                match_details = requests.get(r"https://hs-consumer-api.espncricinfo.com/v1/pages/match/details?seriesId=" +
                    str(matches['series_id']) + "&matchId=" + str(matches['match_id'])).json()
                if 'scorecard' not in match_details:
                    print("https://hs-consumer-api.espncricinfo.com/v1/pages/match/details?seriesId=" +
                            str(matches['series_id']) + "&matchId=" + str(matches['match_id']))
                    matches['inning_1_team'] = team_dict[matches['inning_1_team_id']]
                    matches['inning_1_runs'] = None
                    matches['inning_1_wickets'] = None
                    matches['inning_1_overs_played'] = None
                    matches['inning_1_balls_played'] = None
                    matches['inning_2_team'] = team_dict[matches['inning_2_team_id']]
                    matches['inning_2_runs'] = None
                    matches['inning_2_wickets'] = None
                    matches['inning_2_overs_played'] = None
                    matches['inning_2_balls_played'] = None
                else:
                    innings = match_details['scorecard']['innings']
                    for inning in innings:
                        if inning['inningNumber'] == 1:
                            matches['inning_1_team'] = team_dict[inning['team']['id']]
                            matches['inning_1_runs'] = inning['runs']
                            matches['inning_1_wickets'] = inning['wickets']
                            matches['inning_1_overs_played'] = inning['overs']
                            matches['inning_1_balls_played'] = inning['balls']
                        else:
                            matches['inning_2_team'] = team_dict[inning['team']['id']]
                            matches['inning_2_runs'] = inning['runs']
                            matches['inning_2_wickets'] = inning['wickets']
                            matches['inning_2_overs_played'] = inning['overs']
                            matches['inning_2_balls_played'] = inning['balls']
            matches_list.append(matches)
            print("Done : ", len(matches_list))
    with open('data/' + str(year) + '_all_matches.json', 'w+') as fout:
        json.dump(matches_list, fout)
    print("Done - Year : ", str(year), ', Total Matches : ', len(matches_list))
