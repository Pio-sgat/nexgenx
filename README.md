# NEXGENX

A small Flask app for publishing and displaying a public NEXGENX project showcase.

## Run locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. Published project details are stored in `nexgenx.db`; attachments are saved in `uploads/`.
