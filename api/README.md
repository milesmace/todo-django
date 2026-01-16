# API CLI Tool

A generic, minimal Bash CLI tool for testing HTTP APIs. This tool is a thin wrapper over `curl` + `jq` designed to work with any REST API without code changes.

## Features

- Generic HTTP client - works with any API
- No endpoint-specific logic
- Environment-based configuration
- Pretty-printed JSON output
- Verbose mode for debugging
- Token masking in verbose output

## Requirements

- `bash` (4.0+)
- `curl`
- `jq`

## Installation

1. Make the script executable:

```bash
chmod +x api
```

2. Copy the example environment file:

```bash
cp .env.example .env
```

3. Edit `.env` with your API settings.

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_BASE` | Yes | Base URL for the API (e.g., `http://localhost:8000`) |
| `DEFAULT_HEADERS` | No | Pipe-separated list of default headers |
| `AUTH_HEADER` | No | Authorization header name (default: `Authorization`) |
| `AUTH_TOKEN` | No | Bearer token for authentication |

### Example `.env` File

```bash
API_BASE=http://localhost:8000
DEFAULT_HEADERS="Content-Type: application/json|Accept: application/json"
AUTH_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Usage

```
api [OPTIONS] METHOD PATH [PAYLOAD_FILE]
```

### Options

| Option | Description |
|--------|-------------|
| `-e, --env <file>` | Load custom environment file (default: `.env`) |
| `-v, --verbose` | Enable verbose output |
| `-h, --help` | Show help message |

### Arguments

| Argument | Description |
|----------|-------------|
| `METHOD` | HTTP method (GET, POST, PUT, PATCH, DELETE) |
| `PATH` | API endpoint path (e.g., `/api/todos/`) |
| `PAYLOAD_FILE` | Optional JSON file for request body |

## Examples

### Basic GET Request

```bash
./api GET /api/todos/
```

Output:
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "is_completed": false
  }
]
```

### POST with Payload File

Create a payload file `payloads/todo.json`:
```json
{
  "title": "Learn Bash",
  "description": "Master shell scripting"
}
```

Execute:
```bash
./api POST /api/todos/ payloads/todo.json
```

### PUT Request

```bash
./api PUT /api/todos/1/ payloads/update.json
```

### DELETE Request

```bash
./api DELETE /api/todos/1/
```

### Verbose Mode

```bash
./api -v POST /api/todos/ payloads/todo.json
```

Output:
```
──────── REQUEST ────────
METHOD: POST
URL: http://localhost:8000/api/todos/
HEADERS:
  Content-Type: application/json
  Authorization: Bearer eyJh****JWT9

PAYLOAD:
{
  "title": "Learn Bash",
  "description": "Master shell scripting"
}

──────── RESPONSE ────────
STATUS: 201

BODY:
{
  "id": 2,
  "title": "Learn Bash",
  "description": "Master shell scripting",
  "is_completed": false
}
```

### Using Custom Environment File

```bash
./api --env .env.prod GET /api/users/
```

### Combining Options

```bash
./api -v -e .env.staging POST /api/todos/ payloads/todo.json
```

## File Structure

```
api/
├── api              # Main executable script
├── .env             # Your local configuration (git-ignored)
├── .env.example     # Example configuration template
├── payloads/        # Directory for JSON payload files
│   ├── todo.json
│   └── user.json
└── README.md        # This file
```

## Error Handling

The tool handles errors gracefully:

- **Missing `jq`**: Fails with installation instructions
- **Missing `API_BASE`**: Shows error with example
- **Missing payload file**: Shows error message
- **HTTP errors (4xx/5xx)**: Prints response body and exits with code 1
- **Non-JSON responses**: Prints raw body without formatting

## Tips

### Quick Authentication Setup

After logging in via your browser or other tool, export your token:

```bash
export AUTH_TOKEN="your-token-here"
./api GET /api/protected-resource/
```

### Multiple Environments

Create separate env files for different environments:

```bash
# Development
./api -e .env.dev GET /api/todos/

# Staging
./api -e .env.staging GET /api/todos/

# Production
./api -e .env.prod GET /api/todos/
```

### Shell Alias

Add to your `.bashrc` or `.zshrc`:

```bash
alias api='/path/to/api/api'
```

## Non-Goals

This tool intentionally does NOT include:

- Endpoint-specific subcommands (login, users, orders)
- Token file storage or persistence
- OpenAPI/Swagger parsing
- Request collections or frameworks
- Hidden state management

This keeps the tool generic and applicable to any REST API.
