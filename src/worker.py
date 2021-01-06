from rq import Connection, Queue, Worker
from core import app, conn

listen = ['high', 'default', 'low']

if __name__ == '__main__':
	with app.app_context():
	    with Connection(conn):
	        worker = Worker(map(Queue, listen))
	        worker.work()