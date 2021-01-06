import random
import joblib
import pandas as pd

from core import db
from models import GameModel, DriveModel, SeriesModel, PlayModel
from helpers import random_eight_character_id

model_play_alt = joblib.load('model_play_alt.joblib')
model_pass = joblib.load('model_pass.joblib')
model_rush = joblib.load('model_rush.joblib')
model_kick = joblib.load('model_kick.joblib')
model_punt = joblib.load('model_punt.joblib')
y_play_alt = joblib.load('y_play_alt.joblib')
x_pass = joblib.load('x_pass.joblib')
x_rush = joblib.load('x_rush.joblib')


# from https://stackoverflow.com/a/62085741
def undummify(df, prefix_sep="_"):
    cols2collapse = {
        item.split(prefix_sep)[0]: (prefix_sep in item) for item in df.columns
    }
    series_list = []
    for col, needs_to_collapse in cols2collapse.items():
        if needs_to_collapse:
            undummified = (
                df.filter(like=col)
                .idxmax(axis=1)
                .apply(lambda x: x.split(prefix_sep, maxsplit=1)[1])
                .rename(col)
            )
            series_list.append(undummified)
        else:
            series_list.append(df[col])
    undummified_df = pd.concat(series_list, axis=1)
    return undummified_df

def input_row_for_play_type_model(down, ydstogo, team_name):
    team_keys = ['posteam_ARI', 'posteam_ATL', 'posteam_BAL', 'posteam_BUF',
       'posteam_CAR', 'posteam_CHI', 'posteam_CIN', 'posteam_CLE',
       'posteam_DAL', 'posteam_DEN', 'posteam_DET', 'posteam_GB',
       'posteam_HOU', 'posteam_IND', 'posteam_JAX', 'posteam_KC', 'posteam_LA',
       'posteam_LAC', 'posteam_LV', 'posteam_MIA', 'posteam_MIN', 'posteam_NE',
       'posteam_NO', 'posteam_NYG', 'posteam_NYJ', 'posteam_PHI',
       'posteam_PIT', 'posteam_SEA', 'posteam_SF', 'posteam_TB', 'posteam_TEN',
       'posteam_WAS']
    output_row = [down, ydstogo]
    output_row.extend([1 if item.endswith(team_name) else 0 for item in team_keys])
    return output_row


def play_sim(down, series_ydstogo, team_name, game_id, drive_id, series_id, play_index):
    play_model_input = input_row_for_play_type_model(down, series_ydstogo, team_name)
    play_prediction = model_play_alt.predict([play_model_input])
    df = pd.DataFrame(play_prediction, columns=pd.Series(list(y_play_alt.columns)))

    play_type_result = undummify(df)
    play_call = play_type_result.loc[0].play
    play_passer = play_type_result.loc[0].passer
    play_receiver = play_type_result.loc[0].receiver
    play_rusher = play_type_result.loc[0].rusher
    
    random_running_back_selection = random.random()
    if (random_running_back_selection > 0.8):
        df.loc[0, 'rusher_'+ play_rusher] = -1
        play_rusher = undummify(df).loc[0].rusher
    
    # TODO make this per team, e.g. (# of plays where receiver is Kelce and passer is Mahomes/total # of plays where passer is Mahomes)
    # randomly select WR2
    random_wide_receiver_selection = random.random()
    if (random_wide_receiver_selection > 0.5):
        df.loc[0, 'receiver_' + play_receiver] = -1
        play_receiver = undummify(df).loc[0].receiver
        
    # randomly select WR3
    if (random_wide_receiver_selection > 0.75):
        df.loc[0, 'receiver_' + play_receiver] = -1
        play_receiver = undummify(df).loc[0].receiver
    
    
    # randomly select RB as pass catcher
    if (random_wide_receiver_selection > 0.9):
        play_receiver = play_rusher
    
    multiplier_list = [random.randrange(0, 2)] * 40 + [random.randrange(2, 3)] * 10 + [random.randrange(3, 4)] * 3 + [random.randrange(4, 5)] * 1
    
    yards_gained = 0
    print(play_call, play_passer, play_receiver, play_rusher)
    if play_call == 'type_pass':
        input_pass = [down]
        for col in list(x_pass.columns)[1:]:
            if col == 'passer_' + (play_passer):
                input_pass.append(1)
            elif col == 'receiver_' +(play_receiver):
                input_pass.append(1)
            else:
                input_pass.append(0)
        receiving_yards_gained, catch_drop_probability = model_pass.predict([input_pass])[0]
        rand_value = random.random()
        catch_drop_probability_multiplier = 0 if rand_value <= catch_drop_probability else 1
        total_receiving_yards_gained = round((receiving_yards_gained * catch_drop_probability_multiplier * random.choice(multiplier_list)))
        yards_gained = total_receiving_yards_gained
    elif play_call == 'type_run':
        input_rush = [down]
        for col in list(x_rush.columns)[1:]:
            if col == 'rusher_'+ play_rusher:
                input_rush.append(1)
            else:
                input_rush.append(0)
        rush_yards_gained = random.choice(multiplier_list) * model_rush.predict([input_rush])[0][0]
        yards_gained = rush_yards_gained
    
    new_play_model = PlayModel(id=random_eight_character_id(), game_id=game_id, drive_id=drive_id, series_id=series_id, team_name=team_name, down=down, play_type=play_call, play_index=play_index, passer=play_passer, rusher=play_rusher, receiver=play_receiver, yards_gained=yards_gained) 
    db.session.add(new_play_model)
    db.session.commit()

    return {
        'yards_gained': yards_gained
    }

