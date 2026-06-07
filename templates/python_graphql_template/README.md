# GraphQL API Template

A production-ready GraphQL API template built with FastAPI and Strawberry GraphQL, featuring Docker support, rate limiting, logging, and security features.

## Features

- **Strawberry GraphQL**: Modern, type-safe GraphQL library for Python
- **FastAPI Integration**: Seamless integration with FastAPI
- **Docker Support**: Multi-stage Dockerfile and docker-compose for easy deployment
- **Rate Limiting**: Built-in request rate limiting with SlowAPI on the GraphQL endpoint
- **Comprehensive Logging**: File and console logging with configurable levels
- **Security**: Non-root user in Docker, input validation, encryption utilities
- **Configuration**: JSON-based configuration management via `config_loader`
- **Health Checks**: Built-in health check endpoint
- **Development Ready**: Hot reload support and GraphiQL interface
- **Type Safety**: Full type safety with Python type hints and Strawberry

## Project Structure

```
python_graphql_template/
├── src/
│   ├── graphql_schema/             # GraphQL schema definition
│   │   └── schema.py               # Combines Query + Mutation into schema
│   ├── resolvers/                  # GraphQL resolvers
│   │   ├── query.py                # Root Query (inherits example mixins)
│   │   ├── mutation.py             # Root Mutation (inherits example mixins)
│   │   ├── example_items_store.py  # Shared in-memory store for examples
│   │   ├── specific_resolver_group_1/
│   │   │   └── example_query.py    # Reference query — copy this pattern
│   │   └── specific_resolver_group_2/
│   │       └── example_mutation.py # Reference mutation — copy this pattern
│   ├── types/                      # Strawberry GraphQL type definitions
│   │   ├── user.py                 # User type (sample data)
│   │   ├── post.py                 # Post type (sample data)
│   │   └── example_item.py         # Example entity type + input
│   ├── models/
│   │   └── models_example.py       # Pydantic model pattern (for non-GraphQL use)
│   ├── core_specs/                 # Core configuration and static data
│   │   ├── configuration/
│   │   │   ├── config_file.json        # Network, GraphQL, endpoint settings
│   │   │   └── config_loader.py        # Loads config_file.json → config_loader
│   │   └── data/
│   │       ├── general_data.json         # Static reference + sample data
│   │       └── data_loader.py            # Loads general_data.json → data_loader
│   ├── resources/                  # Database-related assets (placeholder)
│   │   ├── db/                         # Migration files (add when needed)
│   │   └── mock_db_jsons/              # Mock JSON tables (add when needed)
│   └── utils/
│       ├── custom_logger.py        # Logging configuration (log_handler)
│       ├── limiter.py              # Shared SlowAPI limiter instance
│       ├── request_limiter.py      # 429 handler for rate-limit exceeded
│       ├── validators.py           # Email, password, phone, token, UUID validators
│       ├── en_de_crypt.py          # RSA encrypt/decrypt (requires .env keys)
│       ├── keys_generator.py       # One-off script to generate RSA key pairs
│       ├── secure_file_io.py       # Hardened atomic file read/write helpers
│       └── pycache_n_logs_deleter.py  # Dev utility to purge __pycache__ / logs
├── logs/                           # Log files (created automatically)
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
├── start.sh / start.bat            # Dev setup and launch scripts
├── DOCKERFILE                      # Docker build configuration
├── docker-compose.yml              # Docker compose configuration
├── .env / .env.example             # Environment variables template
├── .dockerignore
├── .gitignore
└── README.md
```

## Quick Start

### Option 1: Run with Python (Development)

1. **Clone and setup**:
   ```bash
   cd templates/python_graphql_template
   python -m venv venv
   source venv/bin/activate          # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env.local        # or copy .env on Windows
   # Edit .env.local — set E_PRIVATE_KEY, E_PRIVATE_PASSWORD, E_PUBLIC_KEY
   # (run src/utils/keys_generator.py once to generate them)
   ```

