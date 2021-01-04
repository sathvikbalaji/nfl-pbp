from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class GameModel(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.String(), primary_key=True)
    home_team = db.Column(db.String())
    away_team = db.Column(db.String())
    game_status = db.Column(db.String())
    winning_team = db.Column(db.String())
    home_team_score = db.Column(db.Integer, nullable=False)
    away_team_score = db.Column(db.Integer, nullable=False)
    
    drive = db.relationship('DriveModel')
    series = db.relationship('SeriesModel')
    plays = db.relationship('PlayModel')

    def __init__(self, id, home_team, away_team, game_status, home_team_score=0, away_team_score=0, winning_team=None):
        self.id = id
        self.home_team = home_team	
        self.away_team = away_team
        self.game_status = game_status
        self.winning_team = winning_team
        self.home_team_score = home_team_score
        self.away_team_score = away_team_score

    def get_description(self):
        desc = ''
        if (self.game_status == 'pending'):
            desc = desc + 'Game in progress. '
            if (self.home_team_score > self.away_team_score):
                desc = desc + f'{self.home_team} is winning against {self.away_team}, {self.home_team_score} to {self.away_team_score}.'
            else:
                desc = desc + f'{self.away_team} is winning against {self.home_team}, {self.away_team_score} to {self.home_team_score}.'
        else:
            desc = desc + 'Game complete. '
            if (self.home_team_score > self.away_team_score):
                desc = desc + f'{self.home_team} beat {self.away_team}, {self.home_team_score} to {self.away_team_score}.'
            else:
                desc = desc + f'{self.away_team} beat {self.home_team}, {self.away_team_score} to {self.home_team_score}.'
        return desc

    def toJSON(self):
        return {
            'type': 'game',
            'id': self.id,
            'home_team': self.home_team,
            'away_team': self.away_team,
            'game_status': self.game_status,
            'winning_team': self.winning_team,
            'home_team_score': self.home_team_score,
            'away_team_score': self.away_team_score,
            'desc': self.get_description()
        }

class DriveModel(db.Model):
    __tablename__ = 'drives'

    id = db.Column(db.String(), primary_key=True)
    game_id = db.Column(db.String(), db.ForeignKey('games.id'))
    drive_index = db.Column(db.Integer(), nullable=False)
    team_name = db.Column(db.String(), nullable=False)
    drive_result = db.Column(db.String())
    points_gained = db.Column(db.Integer())
    drive_total_time_sec = db.Column(db.Integer())

    series = db.relationship('SeriesModel')
    plays = db.relationship('PlayModel')


    def __init__(self, id, game_id, drive_index, team_name, drive_result=None, points_gained=None, drive_total_time_sec=None):
        self.id = id
        self.game_id = game_id
        self.team_name = team_name
        self.drive_result = drive_result
        self.points_gained = points_gained
        self.drive_total_time_sec = drive_total_time_sec
        self.drive_index = drive_index

    def get_description(self):
        return f'Drive complete for {self.team_name}. The drive ended in a {self.drive_result} and took {self.drive_total_time_sec} seconds. '

    def toJSON(self):
        return {
            'type': 'drive',
            'id': self.id,
            'game_id': self.game_id,
            'team_name': self.team_name,
            'drive_result': self.drive_result,
            'points_gained': self.points_gained,
            'drive_total_time_sec': self.drive_total_time_sec,
            'drive_index': self.drive_index,
            'desc': self.get_description()
        }

