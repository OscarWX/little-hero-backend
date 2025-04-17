# Backend API

A FastAPI-based backend project.

## Setup

1. Clone the repository
2. Create a virtual environment and activate it:
   ```
   python -m venv .venv
   # On Windows:
   .\.venv\Scripts\activate
   # On Unix/MacOS:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

Start the development server:
```
uvicorn main:app --reload
```

The server will start at http://localhost:8000

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: http://localhost:8000/docs
- Alternative documentation: http://localhost:8000/redoc

## Version Control with Git

The project uses Git for version control. Here are some common commands:

### Tracking Changes

1. Check status of changes:
   ```
   git status
   ```

2. Stage changes for commit:
   ```
   git add <filename>   # Stage specific file
   git add .            # Stage all changes
   ```

3. Commit changes:
   ```
   git commit -m "Description of changes"
   ```

### GitHub Integration

1. Connect to a GitHub repository:
   ```
   git remote add origin https://github.com/username/backend-project.git
   ```

2. Push to GitHub:
   ```
   git push -u origin master   # First push
   git push                    # Subsequent pushes
   ```

3. Pull changes from GitHub:
   ```
   git pull
   ```

### Undoing Changes

1. Discard changes in working directory:
   ```
   git checkout -- <filename>   # For specific file
   git checkout -- .            # For all files
   ```

2. Undo last commit (keeping changes):
   ```
   git reset --soft HEAD~1
   ```

3. View commit history:
   ```
   git log
   ```

4. Revert to a specific commit:
   ```
   git checkout <commit-hash>
   ```

## Project Structure

- `main.py` - Main application entry point with API routes
- `requirements.txt` - Project dependencies 