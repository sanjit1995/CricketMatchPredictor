import json
import pandas as pd

team_dict = {1: 'England', 2: 'Australia', 3: 'South-Africa', 4: 'West-Indies', 5: 'New-Zealand',
             6: 'India', 7: 'Pakistan', 8: 'Sri-Lanka', 25: 'Bangladesh'}

second_innings_data = pd.DataFrame(columns=['uid','odi_type','team','opposition','toss_won','bat_second_win_prob','is_home',
            'balls_total','stadium_id','runs','target','req_balls_per_wicket','current_balls_per_wicket','req_runs_per_wicket',
            'current_runs_per_wicket','req_run_rate','current_run_rate','year','all_out_flag',
            'target_deviation_from_avg_inning_1','target_deviation_from_avg_inning_2','win_percentage'])

with open('data/grounds_data.json', 'r') as gdin:
    grounds_data = pd.read_json(gdin)

for year in range(2000, 2020):
    with open('data/' + str(year) + '_all_matches.json', 'r') as fin:
        yearly_matches_data = json.load(fin)
    for match_data in yearly_matches_data:
        if match_data['match_tied'] == 1:
            continue
        uid = match_data['uid']
        odi_type = match_data['odi_type']
        team_id = match_data['inning_2_team_id']
        team = team_dict[team_id]
        opposition = team_dict[match_data['inning_1_team_id']]
        if team_dict[team_id] == match_data['toss_winner_id']:
            toss_won = 1
        else:
            toss_won = 0
        stadium_id = match_data['stadium_id']
        won_bowl_first = grounds_data.loc[grounds_data['stadium_id'] == stadium_id, 'won_bowl_first'].iloc[0]
        matches_played = grounds_data.loc[grounds_data['stadium_id'] == stadium_id, 'matches_played'].iloc[0]
        bat_second_win_prob = won_bowl_first / matches_played
        if team_id == match_data['stadium_country_id']:
            is_home = 1
        else:
            is_home = 0
        balls_total = match_data['inning_2_balls_played']
        runs = match_data['inning_2_runs']
        req_balls_per_wicket = match_data['inning_1_balls_played'] / (match_data['inning_1_wickets'] + 1)
        current_balls_per_wicket = balls_total / (match_data['inning_2_wickets'] + 1)
        req_runs_per_wicket = match_data['inning_1_runs'] / (match_data['inning_2_wickets'] + 1)
        current_runs_per_wicket = runs / (match_data['inning_2_wickets'] + 1)
        req_run_rate = (match_data['inning_1_runs'] / match_data['inning_1_balls_played']) * 6
        current_run_rate = (runs / balls_total) * 6
        all_out_flag = 1 if match_data['inning_2_wickets'] == 10 else 0
        target = match_data['inning_1_runs']
        avg_ground_score_innings_1 = grounds_data.loc[grounds_data['stadium_id'] == stadium_id, 'avg_inns1_score'].iloc[0]
        avg_ground_score_innings_2 = grounds_data.loc[grounds_data['stadium_id'] == stadium_id, 'avg_inns2_score'].iloc[0]
        target_deviation_from_avg_inning_1 = target - avg_ground_score_innings_1
        target_deviation_from_avg_inning_2 = target - avg_ground_score_innings_2
        if team_id == match_data['winner_id']:
            win_percentage = 1
        else:
            win_percentage = 0
        second_innings_data = second_innings_data.append({'uid': uid, 'odi_type': odi_type, 'team': team, 'opposition':opposition,
                        'toss_won': toss_won,'bat_second_win_prob': bat_second_win_prob,'is_home': is_home, 'balls_total': balls_total,
                        'stadium_id': stadium_id, 'runs': runs, 'target': target, 'req_balls_per_wicket': req_balls_per_wicket,
                        'current_balls_per_wicket': current_balls_per_wicket,'req_runs_per_wicket': req_runs_per_wicket,
                        'current_runs_per_wicket': current_runs_per_wicket,'req_run_rate': req_run_rate,
                        'current_run_rate':current_run_rate, 'year': year,'all_out_flag': all_out_flag,
                        'target_deviation_from_avg_inning_1': target_deviation_from_avg_inning_1,
                        'target_deviation_from_avg_inning_2': target_deviation_from_avg_inning_2,'win_percentage': win_percentage},
                        ignore_index=True)
    print("Done - Year : ", str(year))
second_innings_data.to_csv("data/second_innings_data.csv")
