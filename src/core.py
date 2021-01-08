from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import redis
from rq import Queue

pg_url = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/nfl-pbp')
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

# Flask setup
app = Flask(__name__)

# PG Setup
app.config['SQLALCHEMY_DATABASE_URI'] = pg_url
db = SQLAlchemy(app)
#db.init_app(app)

# rq setup
conn = redis.from_url(redis_url)
q = Queue(connection=conn)
