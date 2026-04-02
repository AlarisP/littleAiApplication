# Anime Guild Request Board / Assassin Request Board

A web application for managing guild requests, tasks, and rewards in an anime-inspired setting.

## Project Structure

```
littleAiApplication/
├── request_board.pyi          # Type stub file defining the interface
├── request_board.py           # Core implementation of request board system
├── app.py                     # Flask web application
├── requirements.txt           # Python dependencies
├── templates/
│   └── index.html            # Main HTML template
├── static/
│   ├── style.css             # Stylesheet
│   └── script.js             # Client-side JavaScript
└── board_state.json          # Saved board state (generated at runtime)
```

## Features

### Core System (request_board.py)
- **Users**: Create adventurers with levels, experience, and gold
- **Guilds**: Create guilds that post requests
- **Requests**: Post tasks with rewards (currently supporting Assassination, Escort, Retrieval, Exploration, Defense, Gathering)
- **Rewards**: Configure gold and experience rewards
- **Request Status**: Track request lifecycle (Open → In Progress → Completed/Cancelled)
- **Difficulty Levels**: Beginner, Intermediate, Advanced, Legendary

### Web Application (Flask + HTML/CSS/JS)
- Browse available requests
- Filter requests by type and difficulty
- Register new users and persist session via localStorage
- Create guilds
- Accept requests (button changes to **Finish Request** once accepted)
- Decline requests (stays open for others; tracked per user)
- Complete accepted requests and receive gold + XP rewards
- **My Requests** panel: view In Progress, Completed, and Declined requests
- View user profile (level, gold, XP) shown in the header bar
- Save/load board state to JSON

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

The web app will be available at `http://localhost:5000`

## Type Stub File (.pyi)

The `request_board.pyi` file defines the complete interface for the system:
- All class definitions
- Method signatures with type hints
- Return types

**IMPORTANT**: When modifying the core implementation in `request_board.py`, always update the corresponding signatures in `request_board.pyi` to maintain consistency.

## API Endpoints

### Requests
- `GET /api/requests` - Get all requests (query params: `type`, `difficulty`)
- `GET /api/requests/<request_id>` - Get specific request
- `POST /api/requests` - Create new request
  ```json
  {
    "guild_id": "...",
    "title": "...",
    "description": "...",
    "type": "assassination|escort|retrieval|exploration|defense|gathering|other",
    "difficulty": "beginner|intermediate|advanced|legendary",
    "reward_gold": 1000,
    "reward_experience": 500,
    "reward_items": [],
    "reward_description": "..."
  }
  ```
- `POST /api/requests/<request_id>/accept` - Accept request
- `POST /api/requests/<request_id>/decline` - Decline request (request stays open for others)
- `POST /api/requests/<request_id>/complete` - Complete an accepted request

### Users
- `POST /api/users/register` - Register new user
- `GET /api/users/<user_id>/profile` - Get user profile
- `GET /api/users/<user_id>/requests` - Get user's requests (active, completed, declined)

### Guilds
- `POST /api/guilds` - Create guild
- `GET /api/guilds/<guild_id>` - Get guild info
- `GET /api/guilds/<guild_id>/requests` - Get guild's requests

### Persistence
- `POST /api/save` - Save board state to JSON
- `POST /api/load` - Load board state from JSON

## Example Usage

```python
from request_board import (
    RequestBoard, RequestType, RequestDifficulty, Reward, Request
)

# Initialize
board = RequestBoard()

# Create guild
guild = board.create_guild("Hunter's Guild", "A guild of skilled hunters")

# Create user
user = board.register_user("Tanjiro")

# Create reward
reward = Reward(gold=1000, experience=500, description="Defeat the demon")

# Post request
request = Request(
    title="Defeat Mountain Demon",
    description="A powerful demon terrorizing the village",
    request_type=RequestType.ASSASSINATION,
    difficulty=RequestDifficulty.ADVANCED,
    reward=reward,
    posted_by=guild.id
)
board.post_request(guild.id, request)

# Accept request
board.accept_request(user.id, request.id)

# Complete request (awards rewards)
board.complete_request(user.id, request.id)

# Check user progress
user_profile = board.get_user(user.id)
print(f"{user_profile.username} - Level {user_profile.level}, Gold: {user_profile.gold}")
```

## Development Notes

### Adding New Request Types
1. Add to `RequestType` enum in `request_board.py`
2. Update `request_board.pyi` enum definition
3. UI will automatically support the new type

### Adding New Features
1. Implement in `request_board.py`
2. Add type signatures to `request_board.pyi`
3. Add API endpoints in `app.py` if needed
4. Update HTML/CSS/JS for UI if needed

### Testing
Run with demo data by starting the Flask app. Demo data includes:
- 2 guilds (Hunter's Guild, Shadow Syndicate)
- 3 users (Tanjiro, Naruto, Ichigo)
- 2 sample requests

## Future Enhancements

- [ ] Database integration (SQLAlchemy)
- [ ] User authentication and sessions
- [ ] Request comments/chat system
- [ ] Item system with inventory
- [ ] Leaderboards
- [ ] Real-time updates with WebSockets
- [ ] Quest chains and achievements
- [ ] Guild wars/competitions
- [ ] Admin dashboard
- [ ] Mobile-responsive improvements