# AutoBiz AI — Django Edition

Python/Django port of the CodeIgniter 4 "AutoBiz AI" app in `../website_agent`.
Add a business, and a chain of GPT agents writes its branding, website copy and
five complete single-page website designs, which you preview or download as a ZIP.

Full documentation (architecture, UML, data model, setup): `docs/AutoBiz_AI_Django_Project_Document.pdf`.

## Quick start (Windows)

1. Start **MySQL** in the XAMPP control panel (or set `DB_ENGINE=sqlite` in `.env`).
2. Double-click **`run.bat`**. It creates `.venv`, installs requirements, creates
   the database, applies migrations and opens http://127.0.0.1:8000.

`run_pipeline.bat` runs the pipeline from the command line (`run_pipeline.bat 5` for business #5).

## Manual commands

```bat
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env               & rem then fill in OPENAI_API_KEY etc.
.venv\Scripts\python manage.py ensure_database
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py runserver

.venv\Scripts\python manage.py agent_run [--id N]   & rem pipeline from the CLI
.venv\Scripts\python manage.py import_legacy        & rem copy data from the CI4 database
.venv\Scripts\python manage.py createsuperuser      & rem for /admin
.venv\Scripts\python manage.py test dashboard       & rem 14 tests
```

With `OPENAI_API_KEY` empty the agents return offline stub content, so the whole
pipeline can be exercised without API costs.

## Database options (`DB_ENGINE` in `.env`)

| Value          | Server                                              |
| -------------- | --------------------------------------------------- |
| `sqlite`       | `db.sqlite3` in the project folder, no setup        |
| `mysql`        | MySQL 8.4+ / MariaDB 10.11+ (Django 6 requirement)  |
| `mysql_legacy` | Older servers such as XAMPP's MariaDB 10.4 (default) |

## Regenerating the project document

```bat
.venv\Scripts\pip install reportlab
.venv\Scripts\python docs\build_project_doc.py
```