3. **Run the application**:
   ```bash
   python main.py
   # or: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the API**:
   - GraphQL / GraphiQL: http://localhost:8000/graphql
   - Health check: http://localhost:8000/health

### Option 2: Run with Docker (Production)

```bash
cd templates/python_graphql_template
docker-compose up --build
```

Or manually:

```bash
docker build -t graphql-api-template .
docker run -p 8000:8000 --env-file .env graphql-api-template
```

### Option 3: Use Startup Scripts

```bash
# Linux/Mac
chmod +x start.sh && ./start.sh

# Windows
start.bat
```

## Configuration

### Environment Variables (.env)

```bash
# Server (overridden by config_file.json when using python main.py)
SERVER_PORT=8000
HOST=0.0.0.0
RELOAD=false
WORKERS=1

# RSA encryption keys (required by en_de_crypt.py)
E_PRIVATE_KEY=your_private_key_here
E_PRIVATE_PASSWORD=your_private_password_here
E_PUBLIC_KEY=your_public_key_here

# API metadata (read by main.py)
API_TITLE=GraphQL API Template
API_VERSION=1.0.0
API_DESCRIPTION=A template for building GraphQL APIs

# GraphQL (also configured in config_file.json)
GRAPHQL_ENDPOINT=/graphql
GRAPHIQL_ENABLED=true
INTROSPECTION_ENABLED=true
```

### JSON Configuration (`config_file.json` + `config_loader`)

`config_loader.py` reads `config_file.json` at import time and exposes the result as `config_loader` (a dict).

**Sections in `config_file.json`:**

| Section | Purpose |
|---|---|
| `defaults` | Shared paths and defaults |
| `logging` | Log level, directory, file name prefix |
| `email_validation` | Allowed email providers and TLDs (used by `validators.py`) |
| `network` | Uvicorn host, port, workers, reload |
| `graphql` | GraphQL endpoint path, GraphiQL, introspection, rate limits |
| `endpoints` | Health check route and per-field example resolver config |

**Example resolver config shape** (one entry per query/mutation field):

```json
"example_endpoint_1": {
    "field_name": "exampleItems",
    "description": "List all example items"
}
```

**Usage in a resolver:**

```python
from src.core_specs.configuration.config_loader import config_loader

_cfg = config_loader["endpoints"]["example_endpoint_1"]

@strawberry.type
class ExampleItemsQuery:
    @strawberry.field(name=_cfg["field_name"])
    def example_items(self) -> List[ExampleItem]:
        ...
```

### Static Data (`general_data.json` + `data_loader`)

`data_loader.py` loads `src/core_specs/data/general_data.json`. Use it for reference data and template sample data (`sample_data.users`, `sample_data.posts`).

```python
from src.core_specs.data.data_loader import data_loader

languages = data_loader["languages"]
users = data_loader["sample_data"]["users"]
```

## Adding New Resolvers

Use the two example resolver files as the canonical reference:

| File | Role | Config key |
|---|---|---|
| `specific_resolver_group_1/example_query.py` | List example items (query) | `example_endpoint_1` |
| `specific_resolver_group_2/example_mutation.py` | Create example item (mutation) | `example_endpoint_2` |

Each file contains **one field only**. Add further fields in separate files within the same group folder.

**Steps to add a new resolver:**

1. Add an entry under `endpoints` in `config_file.json` with a `field_name`.
2. Create Strawberry types in `src/types/` (see `example_item.py`).
3. Copy `example_query.py` or `example_mutation.py` into a new file under `src/resolvers/<your_group>/`.
4. Register the mixin on the root type in `query.py` or `mutation.py`:
   ```python
   from src.resolvers.your_group.your_query import YourQueryMixin

   @strawberry.type
   class Query(YourQueryMixin, ...):
       ...
   ```

### Example queries and mutations

```graphql
# Template example — list items
query {
  exampleItems {
    id
    name
    description
  }
}

# Template example — create item
mutation {
  createExampleItem(input: {
    name: "My item"
    description: "Optional description"
    contactEmail: "alice@gmail.com"
  }) {
    id
    name
  }
}

# Sample data — list users with posts
query {
  users(activeOnly: true) {
    id
    name
    email
    posts {
      id
      title
      published
    }
  }
}

