from models import GameModel, DriveModel,SeriesModel, PlayModel

def get_game_information(game_id):
	game_data = [] # append drive, series, and play information to game_data
	home_team_score = 0
	away_team_score = 0

	game = GameModel.query.filter_by(id=game_id).first()
	if game is None:
		return None
	home_team = game.home_team
	away_team = game.away_team

	drives = DriveModel.query.filter_by(game_id=game_id).all()

	for drive in drives:
		all_series = SeriesModel.query.filter_by(drive_id=drive.id).all()
		for series in all_series:
			all_plays = PlayModel.query.filter_by(series_id=series.id).all()
			game_data.extend([f'[{home_team} {home_team_score} - {away_team_score} {away_team}] ' +  play.get_description() for play in all_plays])
			game_data.append(f'[{home_team} {home_team_score} - {away_team_score} {away_team}] ' + series.get_description())
		if drive.team_name == home_team:
			home_team_score += (drive.points_gained or 0)
		else:
			away_team_score += (drive.points_gained or 0)
		game_data.append(f'[{home_team} {home_team_score} - {away_team_score} {away_team}] ' + drive.get_description())
	game_data.append(f'[{home_team} {home_team_score} - {away_team_score} {away_team}] ' + game.get_description())
		
	return {
		'game_results': game_data
	}
