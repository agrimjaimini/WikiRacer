from flask import Flask, render_template
import db
from flask_socketio import SocketIO
from wikiracer import a_star_search
import json


DB = db.DatabaseDriver() 
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


def run_search(start_page, end_page):
    a_star_search(start_page, end_page)

@app.route('/')
def index():
    return render_template('index.html') 

@socketio.on('start_search')
def handle_search(data):
    start_page = data['start']
    end_page = data['end']

    result = DB.get_path(start_page, end_page)
    if result is None:
        socketio.start_background_task(a_star_search, start_page, end_page, socketio)
    else:
        socketio.emit('search_exists', {'path': json.loads(result['path']), 'links' : result['links'], 'timestamp' : result['timestamp'] })
    

if __name__ == '__main__':
    pass