from flask import Flask, request, render_template

from game_sim import game_sim
from models import db
from reconstruct_game import get_game_information

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost:5432/nfl-pbp'

db.init_app(app)

@app.route('/create', methods=['POST'])
def create_game():
	data = request.get_json()
	return game_sim(data['home_team'], data['away_team'])

@app.route('/game/<game_id>', methods=['GET'])
def get_game(game_id):
	game_data = get_game_information(game_id)
	print(game_data)
	return render_template('game_view.html', game=game_data['game_results'])
	#return get_game_information(game_id)
