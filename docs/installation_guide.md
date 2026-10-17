# Windows setup

1. Install Python 3.11, VS Code, Git.
2. Open the repository folder in VS Code.
3. `python -m venv .venv`
4. PowerShell: `.\.venv\Scripts\Activate.ps1`; CMD: `.venv\Scripts\activate.bat`.
5. `python -m pip install -r requirements.txt`
6. `python main.py all`
7. `python -m pytest -q`
8. `python -m streamlit run app/dashboard.py`

To regenerate a locked list from your own working environment: `python -m pip freeze > requirements-lock.txt`.
