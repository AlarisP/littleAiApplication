# Development Guide

## Important: Maintaining the .pyi File

The `request_board.pyi` file is a **type stub file** that defines the complete interface and type hints for the request board system. This file is crucial for:
- IDE autocompletion
- Static type checking with tools like mypy
- Documentation of the API contract

### When to Update request_board.pyi

**You MUST update `request_board.pyi` whenever you:**

1. **Add a new method** to any class
2. **Change a method signature** (add/remove/rename parameters)
3. **Change return types** of methods
4. **Add new class attributes**
5. **Change method visibility** (public/private)
6. **Add new enums or enum values**

### How to Update request_board.pyi

The `.pyi` file should mirror the structure of `request_board.py`:

**In request_board.py:**
```python
def accept_request(self, user_id: str, request_id: str) -> bool:
    """Accept the request"""
    # implementation
```

**In request_board.pyi:**
```python
def accept_request(self, user_id: str, request_id: str) -> bool: ...
```

Key differences:
- `.pyi` files use `...` (ellipsis) instead of implementation code
- Include all docstrings for documentation
- Include all type hints exactly as in the implementation

## File Structure Overview

### request_board.pyi (Type Stubs)
- Defines all class and function signatures
- Type hints for all parameters and returns
- Docstrings for documentation
- No implementation code

### request_board.py (Core Implementation)
- Business logic for request board
- All database/state management operations
- Enum definitions
- Model classes

### app.py (Flask Web App)
- HTTP endpoints
- Request routing
- JSON response handling
- Demo data setup

### templates/index.html
- Main webpage layout
- Request cards display
- Action buttons

### static/style.css
- Styling and layout
- Responsive design
- Anime-themed colors and fonts

### static/script.js
- Frontend interactions
- API calls
- Form handling

## Adding a New Feature

### Example: Add a "Tags" system to Requests

1. **Update request_board.py:**
```python
class Request:
    def __init__(self, ..., tags: Optional[List[str]] = None):
        # ... existing code ...
        self.tags: List[str] = tags or []
    
    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)
    
    def to_dict(self) -> Dict[str, Any]:
        # ... existing code ...
        result["tags"] = self.tags
        return result
```

2. **Update request_board.pyi:**
```python
class Request:
    tags: List[str]
    
    def __init__(
        self,
        # ... existing params ...
        tags: Optional[List[str]] = None,
    ) -> None: ...
    
    def add_tag(self, tag: str) -> None: ...
    
    def to_dict(self) -> Dict[str, Any]: ...
```

3. **Add API endpoint in app.py:**
```python
@app.route('/api/requests/<request_id>/tags', methods=['POST'])
def add_tag_to_request(request_id):
    data = request.get_json()
    tag = data.get('tag')
    # ... implementation ...
```

4. **Update HTML/CSS/JS** if needed for UI

## Testing Locally

### Without installing dependencies:
```bash
python request_board.py  # Test the core logic
```

### With Flask:
```bash
pip install -r requirements.txt
python app.py
```

Then visit `http://localhost:5000`

## Type Checking

To check for type issues with mypy:
```bash
pip install mypy
mypy request_board.py
```

## Git Workflow

When committing changes:
1. Always commit `request_board.py` and `request_board.pyi` together
2. If you forget to update `.pyi`, the next developer will catch it in code review
3. Use descriptive commit messages mentioning both files

Example:
```
git add request_board.py request_board.pyi app.py
git commit -m "Add tags system to requests (updates .pyi signatures)"
```

## Common Mistakes to Avoid

❌ **Don't:**
- Update only `request_board.py` and forget `request_board.pyi`
- Change method signatures without updating type hints
- Add new attributes without documenting their types
- Use `Any` type when more specific typing is possible

✅ **Do:**
- Update both files simultaneously
- Keep type hints consistent across files
- Use descriptive type hints (e.g., `Dict[str, Request]` instead of `dict`)
- Add docstrings to clarify intent

## Architecture Pattern

The project uses a classic layered architecture:

```
Frontend (HTML/CSS/JS)
    ↓ (HTTP calls)
API Layer (app.py + RequestBoardAPI class)
    ↓ (method calls)
Business Logic (RequestBoard + Models)
    ↓ (state management)
Memory (Python objects + JSON persistence)
```

Each layer has clear responsibilities and interfaces defined in `.pyi` files.
