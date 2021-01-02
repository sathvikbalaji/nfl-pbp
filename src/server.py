from flask import Flask, request

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
	return get_game_information(game_id)
