"""
Anime Guild Request Board Web Application

Flask web app for the request board system.
"""

from flask import Flask, render_template, request, jsonify, session
from request_board import (
    RequestBoard, RequestBoardAPI, RequestType, RequestDifficulty,
    User, Guild, Request as BoardRequest, Reward
)
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize the board and API
board = RequestBoard()
api = RequestBoardAPI(board)

# Demo data setup
def setup_demo_data():
    """Setup some demo data for testing"""
    # Create guilds
    hunter_guild = board.create_guild("Hunter's Guild", "A prestigious guild for hunters of all kinds")
    assassin_guild = board.create_guild("Shadow Syndicate", "Elite assassin organization")
    
    # Create users
    user1 = board.register_user("Tanjiro")
    user2 = board.register_user("Naruto")
    user3 = board.register_user("Ichigo")
    
    # Create some requests
    reward1 = Reward(gold=1000, experience=500, description="Reward for defeating the demon")
    request1 = BoardRequest(
        title="Defeat the Mountain Demon",
        description="A powerful demon has been terrorizing the mountain village. Eliminate it.",
        request_type=RequestType.ASSASSINATION,
        difficulty=RequestDifficulty.ADVANCED,
        reward=reward1,
        posted_by=hunter_guild.id,
    )
    board.post_request(hunter_guild.id, request1)
    
    reward2 = Reward(gold=500, experience=200, description="Reward for escort mission")
    request2 = BoardRequest(
        title="Escort the Merchant",
        description="A merchant needs protection traveling through dangerous territory.",
        request_type=RequestType.ESCORT,
        difficulty=RequestDifficulty.INTERMEDIATE,
        reward=reward2,
        posted_by=hunter_guild.id,
    )
    board.post_request(hunter_guild.id, request2)


# Routes

@app.route('/')
def index():
    """Homepage"""
    requests = board.get_open_requests()
    return render_template('index.html', requests=requests)


@app.route('/api/requests', methods=['GET'])
def get_requests():
    """Get all requests - can filter by type, difficulty, status"""
    request_type = request.args.get('type')
    difficulty = request.args.get('difficulty')
    
    requests_list = board.get_all_requests()
    
    if request_type:
        requests_list = [r for r in requests_list if r.request_type.value == request_type]
    
    if difficulty:
        requests_list = [r for r in requests_list if r.difficulty.value == difficulty]
    
    return jsonify({
        "success": True,
        "requests": [r.to_dict() for r in requests_list],
        "count": len(requests_list),
    })


@app.route('/api/requests/<request_id>', methods=['GET'])
def get_request(request_id):
    """Get a specific request"""
    return jsonify(api.get_request_by_id(request_id))


@app.route('/api/requests', methods=['POST'])
def post_request():
    """Post a new request"""
    data = request.get_json()
    guild_id = data.get('guild_id')
    return jsonify(api.post_request(guild_id, data))


@app.route('/api/requests/<request_id>/accept', methods=['POST'])
def accept_request(request_id):
    """Accept a request"""
    data = request.get_json()
    user_id = data.get('user_id')
    return jsonify(api.accept_request(user_id, request_id))


@app.route('/api/requests/<request_id>/decline', methods=['POST'])
def decline_request(request_id):
    """Decline a request"""
    data = request.get_json()
    user_id = data.get('user_id')
    return jsonify(api.decline_request(user_id, request_id))


@app.route('/api/requests/<request_id>/complete', methods=['POST'])
def complete_request(request_id):
    """Complete a request"""
    data = request.get_json()
    user_id = data.get('user_id')
    return jsonify(api.complete_request(user_id, request_id))


@app.route('/api/users/register', methods=['POST'])
def register_user():
    """Register a new user"""
    data = request.get_json()
    username = data.get('username')
    return jsonify(api.register_user(username))


@app.route('/api/users/<user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    """Get user profile"""
    return jsonify(api.get_user_profile(user_id))


@app.route('/api/users/<user_id>/requests', methods=['GET'])
def get_user_requests(user_id):
    """Get user's requests (active and completed)"""
    return jsonify(api.get_user_requests(user_id))


@app.route('/api/guilds', methods=['POST'])
def create_guild():
    """Create a new guild"""
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    return jsonify(api.create_guild(name, description))


@app.route('/api/guilds/<guild_id>', methods=['GET'])
def get_guild(guild_id):
    """Get guild information"""
    return jsonify(api.get_guild(guild_id))


@app.route('/api/guilds/<guild_id>/requests', methods=['GET'])
def get_guild_requests(guild_id):
    """Get all requests from a guild"""
    return jsonify(api.get_guild_requests(guild_id))


@app.route('/api/save', methods=['POST'])
def save_board():
    """Save board state"""
    filepath = "board_state.json"
    if board.save_state(filepath):
        return jsonify({"success": True, "message": f"Board saved to {filepath}"})
    return jsonify({"success": False, "error": "Failed to save board"})


@app.route('/api/load', methods=['POST'])
def load_board():
    """Load board state"""
    filepath = "board_state.json"
    if board.load_state(filepath):
        return jsonify({"success": True, "message": f"Board loaded from {filepath}"})
    return jsonify({"success": False, "error": "Failed to load board"})


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({"success": False, "error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({"success": False, "error": "Internal server error"}), 500


if __name__ == '__main__':
    setup_demo_data()
    # use_reloader=False prevents watchdog from constantly detecting changes in .venv
    app.run(debug=True, port=5000, use_reloader=False)
