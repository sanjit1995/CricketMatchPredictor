from fastapi import FastAPI
import requests
import json
import pickle
import pandas as pd

team_dict = {1: 'England', 2: 'Australia', 3: 'South-Africa', 4: 'West-Indies', 5: 'New-Zealand',
             6: 'India', 7: 'Pakistan', 8: 'Sri-Lanka', 25: 'Bangladesh'}

stadium_data = pd.read_json("data/grounds_data.json")
print(stadium_data.columns)
print(stadium_data.loc[stadium_data['stadium_id'] == 2524, 'won_bat_first'].iloc[0])
exit(0)
odi_matches = []
invalidTeam = False
first_innings_started = False
second_innings_started = False
for match in matches_data:
    if match['isCancelled']:
        continue
    if 'internationalClassId' not in match or not match['internationalClassId']:
        continue
    if match['format'] == "TEST":
        odi_matches.append(match)
    for team in match['teams']:
        if team['team']['id'] not in team_dict.keys():
            invalidTeam = True
if not odi_matches and not invalidTeam:
    pass
with open('models/first_innings_predictor.pkl', 'rb') as ff:
    first_innings_model = pickle.load(ff)
with open('models/second_innings_predictor.pkl', 'rb') as fs:
    second_innings_model = pickle.load(fs)
for odi_match in odi_matches:
    model_data = {}
    first_innings_data = {}
    second_innings_data = {}
    match_scorecard = requests.get(r"https://hs-consumer-api.espncricinfo.com/v1/pages/match/details?seriesId=" +
                                   str(odi_match['series']['objectId']) + "&matchId=" + str(
        odi_match['objectId'])).json()
    toss_winner_id = odi_match['tossWinnerTeamId']
    for inning in match_scorecard['scorecard']['innings']:
        if inning['inningNumber'] == 1:
            first_innings_data = inning
            if inning['runs']:
                first_innings_started = True
            else:
                pass
        if inning['inningNumber'] == 2:
            second_innings_data = inning
            if inning['runs']:
                second_innings_started = True
    if second_innings_started:
        pass
    elif first_innings_started:
        if first_innings_data['team']['id'] == odi_match['tossWinnerTeamId']:
            model_data['toss_won'] = 1
        else:
            model_data['toss_won'] = 1

    else:
        pass