# Sample data — create a post
mutation {
  createPost(input: {
    title: "My New Post"
    content: "Post content"
    authorId: 1
    published: true
  }) {
    id
    title
    author {
      name
    }
  }
}
```

## Types (`src/types/`)

Each entity gets a Strawberry `@strawberry.type` for responses and `@strawberry.input` for mutations. See `example_item.py` for the minimal pattern.

For circular references between types (e.g. `User.posts` ↔ `Post.author`), use `Annotated` with `strawberry.lazy`:

```python
from typing import TYPE_CHECKING, Annotated, List
import strawberry

if TYPE_CHECKING:
    from src.types.post import Post

@strawberry.type
class User:
    @strawberry.field
    def posts(self) -> List[Annotated["Post", strawberry.lazy("src.types.post")]]:
        ...
```

## Models (`src/models/`)

`models_example.py` shows the Pydantic split for REST-style payloads or internal validation. GraphQL resolvers use Strawberry types in `src/types/` instead, but the same Base / Create / Update / Response naming applies when you add Pydantic models for other layers.

## Utilities (`src/utils/`)

| Module | When to use |
|---|---|
| `custom_logger.py` | `log_handler` — use everywhere instead of `print` |
| `limiter.py` | Shared `limiter` instance; applied to `/graphql` in `main.py` |
| `request_limiter.py` | Registered in `main.py` as the global 429 handler |
| `validators.py` | `validate_email_format`, `validate_password_format`, `validate_phone_format`, token/UUID checks |
| `en_de_crypt.py` | `encrypt_in` / `decrypt_out` for RSA-encrypted request fields |
| `keys_generator.py` | Run once to generate `E_PRIVATE_KEY` / `E_PUBLIC_KEY` for `.env` |
| `secure_file_io.py` | Safe atomic file reads/writes with path confinement |
| `pycache_n_logs_deleter.py` | Dev cleanup script — set `ROOT_FOLDER` before running |

## Security Features

- **Rate Limiting**: Applied to the `/graphql` endpoint via middleware in `main.py`
- **Input Validation**: Strawberry input types + `validators.py` helpers
- **Type Safety**: Full type hints with lazy resolution for circular types
- **Non-root Docker**: Container runs as non-root user
- **Environment Variables**: Sensitive data via `.env`, never committed

## Logging

- **File Logging**: Timestamped log files in `logs/`
- **Console Logging**: Structured output for containers
- **Configurable Levels**: Set via `logging.logging_level` in `config_file.json`
- **GraphQL Logging**: Query and mutation resolvers log via `log_handler`

## Docker Features

### Multi-stage Build
- **Builder stage**: Installs dependencies
- **Production stage**: Minimal runtime image
- **Security**: Non-root user execution
- **Health checks**: Built-in container health monitoring

### Docker Compose
- **Production**: Optimized for deployment
- **Services**: Ready for Redis, PostgreSQL integration (commented in compose file)
- **Volumes**: Persistent log storage

## Development

### Hot Reload

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Testing in GraphiQL

Open http://localhost:8000/graphql to write queries, explore the schema, and view auto-generated type documentation.

### Adding Dependencies

```bash
pip install new-package
pip freeze > requirements.txt
```

## Deployment

1. Update environment variables for production.
2. Disable GraphiQL and introspection in `config_file.json` (`graphiql: false`, `introspection: false`).
3. Build: `docker build -t your-graphql-api:latest .`
4. Deploy: `docker-compose up -d`

Compatible with AWS ECS/Fargate, Google Cloud Run, Azure Container Instances, Heroku, DigitalOcean App Platform, and similar.

## Requirements

- Python 3.12+
- Docker (optional)
- Docker Compose (optional)

## Contributing

This is a template — customize it for your specific needs:

1. Update `config_file.json` and `.env`
2. Copy `example_query.py` / `example_mutation.py` and `example_item.py` as starting points
3. Implement your types and resolvers
4. Add tests
5. Update this README

## License

This template is provided as-is for educational and development purposes.
