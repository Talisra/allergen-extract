**Installation**
1. Create virtual environment:
`python -m venv .venv`
activate:
`.venv/scripts/activate`
2. Install dependencies:
`pip install -r requirements.txt`
3. Run the server:
`uvicorn server:app --reload`
4. Use the app from `http://127.0.0.1:8000/`