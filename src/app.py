import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, session
import db
from flask_socketio import SocketIO, disconnect
from wikiracer import a_star_search, check_link
import json

DB = db.DatabaseDriver() 
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

def run_search(start_page, end_page):
    # This function should call a_star_search and handle its result, emitting a socket event
    path, links, timestamp = a_star_search(start_page, end_page, socketio)  # Assuming this returns these values
    socketio.emit('search_result', {
        'path': json.dumps(path),
        'links': links,
        'timestamp': timestamp
    })

@app.route('/')
def index():
    return render_template('index.html') 

@socketio.on('start_search')
def handle_search(data):
    start_page = data['start']
    end_page = data['end']

    # Check if the path already exists in the database
    result = DB.get_path(start_page, end_page)
    if result is None:
        # If not in DB, run the search in the background
        socketio.start_background_task(run_search, start_page, end_page)
    else:
        # Emit the existing result if already in DB
        socketio.emit('search_exists', {
            'path': result['path'],
            'links': result['links'],
            'timestamp': result['timestamp']
        })

@socketio.on('link_check')
def link_validity(data):
    title = data['title']
    socketio.emit('link_check_response', {'id' : data[id], 'exists' : check_link(title)})


@socketio.on('disconnect')
def handle_disconnect():
    session.clear()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
