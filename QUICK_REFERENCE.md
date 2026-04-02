# Quick Reference: Guild Request Board API

## Core Enums

### RequestStatus
- `OPEN` - Request is available to accept
- `IN_PROGRESS` - Request has been accepted
- `COMPLETED` - Request has been completed
- `CANCELLED` - Request has been cancelled

### RequestType
- `ASSASSINATION` - Eliminate a target
- `ESCORT` - Protect someone/something
- `RETRIEVAL` - Obtain an item
- `EXPLORATION` - Explore a location
- `DEFENSE` - Defend a location/person
- `GATHERING` - Collect resources
- `OTHER` - Miscellaneous task

### RequestDifficulty
- `BEGINNER` - Easy, low risk
- `INTERMEDIATE` - Moderate difficulty
- `ADVANCED` - High difficulty, challenging
- `LEGENDARY` - Extremely difficult, rare rewards

## Core Classes

### Reward
```python
reward = Reward(
    gold=1000,
    experience=500,
    items=[{"name": "Demon Blade", "rarity": "Rare"}],
    description="Reward for slaying the demon"
)
```

### Request
```python
request = Request(
    title="Slay the Mountain Demon",
    description="A demon has been terrorizing the nearby village",
    request_type=RequestType.ASSASSINATION,
    difficulty=RequestDifficulty.ADVANCED,
    reward=reward,
    posted_by=guild.id,
    deadline=None  # Optional
)

request.accept(user_id)  # Returns: True/False
request.complete()       # Returns: True/False
request.cancel()         # Returns: True/False
```

### User
```python
user = User(username="Tanjiro", initial_gold=100)

user.accept_request(request_id)      # Add to active requests
user.complete_request(request_id)    # Mark as completed
user.gain_gold(500)                  # Add gold
user.gain_experience(100)            # Add XP (auto level-up at 100)
user.join_guild(guild_id)            # Join a guild
```

### Guild
```python
guild = Guild(
    name="Hunter's Guild",
    description="Elite hunters",
    initial_funds=5000
)

guild.add_member(user_id)
guild.remove_member(user_id)
guild.post_request(request)  # Requires: request_type == this guild's posts
guild.fund_update(1000)      # Add/subtract funds (negative to spend)
```

### RequestBoard (Main Controller)
```python
board = RequestBoard()

# Request Operations
board.post_request(guild_id, request)
board.get_all_requests()
board.get_open_requests()
board.get_requests_by_type(RequestType.ASSASSINATION)
board.get_requests_by_difficulty(RequestDifficulty.ADVANCED)
board.get_request(request_id)
board.update_request_status(request_id, RequestStatus.COMPLETED)

# User Operations
user = board.register_user("Tanjiro")
board.get_user(user_id)
board.get_user_by_username("Tanjiro")
board.update_user(user)

# Guild Operations
guild = board.create_guild("Hunter's Guild", "Description")
board.get_guild(guild_id)
board.get_guild_requests(guild_id)

# Actions
board.accept_request(user_id, request_id)
board.complete_request(user_id, request_id)  # Awards gold + xp
board.get_user_active_requests(user_id)
board.get_user_completed_requests(user_id)

# Persistence
board.save_state("board_state.json")
board.load_state("board_state.json")
```

## REST API Endpoints

### Browse Requests
```
GET /api/requests
GET /api/requests?type=assassination&difficulty=advanced
GET /api/requests/<request_id>
```

### Post a Request
```
POST /api/requests
{
  "guild_id": "uuid",
  "title": "Task Title",
  "description": "Task description",
  "type": "assassination",
  "difficulty": "advanced",
  "reward_gold": 1000,
  "reward_experience": 500,
  "reward_items": [],
  "reward_description": "Description of reward"
}
```

### Accept/Complete Request
```
POST /api/requests/<request_id>/accept
{
  "user_id": "uuid"
}

POST /api/requests/<request_id>/complete
{
  "user_id": "uuid"
}
```

### User Management
```
POST /api/users/register
{
  "username": "Tanjiro"
}

GET /api/users/<user_id>/profile
GET /api/users/<user_id>/requests
```

### Guild Management
```
POST /api/guilds
{
  "name": "Guild Name",
  "description": "Guild description"
}

GET /api/guilds/<guild_id>
GET /api/guilds/<guild_id>/requests
```

### Data Persistence
```
POST /api/save
POST /api/load
```

## Common Workflows

### Post a Request (As Guild)
```python
guild = board.create_guild("My Guild")
reward = Reward(gold=1000, experience=500)
request = Request(
    title="My Task",
    description="Task description",
    request_type=RequestType.ASSASSINATION,
    difficulty=RequestDifficulty.INTERMEDIATE,
    reward=reward,
    posted_by=guild.id
)
board.post_request(guild.id, request)
```

### Complete Quest (As User)
```python
user = board.register_user("MyCharacter")
board.accept_request(user.id, request_id)
board.complete_request(user.id, request_id)
# User now has: +1000 gold, +500 experience
```

### Check Progress
```python
user = board.get_user(user_id)
print(f"Level: {user.level}")
print(f"Gold: {user.gold}")
print(f"Completed: {user.completed_requests}")
```

### Save/Load Game State
```python
board.save_state("my_save.json")
# Later...
board.load_state("my_save.json")
```

## Level System

- Starts at Level 1
- Requires 100 XP per level
- XP overflows to next level (e.g., gain 150 XP at 50 XP = Level 2 + 50 XP)

## Response Format

### Success Response
```json
{
  "success": true,
  "data": "..."
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message"
}
```

## Type Hints Quick Reference

```python
Optional[str]           # Can be str or None
List[Request]          # List of Request objects
Dict[str, Request]     # Dictionary mapping strings to Request objects
Union[str, int]        # Either str or int
Any                    # Any type (use sparingly)
```

---
**Remember:** Update both `.py` and `.pyi` files when making changes!
