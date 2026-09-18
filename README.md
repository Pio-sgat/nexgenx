# NEXGENX

A small Flask app for collecting and storing project details.

## Run locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. Submitted details are stored in `nexgenx.db`; attachments are saved in `uploads/`.
