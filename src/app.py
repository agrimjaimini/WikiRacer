import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, session, request
import db
from flask_socketio import SocketIO, disconnect
from wikiracer import a_star_search, check_link
import uuid

DB = db.DatabaseDriver()
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

@app.before_request
def handle_session():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_search')
def handle_search(data):
    session_id = session.get('session_id')
    start_page = data['start']
    end_page = data['end']

    result = DB.get_path(start_page, end_page)
    if result is None:
        socketio.start_background_task(a_star_search, start_page, end_page, socketio, request.sid)
    else:
        socketio.emit('search_exists', {
            'path': result['path'],
            'links': result['links'],
            'timestamp': result['timestamp']
        }, to=request.sid)

@socketio.on('link_check')
def link_validity(data):
    title = data['title']
    socketio.emit('link_check_response', {
        'id': data['id'], 
        'exists': check_link(title)
    }, to=request.sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
