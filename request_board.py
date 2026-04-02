"""
Anime Guild Request Board / Assassin Request Board Implementation

System for posting tasks, managing rewards, and tracking user progress.
"""

import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RequestStatus(Enum):
    """Status of a request"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RequestType(Enum):
    """Types of requests available"""
    ASSASSINATION = "assassination"
    ESCORT = "escort"
    RETRIEVAL = "retrieval"
    EXPLORATION = "exploration"
    DEFENSE = "defense"
    GATHERING = "gathering"
    OTHER = "other"


class RequestDifficulty(Enum):
    """Difficulty level of a request"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    LEGENDARY = "legendary"


class Reward:
    """Represents a reward for completing a request"""
    
    def __init__(self, gold: int, experience: int, items: Optional[List[Dict[str, Any]]] = None, description: str = "") -> None:
        self.id: str = str(uuid.uuid4())
        self.gold: int = gold
        self.experience: int = experience
        self.items: List[Dict[str, Any]] = items or []
        self.description: str = description
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "gold": self.gold,
            "experience": self.experience,
            "items": self.items,
            "description": self.description,
        }


class Request:
    """Represents a single request/task on the board"""
    
    def __init__(
        self,
        title: str,
        description: str,
        request_type: RequestType,
        difficulty: RequestDifficulty,
        reward: Reward,
        posted_by: str,
        deadline: Optional[datetime] = None,
    ) -> None:
        self.id: str = str(uuid.uuid4())
        self.title: str = title
        self.description: str = description
        self.request_type: RequestType = request_type
        self.difficulty: RequestDifficulty = difficulty
        self.status: RequestStatus = RequestStatus.OPEN
        self.reward: Reward = reward
        self.posted_by: str = posted_by
        self.posted_date: datetime = datetime.now()
        self.deadline: Optional[datetime] = deadline
        self.accepted_by: Optional[str] = None
        self.completion_date: Optional[datetime] = None
    
    def accept(self, user_id: str) -> bool:
        """Accept the request"""
        if self.status == RequestStatus.OPEN:
            self.accepted_by = user_id
            self.status = RequestStatus.IN_PROGRESS
            return True
        return False
    
    def complete(self) -> bool:
        """Mark request as completed"""
        if self.status == RequestStatus.IN_PROGRESS:
            self.status = RequestStatus.COMPLETED
            self.completion_date = datetime.now()
            return True
        return False
    
    def cancel(self) -> bool:
        """Cancel the request"""
        if self.status in [RequestStatus.OPEN, RequestStatus.IN_PROGRESS]:
            self.status = RequestStatus.CANCELLED
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "request_type": self.request_type.value,
            "difficulty": self.difficulty.value,
            "status": self.status.value,
            "reward": self.reward.to_dict(),
            "posted_by": self.posted_by,
            "posted_date": self.posted_date.isoformat(),
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "accepted_by": self.accepted_by,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
        }


class Guild:
    """Represents a guild that posts requests"""
    
    def __init__(self, name: str, description: str = "", initial_funds: int = 0) -> None:
        self.id: str = str(uuid.uuid4())
        self.name: str = name
        self.description: str = description
        self.members: List[str] = []
        self.created_date: datetime = datetime.now()
        self.funds: int = initial_funds
    
    def add_member(self, user_id: str) -> bool:
        """Add a member to the guild"""
        if user_id not in self.members:
            self.members.append(user_id)
            return True
        return False
    
    def remove_member(self, user_id: str) -> bool:
        """Remove a member from the guild"""
        if user_id in self.members:
            self.members.remove(user_id)
            return True
        return False
    
    def post_request(self, request: Request) -> bool:
        """Post a request (checks if guild has funds)"""
        if self.funds >= 0:  # Simplified check — allow posting unless bankrupt (negative funds)
            return True
        return False
    
    def fund_update(self, amount: int) -> None:
        """Update guild funds"""
        self.funds += amount
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "members": self.members,
            "created_date": self.created_date.isoformat(),
            "funds": self.funds,
        }