class SeriesModel(db.Model):
    __tablename__ = 'series'

    id = db.Column(db.String(), primary_key=True)
    game_id = db.Column(db.String(), db.ForeignKey('games.id'))
    drive_id = db.Column(db.String(), db.ForeignKey('drives.id'))
    series_index = db.Column(db.Integer(), nullable=False)
    team_name = db.Column(db.String(), nullable=False)
    series_end_line = db.Column(db.String())
    series_result = db.Column(db.String())
    series_time_taken_sec = db.Column(db.Integer)

    plays = db.relationship('PlayModel')


    def __init__(self, id, game_id, drive_id, series_index, team_name, series_end_line=None, series_result=None, series_time_taken_sec=None):
        self.id = id
        self.game_id = game_id
        self.drive_id = drive_id
        self.series_index = series_index
        self.team_name = team_name
        self.series_end_line = series_end_line
        self.series_result = series_result
        self.series_time_taken_sec = series_time_taken_sec

    def get_description(self):
        desc = ''
        series_yard_description = ''
        series_result_formatted = self.series_result.replace('_',' ')

        if self.series_end_line < 50:
            series_yard_description = series_yard_description + self.team_name + ' ' + str(self.series_end_line)
            desc = f'Series complete for {self.team_name}. The series resulted in a {series_result_formatted}, and ended on the {series_yard_description} yard line. '
        elif self.series_end_line >= 100:
            desc = f'Series complete for {self.team_name}. The series resulted in a touchdown.'
        elif self.series_end_line > 50:
            series_yard_description = series_yard_description + 'opposition ' + str(100 - self.series_end_line)
            desc = f'Series complete for {self.team_name}. The series resulted in a {series_result_formatted}, and ended on the {series_yard_description} yard line. '
        return desc

    def toJSON(self):
        return {
            'type':'series',
            'id': self.id,
            'game_id': self.game_id,
            'drive_id': self.drive_id,
            'series_index': self.series_index,
            'team_name': self.team_name,
            'series_end_line': self.series_end_line,
            'series_result': self.series_result,
            'series_time_taken_sec': self.series_time_taken_sec,
            'desc': self.get_description()
        }

down_number_to_description = {
    1: 'first',
    2: 'second',
    3: 'third',
    4: 'fourth'
}

class PlayModel(db.Model):
    __tablename__ = 'plays'

    id = db.Column(db.String(), primary_key=True)
    game_id = db.Column(db.String(), db.ForeignKey('games.id'))
    drive_id = db.Column(db.String(), db.ForeignKey('drives.id'))
    series_id = db.Column(db.String(), db.ForeignKey('series.id'))
    team_name = db.Column(db.String(), nullable=False)
    down = db.Column(db.Integer(), nullable=False)
    play_type = db.Column(db.String(), nullable=False)
    play_index = db.Column(db.Integer(), nullable=False)
    passer = db.Column(db.Integer())
    rusher = db.Column(db.Integer())
    receiver = db.Column(db.Integer())
    kicker = db.Column(db.Integer())
    punter = db.Column(db.Integer())
    yards_gained = db.Column(db.Integer(), nullable=False)

    def __init__(self, id, game_id, drive_id, series_id, team_name, down, play_type, play_index, yards_gained, passer=None, rusher=None, receiver=None, kicker=None, punter=None):
        self.id = id
        self.game_id = game_id
        self.drive_id = drive_id
        self.series_id = series_id
        self.team_name = team_name
        self.down = down
        self.play_type = play_type
        self.play_index = play_index
        self.passer = passer
        self.rusher = rusher
        self.receiver = receiver
        self.kicker = kicker
        self.punter = punter
        self.yards_gained = yards_gained

    def get_description(self):
        desc = ''
        down_description = down_number_to_description[self.down]
        if self.play_type == 'type_pass':
            if self.yards_gained > 0:
                desc = f'On {down_description} down, {self.passer} pass complete to {self.receiver} for {self.yards_gained} yards. '
            else:
                desc = f'On {down_description} down, {self.passer} pass incomplete to {self.receiver}. '
        elif self.play_type == 'type_run':
            if self.yards_gained > 0:
                desc = f'On {down_description} down, {self.rusher} rushes for {self.yards_gained} yards. '
            else:
                desc = f'On {down_description} down, {self.rusher} rushes for no gain. '
        return desc

    def toJSON(self):
        return {
            'type': 'play',
            'id': self.id,
            'game_id': self.game_id,
            'drive_id': self.drive_id,
            'series_id': self.series_id,
            'team_name': self.team_name,
            'down': self.down,
            'play_type': self.play_type,
            'play_index': self.play_index,
            'passer': self.passer,
            'rusher': self.rusher,
            'receiver': self.receiver,
            'kicker': self.kicker,
            'punter': self.punter,
            'yards_gained': self.yards_gained,
            'desc': self.get_description()
        }


