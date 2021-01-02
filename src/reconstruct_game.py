from models import GameModel, DriveModel,SeriesModel, PlayModel

def get_game_information(game_id):
	game_data = [] # append drive, series, and play information to game_data
	game = GameModel.query.filter_by(id=game_id).first()
	print(game)
	drives = DriveModel.query.filter_by(game_id=game_id).all()
	print(drives)
	for drive in drives:
		all_series = SeriesModel.query.filter_by(drive_id=drive.id).all()
		for series in all_series:
			all_plays = PlayModel.query.filter_by(series_id=series.id).all()
			print(all_plays)
			game_data.extend([play.toJSON() for play in all_plays])
			game_data.append(series.toJSON())
		game_data.append(drive.toJSON())
	game_data.append(game.toJSON())
		
	return {
		'game_results': game_data
	}
