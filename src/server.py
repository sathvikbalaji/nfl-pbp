from flask import request, render_template

from core import app, db, q
from game_sim import game_sim
from helpers import random_eight_character_id
from models import db, GameModel
from reconstruct_game import get_game_information

@app.route('/create', methods=['POST'])
def create_game():
	data = request.get_json()
	new_game_model = GameModel(id=random_eight_character_id(), home_team=data['home_team'], away_team=data['away_team'], game_status='pending')
	db.session.add(new_game_model)
	db.session.commit()
	# return game_sim(data['home_team'], data['away_team'])'
	result = q.enqueue(game_sim, new_game_model.id)
	print(result)
	return {
		'game_id': new_game_model.id
	}

@app.route('/game/<game_id>', methods=['GET'])
def get_game(game_id):
	game_data = get_game_information(game_id)
	return render_template('game_view.html', game=game_data['game_results'])
	#return get_game_information(game_id)