class User:
    """Represents a user/adventurer on the board"""
    
    def __init__(self, username: str, initial_gold: int = 100) -> None:
        self.id: str = str(uuid.uuid4())
        self.username: str = username
        self.level: int = 1
        self.experience: int = 0
        self.gold: int = initial_gold
        self.completed_requests: int = 0
        self.guild_id: Optional[str] = None
        self.joined_date: datetime = datetime.now()
        self.active_requests: List[str] = []  # Request IDs
        self.declined_requests: List[str] = []  # Request IDs the user declined

    def accept_request(self, request_id: str) -> bool:
        """Accept a request"""
        if request_id not in self.active_requests:
            self.active_requests.append(request_id)
            return True
        return False

    def complete_request(self, request_id: str) -> bool:
        """Complete a request"""
        if request_id in self.active_requests:
            self.active_requests.remove(request_id)
            self.completed_requests += 1
            return True
        return False

    def decline_request(self, request_id: str) -> bool:
        """Decline a request"""
        if request_id not in self.declined_requests and request_id not in self.active_requests:
            self.declined_requests.append(request_id)
            return True
        return False
    
    def gain_experience(self, amount: int) -> None:
        """Gain experience points"""
        self.experience += amount
        # Level up every 100 experience
        while self.experience >= 100:
            self.level_up()
    
    def gain_gold(self, amount: int) -> None:
        """Gain gold"""
        self.gold += amount
    
    def join_guild(self, guild_id: str) -> bool:
        """Join a guild"""
        if self.guild_id is None:
            self.guild_id = guild_id
            return True
        return False
    
    def level_up(self) -> None:
        """Level up the user"""
        self.experience -= 100
        self.level += 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "level": self.level,
            "experience": self.experience,
            "gold": self.gold,
            "completed_requests": self.completed_requests,
            "guild_id": self.guild_id,
            "joined_date": self.joined_date.isoformat(),
            "active_requests": self.active_requests,
            "declined_requests": self.declined_requests,
        }


