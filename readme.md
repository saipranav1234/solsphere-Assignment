python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001

python -m system_utility.daemon
pyinstaller --onefile system_utility/main.py

npm run dev
