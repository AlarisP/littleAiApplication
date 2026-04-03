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

# ID of the system "Town Board" guild — set during setup_demo_data()
system_guild_id: str = ""


def setup_demo_data():
    """Setup some demo data for testing"""
    global system_guild_id

    # System guild for user-posted requests
    town_board = board.create_guild("Town Board", "Open board for all adventurers")
    system_guild_id = town_board.id

    # Named guilds
    hunter_guild = board.create_guild("Hunter's Guild", "A prestigious guild for hunters of all kinds")
    assassin_guild = board.create_guild("Shadow Syndicate", "Elite assassin organization")
    mage_guild = board.create_guild("Arcane Circle", "A guild of powerful mages and scholars")

    demo_requests = [
        BoardRequest(
            title="Slay the Dragon of Mount Fuji",
            description="A legendary fire dragon has taken residence on Mount Fuji. Several villages are at risk. Bring back a scale as proof.",
            request_type=RequestType.ASSASSINATION,
            difficulty=RequestDifficulty.LEGENDARY,
            reward=Reward(gold=5000, experience=2000, description="Dragon slayer's bounty"),
            posted_by=hunter_guild.id,
        ),
        BoardRequest(
            title="Escort Princess Yuki to the Capital",
            description="The princess must reach the capital safely before the new moon. Bandits have been spotted along the Eastern Road.",
            request_type=RequestType.ESCORT,
            difficulty=RequestDifficulty.INTERMEDIATE,
            reward=Reward(gold=800, experience=300, description="Royal escort fee"),
            posted_by=hunter_guild.id,
        ),
        BoardRequest(
            title="Retrieve the Sacred Scroll of Flames",
            description="A powerful scroll was stolen from the Arcane Circle library. It was last seen in the possession of a rogue mage near the Darkwood.",
            request_type=RequestType.RETRIEVAL,
            difficulty=RequestDifficulty.ADVANCED,
            reward=Reward(gold=1500, experience=700, description="Scroll recovery bounty"),
            posted_by=mage_guild.id,
        ),
        BoardRequest(
            title="Gather Moonflower Herbs",
            description="We need 20 bundles of Moonflower herbs from the meadows north of town. They only bloom at night — bring gloves.",
            request_type=RequestType.GATHERING,
            difficulty=RequestDifficulty.BEGINNER,
            reward=Reward(gold=200, experience=80, description="Herbalist payment"),
            posted_by=mage_guild.id,
        ),
        BoardRequest(
            title="Explore the Ruins of Ashenvale",
            description="Ancient ruins have resurfaced near the Ashenvale forest. Map the interior and report any dangers or treasures found.",
            request_type=RequestType.EXPLORATION,
            difficulty=RequestDifficulty.ADVANCED,
            reward=Reward(gold=1200, experience=600, description="Explorer's commission"),
            posted_by=hunter_guild.id,
        ),
        BoardRequest(
            title="Defend Millbrook Village",
            description="A bandit warlord has threatened to raid Millbrook at dawn. The village has no guards — they need able-bodied defenders tonight.",
            request_type=RequestType.DEFENSE,
            difficulty=RequestDifficulty.INTERMEDIATE,
            reward=Reward(gold=600, experience=250, description="Village defense payment"),
            posted_by=town_board.id,
        ),
        BoardRequest(
            title="Assassinate the Corrupt Tax Collector",
            description="Lord Vren has been extorting the poor for years. The people have pooled their savings for this contract. Discreet execution required.",
            request_type=RequestType.ASSASSINATION,
            difficulty=RequestDifficulty.ADVANCED,
            reward=Reward(gold=2000, experience=900, description="People's justice fund"),
            posted_by=assassin_guild.id,
        ),
        BoardRequest(
            title="Track the Missing Merchant",
            description="Merchant Gorou went missing three days ago on the southern trade road. Find him — dead or alive — and retrieve his cargo.",
            request_type=RequestType.RETRIEVAL,
            difficulty=RequestDifficulty.BEGINNER,
            reward=Reward(gold=300, experience=100, description="Family's reward"),
            posted_by=town_board.id,
        ),
        BoardRequest(
            title="Collect Rare Spell Components",
            description="The Circle needs 5 phoenix feathers, 3 vials of basilisk venom, and a handful of starstone dust. Sources are scattered across the region.",
            request_type=RequestType.GATHERING,
            difficulty=RequestDifficulty.INTERMEDIATE,
            reward=Reward(gold=700, experience=350, description="Alchemist's fee"),
            posted_by=mage_guild.id,
        ),
        BoardRequest(
            title="Scout the Demon King's Stronghold",
            description="A full assault is being planned. We need detailed intelligence on the stronghold's layout, guard rotations, and weak points. Do NOT engage.",
            request_type=RequestType.EXPLORATION,
            difficulty=RequestDifficulty.LEGENDARY,
            reward=Reward(gold=3000, experience=1500, description="War council payment"),
            posted_by=assassin_guild.id,
        ),
    ]

    for req in demo_requests:
        board.post_request(req.posted_by, req)


# Run setup at import time so gunicorn picks it up
setup_demo_data()


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


@app.route('/api/system-guild', methods=['GET'])
def get_system_guild():
    """Return the system guild ID for user-posted requests"""
    return jsonify({"success": True, "guild_id": system_guild_id})


@app.route('/api/requests', methods=['POST'])
def post_request():
    """Post a new request"""
    data = request.get_json(silent=True) or {}
    guild_id = data.get('guild_id', system_guild_id)
    result = api.post_request(guild_id, data)
    if result.get('success') and data.get('user_id'):
        req = board.get_request(result['request_id'])
        if req:
            req.posted_by_user = data['user_id']
    return jsonify(result)


@app.route('/api/requests/<request_id>', methods=['DELETE'])
def delete_request(request_id):
    """Delete a request (only by the user who posted it)"""
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id')
    return jsonify(api.delete_request(request_id, user_id))


@app.route('/api/requests/<request_id>/accept', methods=['POST'])
def accept_request(request_id):
    """Accept a request"""
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in"})
    return jsonify(api.accept_request(user_id, request_id))


@app.route('/api/requests/<request_id>/decline', methods=['POST'])
def decline_request(request_id):
    """Decline a request"""
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in"})
    return jsonify(api.decline_request(user_id, request_id))


@app.route('/api/requests/<request_id>/complete', methods=['POST'])
def complete_request(request_id):
    """Complete a request"""
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in"})
    return jsonify(api.complete_request(user_id, request_id))


@app.route('/api/users/login', methods=['POST'])
def login_user():
    """Log in by username"""
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    user = board.get_user_by_username(username)
    if user:
        return jsonify({"success": True, "user_id": user.id, "username": user.username})
    return jsonify({"success": False, "error": "User not found"})


@app.route('/api/users/register', methods=['POST'])
def register_user():
    """Register a new user"""
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    if not username:
        return jsonify({"success": False, "error": "Username is required"})
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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
