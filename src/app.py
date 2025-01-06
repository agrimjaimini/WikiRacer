import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, session, request
import db
from flask_socketio import SocketIO, disconnect
from wikiracer import a_star_search, check_link
import uuid

# Initialize database and Flask app
DB = db.DatabaseDriver()
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong, random string
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# Generate a unique session ID for each session
@app.before_request
def handle_session():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

# Route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Handle search requests
@socketio.on('start_search')
def handle_search(data):
    session_id = session.get('session_id')
    start_page = data['start']
    end_page = data['end']


    # Check if the path is already in the database
    result = DB.get_path(start_page, end_page)
    if result is None:
        # Start A* search in the background, passing the session ID
        socketio.start_background_task(a_star_search, start_page, end_page, socketio, request.sid)
    else:
        # Emit the existing search result to the specific session
        socketio.emit('search_exists', {
            'path': result['path'],
            'links': result['links'],
            'timestamp': result['timestamp']
        }, to=request.sid)

# Handle link validity checks
@socketio.on('link_check')
def link_validity(data):
    title = data['title']
    # Emit link validity result back to the specific session
    socketio.emit('link_check_response', {
        'id': data['id'], 
        'exists': check_link(title)
    }, to=request.sid)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