class RequestBoard:
    """Main request board that manages all requests"""
    
    def __init__(self) -> None:
        self.requests: Dict[str, Request] = {}
        self.users: Dict[str, User] = {}
        self.guilds: Dict[str, Guild] = {}
    
    # Request management
    def post_request(self, guild_id: str, request: Request) -> bool:
        """Post a request to the board"""
        guild = self.guilds.get(guild_id)
        if guild and guild.post_request(request):
            self.requests[request.id] = request
            return True
        return False
    
    def get_all_requests(self) -> List[Request]:
        """Get all requests"""
        return list(self.requests.values())
    
    def get_open_requests(self) -> List[Request]:
        """Get all open requests"""
        return [r for r in self.requests.values() if r.status == RequestStatus.OPEN]
    
    def get_requests_by_type(self, request_type: RequestType) -> List[Request]:
        """Get requests filtered by type"""
        return [r for r in self.requests.values() if r.request_type == request_type]
    
    def get_requests_by_difficulty(self, difficulty: RequestDifficulty) -> List[Request]:
        """Get requests filtered by difficulty"""
        return [r for r in self.requests.values() if r.difficulty == difficulty]
    
    def get_request(self, request_id: str) -> Optional[Request]:
        """Get a specific request"""
        return self.requests.get(request_id)
    
    def update_request_status(self, request_id: str, status: RequestStatus) -> bool:
        """Update request status"""
        request = self.requests.get(request_id)
        if request:
            request.status = status
            return True
        return False
    
    # User management
    def register_user(self, username: str) -> User:
        """Register a new user"""
        user = User(username)
        self.users[user.id] = user
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def update_user(self, user: User) -> bool:
        """Update user data"""
        if user.id in self.users:
            self.users[user.id] = user
            return True
        return False
    
    # Guild management
    def create_guild(self, name: str, description: str = "") -> Guild:
        """Create a new guild"""
        guild = Guild(name, description)
        self.guilds[guild.id] = guild
        return guild
    
    def get_guild(self, guild_id: str) -> Optional[Guild]:
        """Get a guild by ID"""
        return self.guilds.get(guild_id)
    
    def get_guild_requests(self, guild_id: str) -> List[Request]:
        """Get all requests posted by a guild"""
        return [r for r in self.requests.values() if r.posted_by == guild_id]
    
    # Actions
    def accept_request(self, user_id: str, request_id: str) -> bool:
        """Accept a request as a user"""
        user = self.users.get(user_id)
        request = self.requests.get(request_id)
        
        if user and request and request.accept(user_id):
            user.accept_request(request_id)
            return True
        return False
    
    def complete_request(self, user_id: str, request_id: str) -> bool:
        """Complete a request and award rewards"""
        user = self.users.get(user_id)
        request = self.requests.get(request_id)
        
        if user and request and request.accepted_by == user_id:
            if request.complete():
                user.complete_request(request_id)
                user.gain_gold(request.reward.gold)
                user.gain_experience(request.reward.experience)
                return True
        return False
    
    def decline_request(self, user_id: str, request_id: str) -> bool:
        """Decline a request (stays open for others; tracked on the user)"""
        user = self.users.get(user_id)
        request = self.requests.get(request_id)
        if user and request and request.status == RequestStatus.OPEN:
            return user.decline_request(request_id)
        return False

    def get_user_declined_requests(self, user_id: str) -> List[Request]:
        """Get all requests a user has declined"""
        user = self.users.get(user_id)
        if user:
            return [self.requests[rid] for rid in user.declined_requests if rid in self.requests]
        return []

    def get_user_active_requests(self, user_id: str) -> List[Request]:
        """Get all active requests for a user"""
        user = self.users.get(user_id)
        if user:
            return [self.requests[rid] for rid in user.active_requests if rid in self.requests]
        return []
    
    def get_user_completed_requests(self, user_id: str) -> List[Request]:
        """Get all completed requests by a user"""
        return [
            r for r in self.requests.values()
            if r.accepted_by == user_id and r.status == RequestStatus.COMPLETED
        ]
    
    # Data persistence
    def save_state(self, filepath: str) -> bool:
        """Save board state to JSON file"""
        try:
            data = {
                "requests": {rid: r.to_dict() for rid, r in self.requests.items()},
                "users": {uid: u.to_dict() for uid, u in self.users.items()},
                "guilds": {gid: g.to_dict() for gid, g in self.guilds.items()},
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving state: {e}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """Load board state from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Restore guilds
            self.guilds = {}
            for gid, gdata in data.get("guilds", {}).items():
                guild = Guild(gdata["name"], gdata.get("description", ""))
                guild.id = gdata["id"]
                guild.members = gdata.get("members", [])
                guild.funds = gdata.get("funds", 0)
                guild.created_date = datetime.fromisoformat(gdata["created_date"])
                self.guilds[guild.id] = guild

            # Restore users
            self.users = {}
            for uid, udata in data.get("users", {}).items():
                user = User(udata["username"])
                user.id = udata["id"]
                user.level = udata.get("level", 1)
                user.experience = udata.get("experience", 0)
                user.gold = udata.get("gold", 100)
                user.completed_requests = udata.get("completed_requests", 0)
                user.guild_id = udata.get("guild_id")
                user.joined_date = datetime.fromisoformat(udata["joined_date"])
                user.active_requests = udata.get("active_requests", [])
                user.declined_requests = udata.get("declined_requests", [])
                self.users[user.id] = user

            # Restore requests
            self.requests = {}
            for rid, rdata in data.get("requests", {}).items():
                reward_data = rdata["reward"]
                reward = Reward(
                    gold=reward_data["gold"],
                    experience=reward_data["experience"],
                    items=reward_data.get("items", []),
                    description=reward_data.get("description", ""),
                )
                reward.id = reward_data["id"]

                req = Request(
                    title=rdata["title"],
                    description=rdata["description"],
                    request_type=RequestType(rdata["request_type"]),
                    difficulty=RequestDifficulty(rdata["difficulty"]),
                    reward=reward,
                    posted_by=rdata["posted_by"],
                )
                req.id = rdata["id"]
                req.status = RequestStatus(rdata["status"])
                req.posted_date = datetime.fromisoformat(rdata["posted_date"])
                req.accepted_by = rdata.get("accepted_by")
                req.completion_date = (
                    datetime.fromisoformat(rdata["completion_date"])
                    if rdata.get("completion_date") else None
                )
                self.requests[req.id] = req

            print(f"Loaded state from {filepath}")
            return True
        except Exception as e:
            print(f"Error loading state: {e}")
            return False


class RequestBoardAPI:
    """Flask API wrapper for the request board"""
    
    def __init__(self, board: RequestBoard) -> None:
        self.board: RequestBoard = board
    
    # Request endpoints
    def get_all_requests(self) -> Dict[str, Any]:
        """Get all requests"""
        requests = self.board.get_all_requests()
        return {
            "success": True,
            "requests": [r.to_dict() for r in requests],
            "count": len(requests),
        }
    
    def get_request_by_id(self, request_id: str) -> Dict[str, Any]:
        """Get a specific request"""
        request = self.board.get_request(request_id)
        if request:
            return {"success": True, "request": request.to_dict()}
        return {"success": False, "error": "Request not found"}
    
    def post_request(self, guild_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post a new request"""
        try:
            guild = self.board.get_guild(guild_id)
            if not guild:
                return {"success": False, "error": "Guild not found"}
            
            reward = Reward(
                gold=request_data.get("reward_gold", 0),
                experience=request_data.get("reward_experience", 0),
                items=request_data.get("reward_items", []),
                description=request_data.get("reward_description", ""),
            )
            
            request = Request(
                title=request_data["title"],
                description=request_data["description"],
                request_type=RequestType[request_data.get("type", "OTHER").upper()],
                difficulty=RequestDifficulty[request_data.get("difficulty", "BEGINNER").upper()],
                reward=reward,
                posted_by=guild_id,
                deadline=None,
            )
            
            if self.board.post_request(guild_id, request):
                return {"success": True, "request_id": request.id}
            return {"success": False, "error": "Failed to post request"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def accept_request(self, user_id: str, request_id: str) -> Dict[str, Any]:
        """Accept a request"""
        if self.board.accept_request(user_id, request_id):
            return {"success": True, "message": "Request accepted"}
        return {"success": False, "error": "Failed to accept request"}
    
    def decline_request(self, user_id: str, request_id: str) -> Dict[str, Any]:
        """Decline a request"""
        if self.board.decline_request(user_id, request_id):
            return {"success": True, "message": "Request declined"}
        return {"success": False, "error": "Failed to decline request"}

    def complete_request(self, user_id: str, request_id: str) -> Dict[str, Any]:
        """Complete a request"""
        if self.board.complete_request(user_id, request_id):
            request = self.board.get_request(request_id)
            user = self.board.get_user(user_id)
            return {
                "success": True,
                "message": "Request completed",
                "reward": request.reward.to_dict() if request else None,
                "user_level": user.level if user else None,
                "user_gold": user.gold if user else None,
            }
        return {"success": False, "error": "Failed to complete request"}
    
    # User endpoints
    def register_user(self, username: str) -> Dict[str, Any]:
        """Register a new user"""
        existing = self.board.get_user_by_username(username)
        if existing:
            return {"success": False, "error": "Username already taken"}
        
        user = self.board.register_user(username)
        return {"success": True, "user_id": user.id, "username": user.username}
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        user = self.board.get_user(user_id)
        if user:
            return {"success": True, "user": user.to_dict()}
        return {"success": False, "error": "User not found"}
    
    def get_user_requests(self, user_id: str) -> Dict[str, Any]:
        """Get user's requests"""
        user = self.board.get_user(user_id)
        if user:
            active = self.board.get_user_active_requests(user_id)
            completed = self.board.get_user_completed_requests(user_id)
            declined = self.board.get_user_declined_requests(user_id)
            return {
                "success": True,
                "active_requests": [r.to_dict() for r in active],
                "completed_requests": [r.to_dict() for r in completed],
                "declined_requests": [r.to_dict() for r in declined],
            }
        return {"success": False, "error": "User not found"}
    
    # Guild endpoints
    def create_guild(self, name: str, description: str) -> Dict[str, Any]:
        """Create a new guild"""
        guild = self.board.create_guild(name, description)
        return {"success": True, "guild_id": guild.id, "name": guild.name}
    
    def get_guild(self, guild_id: str) -> Dict[str, Any]:
        """Get guild information"""
        guild = self.board.get_guild(guild_id)
        if guild:
            return {"success": True, "guild": guild.to_dict()}
        return {"success": False, "error": "Guild not found"}
    
    def get_guild_requests(self, guild_id: str) -> Dict[str, Any]:
        """Get all requests from a guild"""
        guild = self.board.get_guild(guild_id)
        if guild:
            requests = self.board.get_guild_requests(guild_id)
            return {
                "success": True,
                "requests": [r.to_dict() for r in requests],
                "count": len(requests),
            }
        return {"success": False, "error": "Guild not found"}
