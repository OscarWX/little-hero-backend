# Little Hero Backend API

A FastAPI-based backend project for the Little Hero platform, which allows users to create personalized children's picture books.

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
python main.py
```

The server will start at http://0.0.0.0:8000

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: http://localhost:8000/docs
- Alternative documentation: http://localhost:8000/redoc

## API Endpoints

### User Management

- **POST /api/users/register** - Register a new user
- **POST /api/users/login** - Authenticate and get a token

### Book Creation

- **POST /api/books** - Create a new book request
- **GET /api/books/{book_id}** - Get the status of a book
- **GET /api/books** - List all books created by the user
- **GET /api/books/{book_id}/download** - Download a completed book

### Adventure Types

- **GET /api/adventure-types** - Get a list of available adventure types

## Project Structure

- `app/` - Main application package
  - `database/` - Database configuration and models
  - `models/` - SQLAlchemy ORM models
  - `routers/` - API endpoint routers
  - `schemas/` - Pydantic models for request/response
  - `utils/` - Utility functions
    - `storage.py` - S3 storage integration
    - `storage_management.py` - Utility script for S3 management
- `static/` - Static files (images, etc.)
- `uploads/` - Directory for user uploads
- `main.py` - Application entry point

## Amazon S3 Storage Integration

The application uses Amazon S3 for storing:
- User-uploaded photos
- Generated book illustrations
- Final PDF books
- Book thumbnails

### Configuration

S3 storage is configured through environment variables in the `.env` file:

```
S3_BUCKET_NAME="your-bucket-name"
S3_REGION="your-region"
S3_ACCESS_KEY="your-access-key"
S3_SECRET_KEY="your-secret-key"
```

### Storage Management

A utility script is provided for managing S3 storage:

```
# List all objects in the bucket
python -m app.utils.storage_management list

# List objects with a specific prefix
python -m app.utils.storage_management list --prefix="books/"

# Delete a specific object
python -m app.utils.storage_management delete "books/123/photos/image.jpg"

# Delete all objects with a specific prefix
python -m app.utils.storage_management delete-prefix "books/123/"

# Set up lifecycle policies
python -m app.utils.storage_management setup-lifecycle
```

### Storage Lifecycle

The application automatically configures lifecycle policies for S3:
- Temporary uploads are deleted after 1 day
- Processing files are deleted after 7 days

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
   git remote add origin https://github.com/username/little-hero-backend.git
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