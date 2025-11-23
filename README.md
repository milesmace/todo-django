# Django Todo App

A Django application with PostgreSQL, Docker setup, and code quality tools.

## Project Structure

```
.
├── src/                    # Django project code
│   └── todoapp/           # Django project
├── .venv/                 # Python virtual environment
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
└── pyproject.toml         # Black and Ruff configuration
```

## Setup

### Local Development

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and set your values. Required variables:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_NAME=todoapp
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5432
   POSTGRES_DB=todoapp
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   ```

   **Important:** Never commit the `.env` file to version control. It contains sensitive information.

4. **Set up pre-commit hooks:**
   ```bash
   git init  # If not already a git repository
   pre-commit install
   ```

5. **Run database migrations:**
   ```bash
   python src/manage.py migrate
   ```

6. **Start the development server:**
   ```bash
   python src/manage.py runserver
   ```

### Docker Setup

1. **Set up environment variables:**
   Create a `.env` file in the root directory (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

   For Docker, make sure `DB_HOST=db` in your `.env` file (not `localhost`).

2. **Build and start containers:**
   ```bash
   docker compose up --build -d
   ```

3. **Run migrations (if needed):**
   ```bash
   docker compose exec web python src/manage.py migrate
   ```

4. **Create a superuser:**
   ```bash
   docker compose exec web python src/manage.py createsuperuser
   ```

4. **Access the application:**
   - Web: http://localhost:8000
   - PostgreSQL: localhost:5432

## Code Quality Tools

### Black (Code Formatter)
Format code with:
```bash
black src/
```

### Ruff (Linter)
Lint code with:
```bash
ruff check src/
```

Auto-fix issues:
```bash
ruff check --fix src/
```

### Pre-commit Hooks
Pre-commit hooks automatically run Black and Ruff before each commit. They are configured in `.pre-commit-config.yaml`.

## Requirements Files

- `requirements.txt`: Production dependencies (Django, PostgreSQL driver, etc.)
- `requirements-dev.txt`: Development dependencies (includes production + Black, Ruff, pre-commit)

## Environment Variables

All sensitive configuration is stored in the `.env` file, which is excluded from version control. The `.env.example` file serves as a template.

**Security Note:**
- Never commit `.env` to version control
- Change `SECRET_KEY` in production
- Use strong passwords for database credentials in production
- Set `DEBUG=False` in production

## Database

The application uses PostgreSQL. All database credentials are configured via the `.env` file:
- For Docker: `DB_HOST=db`
- For local development: `DB_HOST=localhost`

Ensure PostgreSQL is running and the credentials in `.env` match your database setup.
