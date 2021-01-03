import json
import math
from fastapi import FastAPI
from fastapi import requests
import requests
import pickle
import datetime
import pandas as pd

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

team_dict = {1: 'ENG', 2: 'AUS', 3: 'RSA', 4: 'WI', 5: 'NZ', 6: 'IND', 7: 'PAK', 8: 'SL', 25: 'BAN'}

long_team_dict = {1: 'England', 2: 'Australia', 3: 'South-Africa', 4: 'West-Indies', 5: 'New-Zealand',
             6: 'India', 7: 'Pakistan', 8: 'Sri-Lanka', 25: 'Bangladesh'}

flag_dict = {1: "https://img1.hscicdn.com/image/upload/f_auto,t_s_100/lsci/db/PICTURES/CMS/313100/313114.logo.png",
             2: "https://img1.hscicdn.com/image/upload/f_auto,t_s_100/lsci/db/PICTURES/CMS/313100/313124.logo.png",
             3: "https://img1.hscicdn.com/image/upload/f_auto,t_s_100/lsci/db/PICTURES/CMS/313100/313125.logo.png",
             4: "https://img1.hscicdn.com/image/upload/f_auto,t_s_100/lsci/db/PICTURES/CMS/313100/313126.logo.png",
             5: "https://img1.hscicdn.com/image/upload/f_auto,t_s_100/lsci/db/PICTURES/CMS/313100/313127.logo.png",
             6: "https://img1.hscicdn.com/image/upload/f_auto,t_s_100/lsci/db/PICTURES/CMS/313100/313128.logo.png",
             7: "https://img1.hscicdn.com/image/upload/f_auto,t_s_100/lsci/db/PICTURES/CMS/313100/313129.logo.png",
             8: "https://img1.hscicdn.com/image/upload/f_auto,t_s_100/lsci/db/PICTURES/CMS/313100/313130.logo.png",
             25: "https://img1.hscicdn.com/image/upload/f_auto,t_s_100/lsci/db/PICTURES/CMS/313100/313145.logo.png"}


@app.get("/getMatchData", tags=["root"])
def getMatchData():
    live_data = requests.get("https://hs-consumer-api.espncricinfo.com/v1/pages/matches/live?").json()
    matches_data = live_data['content']['matches']
    odi_matches = []
    matches_details = []
    invalidTeam = False
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
    if not odi_matches or invalidTeam:
        return {"error_msg": "Sorry !!!! No ongoing Matches", "status": 404}
    for odi_match in odi_matches:
        match_details = {}
        teams_playing = []
        for team in odi_match['teams']:
            if team['team']['id'] in team_dict.keys():
                teams_playing.append(team['team']['id'])
        match_scorecard = requests.get(r"https://hs-consumer-api.espncricinfo.com/v1/pages/match/details?seriesId=" +
                                       str(odi_match['series']['objectId']) + "&matchId=" + str(odi_match['objectId'])).json()
        # print("https://hs-consumer-api.espncricinfo.com/v1/pages/match/details?seriesId=" + str(odi_match['series']['objectId']) + "&matchId=" + str(odi_match['objectId']))
        if odi_match['state'] == "PRE":
            matches_details.append({"error_details": odi_match['title'] + ', ' + odi_match['series']['alternateName'] + ' - ' + odi_match['statusText'], "status" : "pre"})
            continue
        if 'scorecard' not in match_scorecard or 'innings' not in match_scorecard['scorecard']:
            return {"error_msg": "Match not yet started", "status": 404}
        odi_type = "D" if odi_match['floodlit'] == "day" else "D/N"
        date_new = str(
            datetime.datetime.strptime(str(pd.to_datetime(odi_match['startDate']).date()), '%Y-%m-%d').strftime(
                '%b %d, %Y'))
        match_details['venue_details'] = odi_match['title'] + "(" + odi_type + ") - " + odi_match['ground'][
            'name'] + ", " + \
                                         odi_match['ground']['town']['name'] + " (" + odi_match['ground']['country'][
                                             'name'] + ")"
        match_details['date_details'] = date_new
        match_details['tour_details'] = odi_match['series']['longName'] + " - " + \
                                        odi_match['series']['season']
        status = odi_match['status']
        status_text = odi_match['statusText']
        for inning in match_scorecard['scorecard']['innings']:
            if inning['inningNumber'] == 1:
                match_details['team_flag_inning_1'] = flag_dict[inning['team']['id']]
                match_details['team_inning_1'] = team_dict[inning['team']['id']]
                match_details['score_details_inning_1'] = str(inning['runs']) + "/" + str(inning['wickets']) + " (" + \
                                                          str(inning['overs']) + " overs)"
                for team_playing in teams_playing:
                    if team_playing != inning['team']['id']:
                        match_details['team_flag_inning_2'] = flag_dict[team_playing]
                        match_details['team_inning_2'] = team_dict[team_playing]
            elif inning['inningNumber'] == 2:
                match_details['team_flag_inning_2'] = flag_dict[inning['team']['id']]
                match_details['team_inning_2'] = team_dict[inning['team']['id']]
                match_details['score_details_inning_2'] = str(inning['runs']) + "/" + str(inning['wickets']) + " (" + \
                                                          str(inning['overs']) + " overs)"
        match_details['status'] = status
        match_details['status_text'] = status_text
        matches_details.append(match_details)
    return {"matches_details": matches_details, "matches_status": 200}


