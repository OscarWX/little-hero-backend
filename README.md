# Little Hero Backend

A FastAPI-based backend for the Little Hero project.

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

## Project Structure

- `main.py` - Main application entry point
- `requirements.txt` - Project dependencies 