def series_sim(team_name, starting_pos, series_index, game_id, drive_id):
    series_yard_line = starting_pos
    series_time_taken = 0
    series_ydstogo = 10
    play_index = 0
    series_id = random_eight_character_id()
    new_series_model = SeriesModel(id=series_id, game_id=game_id, drive_id=drive_id, series_index=series_index, team_name=team_name)
    db.session.add(new_series_model)
    db.session.commit()

    for down in range(1,5):
        play_result = play_sim(down, series_ydstogo, team_name, game_id, drive_id, series_id, play_index)
        play_yards_gained = play_result['yards_gained']
        series_time_taken = random.randint(30, 90)
        series_yard_line += round(play_yards_gained)
        series_ydstogo = 10 - round(play_yards_gained)
        play_index = play_index + 1
        if series_yard_line >= starting_pos + 10:
            break
    series_result = '' 
    if series_yard_line >= 100:
        series_result = 'touchdown'
    elif series_yard_line >= starting_pos + 10:
        series_result = 'first_down'
    else:
        series_result = 'turnover'    
    new_series_model.series_end_line = series_yard_line
    new_series_model.series_result = series_result
    new_series_model.series_time_taken_sec = series_time_taken
    db.session.commit()

    return {
        'series_end_line': series_yard_line,
        'series_result': series_result, 
        'series_time_taken_sec': series_time_taken
    }  

def drive_sim(team_name, starting_pos, game_id, drive_index):
    #continue_drive = true
    drive_yard_line = starting_pos
    drive_total_time_sec = 0
    series_index = 0
    drive_id = random_eight_character_id()
    new_drive_model = DriveModel(id=drive_id, game_id=game_id, team_name=team_name, drive_index=drive_index)
    db.session.add(new_drive_model)
    db.session.commit()

    while True:
        result_current_series = series_sim(team_name, drive_yard_line, series_index, game_id, drive_id)
        drive_yard_line = result_current_series['series_end_line']
        drive_total_time_sec += result_current_series['series_time_taken_sec']
        series_index = series_index + 1
        if drive_yard_line >= 100 or result_current_series['series_result'] == 'turnover':
            break
    drive_result = 'touchdown' if drive_yard_line >= 100 else 'turnover'
    points_gained = 7 if drive_yard_line >= 100 else 0

    new_drive_model.drive_result = drive_result
    new_drive_model.points_gained = points_gained
    new_drive_model.drive_total_time_sec = drive_total_time_sec
    db.session.commit()

    return {
        'drive_result': drive_result,
        'points_gained': points_gained,
        'drive_total_time_sec': drive_total_time_sec,
        'drive_end_line': None if drive_result == 'touchdown' else drive_yard_line  
    }

def game_sim(game_id):
    game = GameModel.query.filter_by(id=game_id).first()
    home_team = game.home_team
    away_team = game.away_team
    print(home_team, away_team)
    starting_field_position = 25
    home_team_points = 0
    away_team_points = 0
    total_game_time_sec = 0
    pos_team = home_team
    drive_index = 0
    while total_game_time_sec <= 60*60:
        drive_simulation = drive_sim(pos_team, starting_field_position, game.id, drive_index)
        print(pos_team, drive_simulation)
        if pos_team == home_team:
            home_team_points += drive_simulation['points_gained']
            pos_team = away_team
        else:
            away_team_points += drive_simulation['points_gained']
            pos_team = home_team
        starting_field_position = 25 if drive_simulation['drive_end_line'] is None else (100 - drive_simulation['drive_end_line'])
        game.home_team_score = home_team_points
        game.away_team_score = away_team_points
        db.session.commit()

        total_game_time_sec += drive_simulation['drive_total_time_sec']
        drive_index = drive_index + 1
    
    winning_team = home_team if home_team_points > away_team_points else away_team
    game.winning_team = winning_team
    game.game_status = 'complete'
    db.session.commit()

    return {
        'game_id': game.id,
        'home_team_points': home_team_points,
        'away_team_points': away_team_points,
        'winning_team': winning_team
    }   

if  __name__ == "__main__":
    game_sim('KC', 'GB')   
    