@app.get("/getPredData", tags=["root"])
def getPredData():
    live_data = requests.get("https://hs-consumer-api.espncricinfo.com/v1/pages/matches/live?").json()
    matches_data = live_data['content']['matches']
    stadium_data = pd.read_json("data/grounds_data.json")
    odi_matches = []
    invalidTeam = False
    first_innings_started = False
    second_innings_started = False
    final_predictions = []
    model_datas = []
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
    if not odi_matches and invalidTeam:
        return {"error_msg": "Sorry !!!! No ongoing Matches", "status": 404}
    with open('models/first_innings_predictor.pkl', 'rb') as ff:
        first_innings_model = pickle.load(ff)
    with open('models/second_innings_predictor.pkl', 'rb') as fs:
        second_innings_model = pickle.load(fs)
    for odi_match in odi_matches:
        pred = {}
        first_innings_data = {}
        second_innings_data = {}
        match_scorecard = requests.get(r"https://hs-consumer-api.espncricinfo.com/v1/pages/match/details?seriesId=" +
                                       str(odi_match['series']['objectId']) + "&matchId=" + str(odi_match['objectId'])).json()
        if odi_match['state'] == "PRE":
            final_predictions.append({"error_msg": "Match not yet started", "status": "pre"})
            continue
        for inning in match_scorecard['scorecard']['innings']:
            if inning['inningNumber'] == 1:
                first_innings_data = inning
                if inning['balls']:
                    first_innings_started = True
                else:
                    pred = {"error_msg": "Match not yet started", "status": 406}
            if inning['inningNumber'] == 2:
                second_innings_data = inning
                if inning['balls']:
                    second_innings_started = True
        #### To fetch 2nd innings data ####
        if second_innings_started:
            model_data = pd.DataFrame(columns=['toss_won', 'bat_second_win_prob', 'is_home', 'balls_total',
                                'all_out_flag', 'target_deviation_from_avg_inning_1',
                                'target_deviation_from_avg_inning_2', 'run_rate_margin',
                                'balls_per_wicket_margin', 'runs_per_wicket_margin', 'odi_type_day',
                                'odi_type_daynight', 'odi_type_night', 'team_Australia',
                                'team_Bangladesh', 'team_England', 'team_India', 'team_New-Zealand',
                                'team_Pakistan', 'team_South-Africa', 'team_Sri-Lanka',
                                'team_West-Indies', 'opposition_Australia', 'opposition_Bangladesh',
                                'opposition_England', 'opposition_India', 'opposition_New-Zealand',
                                'opposition_Pakistan', 'opposition_South-Africa',
                                'opposition_Sri-Lanka', 'opposition_West-Indies',
                                'binned_target_less_than_200', 'binned_target_200_to_250',
                                'binned_target_250_to_300', 'binned_target_more_than_300'])
            if second_innings_data['team']['id'] == odi_match['tossWinnerTeamId']:
                model_data.at[0, 'toss_won'] = 1
            else:
                model_data.at[0, 'toss_won'] = 0
            # print(stadium_data[stadium_data['stadium_id'] == odi_match['ground']['id']]['won_bat_first'])
            # print(stadium_data.loc[stadium_data['stadium_id'] == odi_match['ground']['id'], 'won_bat_first'])
            model_data.at[0, 'bat_second_win_prob'] = stadium_data.loc[stadium_data['stadium_id'] == odi_match['ground']['id'], 'won_bowl_first'].iloc[0] / stadium_data.loc[stadium_data['stadium_id'] == odi_match['ground']['id'], 'matches_played'].iloc[0]
            avg_bat_first_score = stadium_data.loc[stadium_data['stadium_id'] == odi_match['ground']['id'], 'avg_inns1_score'].iloc[0]
            avg_bat_second_score = stadium_data.loc[stadium_data['stadium_id'] == odi_match['ground']['id'], 'avg_inns2_score'].iloc[0]
            if second_innings_data['team']['id'] == odi_match['ground']['country']['id']:
                model_data.at[0, 'is_home'] = 1
            else:
                model_data.at[0, 'is_home'] = 0
            model_data.at[0, 'balls_total'] = 300
            first_innings_run_rate = (first_innings_data['runs'] / 300) * 6
            model_data.at[0, 'run_rate_margin'] = ((second_innings_data['runs'] / second_innings_data['balls']) * 6) - first_innings_run_rate
            first_innings_balls_per_wicket = first_innings_data['balls'] / (first_innings_data['wickets'] + 1)
            model_data.at[0, 'balls_per_wicket_margin'] = (second_innings_data['balls'] / (second_innings_data['wickets'] + 1)) - first_innings_balls_per_wicket
            first_innings_runs_per_wicket = first_innings_data['runs'] / (first_innings_data['wickets'] + 1)
            model_data.at[0, 'runs_per_wicket_margin'] = (second_innings_data['runs'] / (second_innings_data['wickets'] + 1)) - first_innings_runs_per_wicket
            overs_played = str(first_innings_data['overs']).split(".")[0]
            if second_innings_data['wickets'] > 0:
                overs_per_wicket = int(overs_played) / second_innings_data['wickets']
            else:
                overs_per_wicket = 0
            if overs_per_wicket < 5 and overs_per_wicket:
                model_data.at[0, 'all_out_flag'] = 1
            else:
                model_data.at[0, 'all_out_flag'] = 0
            target = first_innings_data['runs']
            model_data.at[0, 'target_deviation_from_avg_inning_1'] = target - avg_bat_first_score
            model_data.at[0, 'target_deviation_from_avg_inning_2'] = target - avg_bat_second_score
            for odi_type in ['day', 'daynight', 'night']:
                if str(odi_match['floodlit']) == odi_type:
                    model_data.at[0, 'odi_type_' + str(odi_type)] = 1
                else:
                    model_data.at[0, 'odi_type_' + str(odi_type)] = 0
            for team in long_team_dict.keys():
                if team == second_innings_data['team']['id']:
                    model_data.at[0, 'team_' + str(long_team_dict[team])] = 1
                else:
                    model_data.at[0, 'team_' + str(long_team_dict[team])] = 0
            opposition_team = odi_match['teams'][0]['team']['id']
            for opp_team in long_team_dict.keys():
                if opp_team == opposition_team:
                    model_data.at[0,'opposition_' + str(long_team_dict[opp_team])] = 1
                else:
                    model_data.at[0,'opposition_' + str(long_team_dict[opp_team])] = 0
            batting_team = team_dict[odi_match['teams'][1]['team']['id']]
            bowling_team = team_dict[odi_match['teams'][0]['team']['id']]
            if 200 > target > 0:
                model_data.at[0, 'binned_target_less_than_200'] = 1
                model_data.at[0, 'binned_target_200_to_250'] = 0
                model_data.at[0, 'binned_target_250_to_300'] = 0
                model_data.at[0, 'binned_target_more_than_300'] = 0
            elif 250 > target > 200:
                model_data.at[0, 'binned_target_less_than_200'] = 0
                model_data.at[0, 'binned_target_200_to_250'] = 1
                model_data.at[0, 'binned_target_250_to_300'] = 0
                model_data.at[0, 'binned_target_more_than_300'] = 0
            elif 300 > target > 250:
                model_data.at[0, 'binned_target_less_than_200'] = 0
                model_data.at[0, 'binned_target_200_to_250'] = 0
                model_data.at[0, 'binned_target_250_to_300'] = 1
                model_data.at[0, 'binned_target_more_than_300'] = 0
            else:
                model_data.at[0, 'binned_target_less_than_200'] = 0
                model_data.at[0, 'binned_target_200_to_250'] = 0
                model_data.at[0, 'binned_target_250_to_300'] = 0
                model_data.at[0, 'binned_target_more_than_300'] = 1

        #### To fetch 1st innings data ####
        elif first_innings_started:
            model_data = pd.DataFrame(columns=['toss_won', 'bat_first_win_prob', 'is_home', 'balls_total', 'run_rate',
                                               'balls_per_wicket', 'runs_per_wicket', 'all_out_flag',
                                               'deviation_from_avg_score', 'odi_type_day', 'odi_type_daynight',
                                               'odi_type_night', 'team_Australia', 'team_Bangladesh', 'team_England',
                                               'team_India', 'team_New-Zealand', 'team_Pakistan', 'team_South-Africa',
                                               'team_Sri-Lanka', 'team_West-Indies', 'opposition_Australia',
                                               'opposition_Bangladesh', 'opposition_England', 'opposition_India',
                                               'opposition_New-Zealand', 'opposition_Pakistan',
                                               'opposition_South-Africa', 'opposition_Sri-Lanka',
                                               'opposition_West-Indies', 'binned_runs_less_than_200',
                                               'binned_runs_200_to_250', 'binned_runs_250_to_300',
                                               'binned_runs_more_than_300'])
            if first_innings_data['team']['id'] == odi_match['tossWinnerTeamId']:
                model_data.at[0,'toss_won'] = 1
            else:
                model_data.at[0,'toss_won'] = 0
            # print(stadium_data[stadium_data['stadium_id'] == odi_match['ground']['id']]['won_bat_first'])
            # print(stadium_data.loc[stadium_data['stadium_id'] == odi_match['ground']['id'], 'won_bat_first'])
            model_data.at[0,'bat_first_win_prob'] = stadium_data.loc[stadium_data['stadium_id'] == odi_match['ground']['id'], 'won_bat_first'].iloc[0] / \
                                               stadium_data.loc[stadium_data['stadium_id'] == odi_match['ground']['id'], 'matches_played'].iloc[0]
            avg_bat_first_score = stadium_data.loc[stadium_data['stadium_id'] == odi_match['ground']['id'], 'avg_inns1_score'].iloc[0]
            if first_innings_data['team']['id'] == odi_match['ground']['country']['id']:
                model_data.at[0,'is_home'] = 1
            else:
                model_data.at[0,'is_home'] = 0
            model_data.at[0,'balls_total'] = 300
            model_data.at[0,'run_rate'] = (first_innings_data['runs'] / 300) * 6
            model_data.at[0,'balls_per_wicket'] = first_innings_data['balls'] / (first_innings_data['wickets'] + 1)
            model_data.at[0,'runs_per_wicket'] = first_innings_data['runs'] / (first_innings_data['wickets'] + 1)
            overs_played = str(first_innings_data['overs']).split(".")[0]
            if first_innings_data['wickets'] > 0:
                overs_per_wicket = int(overs_played) / first_innings_data['wickets']
            else:
                overs_per_wicket = 0
            if 5 > overs_per_wicket > 0:
                model_data.at[0,'all_out_flag'] = 1
            else:
                model_data.at[0,'all_out_flag'] = 0
            estimated_score = (first_innings_data['runs'] / first_innings_data['balls']) * 300
            model_data.at[0,'deviation_from_avg_score'] = estimated_score - avg_bat_first_score
            for odi_type in ['day','daynight','night']:
                if str(odi_match['floodlit']) == odi_type:
                    model_data.at[0,'odi_type_' + str(odi_type)] = 1
                else:
                    model_data.at[0, 'odi_type_' + str(odi_type)] = 0
            for team in long_team_dict.keys():
                if team == first_innings_data['team']['id']:
                    model_data.at[0, 'team_' + str(long_team_dict[team])] = 1
                else:
                    model_data.at[0, 'team_' + str(long_team_dict[team])] = 0
            opposition_team = odi_match['teams'][1]['team']['id']
            for opp_team in long_team_dict.keys():
                if opp_team == opposition_team:
                    model_data.at[0,'opposition_' + str(long_team_dict[opp_team])] = 1
                else:
                    model_data.at[0,'opposition_' + str(long_team_dict[opp_team])] = 0
            batting_team = team_dict[odi_match['teams'][0]['team']['id']]
            bowling_team = team_dict[odi_match['teams'][1]['team']['id']]
            if 200 > estimated_score > 0:
                model_data.at[0, 'binned_runs_less_than_200'] = 1
                model_data.at[0, 'binned_runs_200_to_250'] = 0
                model_data.at[0, 'binned_runs_250_to_300'] = 0
                model_data.at[0, 'binned_runs_more_than_300'] = 0
            elif 250 > estimated_score > 200:
                model_data.at[0, 'binned_runs_less_than_200'] = 0
                model_data.at[0, 'binned_runs_200_to_250'] = 1
                model_data.at[0, 'binned_runs_250_to_300'] = 0
                model_data.at[0, 'binned_runs_more_than_300'] = 0
            elif 300 > estimated_score > 250:
                model_data.at[0, 'binned_runs_less_than_200'] = 0
                model_data.at[0, 'binned_runs_200_to_250'] = 0
                model_data.at[0, 'binned_runs_250_to_300'] = 1
                model_data.at[0, 'binned_runs_more_than_300'] = 0
            else:
                model_data.at[0, 'binned_runs_less_than_200'] = 0
                model_data.at[0, 'binned_runs_200_to_250'] = 0
                model_data.at[0, 'binned_runs_250_to_300'] = 0
                model_data.at[0, 'binned_runs_more_than_300'] = 1
        else:
            pred = {"error_msg": "Match not yet started", "status": 406}
        if model_data.isnull().values.any():
            final_predictions.append(pred)
        else:
            model_datas.append(model_data.to_json())
            if second_innings_started:
                pred['loss'] = math.floor(second_innings_model.predict_proba(model_data)[0][0] * 100)
                pred['win'] = 100 - pred['loss']
                pred['batting_team'] = batting_team
                pred['bowling_team'] = bowling_team
                pred['status'] = "live"
            else:
                pred['loss'] = math.floor(first_innings_model.predict_proba(model_data)[0][0] * 100)
                pred['win'] = 100 - pred['loss']
                pred['batting_team'] = batting_team
                pred['bowling_team'] = bowling_team
                pred['status'] = "live"
            final_predictions.append(pred)
    return {"model_data": model_datas, "pred_details": final_predictions, "pred_status": 200}
