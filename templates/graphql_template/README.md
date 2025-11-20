# GraphQL API Template

A production-ready GraphQL API template built with FastAPI and Strawberry GraphQL, featuring Docker support, rate limiting, logging, and security features.

## 🚀 Features

- **Strawberry GraphQL**: Modern, type-safe GraphQL library for Python
- **FastAPI Integration**: Seamless integration with FastAPI
- **Docker Support**: Multi-stage Dockerfile and docker-compose for easy deployment
- **Rate Limiting**: Built-in request rate limiting with SlowAPI
- **Comprehensive Logging**: File and console logging with configurable levels
- **Security**: Non-root user in Docker, input validation, encryption utilities
- **Configuration**: JSON-based configuration management
- **Health Checks**: Built-in health check endpoints
- **Development Ready**: Hot reload support and GraphiQL interface
- **Type Safety**: Full type safety with Python type hints and Strawberry

## 📁 Project Structure

```
graphql_template/
├── src/
│   ├── graphql_schema/        # GraphQL schema definition
│   │   └── schema.py         # Main schema combining queries/mutations
│   ├── resolvers/            # GraphQL resolvers
│   │   ├── query.py         # Query resolvers
│   │   └── mutation.py      # Mutation resolvers
│   ├── types/               # GraphQL type definitions
│   │   ├── user.py         # User type and inputs
│   │   └── post.py         # Post type and inputs
│   ├── core_specs/         # Core configuration and data
│   │   ├── configuration/  # JSON config files and loaders
│   │   └── data/          # Data files and loaders
│   └── utils/             # Utility modules
│       ├── custom_logger.py  # Logging configuration
│       ├── limiter.py        # Rate limiting setup
│       └── request_limiter.py # Rate limit handlers
├── logs/                  # Log files (created automatically)
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── DOCKERFILE           # Docker build configuration
├── docker-compose.yml   # Docker compose configuration
├── .env                # Environment variables template
├── .dockerignore       # Docker ignore file
└── README.md           # This file
```

## 🛠️ Quick Start

### Option 1: Run with Python (Development)

1. **Clone and setup**:
   ```bash
   cd templates/graphql_template
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env .env.local
   # Edit .env.local with your configuration
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Access the API**:
   - GraphQL Endpoint: http://localhost:8000/graphql
   - GraphiQL Interface: http://localhost:8000/graphql
   - Health Check: http://localhost:8000/health

### Option 2: Run with Docker (Production)

1. **Build and run with Docker Compose**:
   ```bash
   cd templates/graphql_template
   docker-compose up --build
   ```

2. **Or build and run manually**:
   ```bash
   docker build -t graphql-api-template .
   docker run -p 8000:8000 --env-file .env graphql-api-template
   ```

### Option 3: Use Startup Scripts

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```cmd
start.bat
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Server Configuration
SERVER_PORT=8000
HOST=0.0.0.0
RELOAD=false
WORKERS=1

# API Configuration
API_TITLE=GraphQL API Template
API_VERSION=1.0.0
API_DESCRIPTION=A template for building GraphQL APIs

# GraphQL Configuration
GRAPHQL_ENDPOINT=/graphql
GRAPHIQL_ENABLED=true
INTROSPECTION_ENABLED=true
```

### JSON Configuration (src/core_specs/configuration/config_file.json)

The template uses JSON-based configuration for:
- Network settings (host, port, workers)
- GraphQL settings (endpoint, GraphiQL, rate limits)
- Logging settings
- Email validation rules

## 📝 GraphQL Schema

### Sample Queries

```graphql
# Get all users
query {
  users {
    id
    name
    email
    age
    active
    posts {
      id
      title
      published
    }
  }
}

# Get a specific user
query {
  user(id: 1) {
    id
    name
    email
    posts {
      id
      title
      content
      published
      createdAt
    }
  }
}

# Get all published posts
query {
  posts(publishedOnly: true) {
    id
    title
    content
    author {
      name
      email
    }
    createdAt
  }
}
```

### Sample Mutations

```graphql
# Create a new user
mutation {
  createUser(input: {
    name: "Alice Johnson"
    email: "alice@example.com"
    age: 28
    active: true
  }) {
    id
    name
    email
    age
    active
  }
}

# Update a user
mutation {
  updateUser(id: 1, input: {
    name: "John Updated"
    age: 31
  }) {
    id
    name
    age
  }
}

# Create a new post
mutation {
  createPost(input: {
    title: "My New Post"
    content: "This is the content of my new post"
    authorId: 1
    published: true
  }) {
    id
    title
    content
    published
    author {
      name
    }
  }
}
```

## 🔧 Adding New Types and Resolvers

### 1. Create a New Type

```python
# src/types/comment.py
import strawberry
from typing import Optional
from datetime import datetime

@strawberry.type
class Comment:
    id: int
    content: str
    post_id: int
    author_id: int
    created_at: datetime

@strawberry.input
class CommentInput:
    content: str
    post_id: int
    author_id: int
```

### 2. Add Resolvers

```python
# In src/resolvers/query.py
@strawberry.field
def comments(self, post_id: Optional[int] = None) -> List[Comment]:
    # Your resolver logic here
    pass

# In src/resolvers/mutation.py
@strawberry.field
def create_comment(self, input: CommentInput) -> Comment:
    # Your mutation logic here
    pass
```

### 3. Update Schema

The schema automatically includes all resolvers from Query and Mutation classes.

## 🔒 Security Features

- **Rate Limiting**: Configurable per-endpoint rate limiting
- **Input Validation**: Strawberry provides automatic input validation
- **Type Safety**: Full type safety with Python type hints
- **Non-root Docker**: Container runs as non-root user
- **Environment Variables**: Sensitive data via environment variables

## 📊 Logging

The template includes comprehensive logging:
- **File Logging**: Timestamped log files in `logs/` directory
- **Console Logging**: Structured output for containers
- **Configurable Levels**: Debug, Info, Warning, Error, Critical
- **GraphQL Logging**: Automatic query and mutation logging

## 🐳 Docker Features

### Multi-stage Build
- **Builder stage**: Installs dependencies
- **Production stage**: Minimal runtime image
- **Security**: Non-root user execution
- **Health checks**: Built-in container health monitoring

### Docker Compose
- **Development**: Hot reload support (commented)
- **Production**: Optimized for deployment
- **Services**: Ready for Redis, PostgreSQL integration
- **Volumes**: Persistent log storage

## 🧪 Development

### Hot Reload Development
```bash
# Enable hot reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Adding Dependencies
```bash
pip install new-package
pip freeze > requirements.txt
```

### Testing GraphQL Queries
Use the GraphiQL interface at http://localhost:8000/graphql to:
- Write and test queries
- Explore the schema
- View documentation
- Debug queries

## 🚀 Deployment

### Production Deployment
1. **Update environment variables** for production
2. **Disable GraphiQL and introspection** in production
3. **Build production image**:
   ```bash
   docker build -t your-graphql-api:latest .
   ```
4. **Deploy with docker-compose**:
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

### Cloud Deployment
The template is ready for deployment on:
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**
- **Heroku**
- **DigitalOcean App Platform**

## 📚 GraphQL Documentation

Once running, access interactive GraphQL documentation:
- **GraphiQL Interface**: http://localhost:8000/graphql
- **Schema Introspection**: Available via GraphiQL
- **Type Documentation**: Auto-generated from Python types

## 🔧 Customization

### Changing the API Configuration
Update in `main.py`:
```python
app = FastAPI(
    title="Your GraphQL API",
    description="Your API Description",
    version="1.0.0"
)
```

### Adding Database Support
1. Uncomment database service in `docker-compose.yml`
2. Add database dependencies to `requirements.txt`
3. Create database connection utilities in `src/utils/`
4. Update resolvers to use database instead of sample data

### Adding Authentication
1. Install authentication dependencies
2. Create auth utilities in `src/utils/`
3. Add authentication context to GraphQL
4. Protect resolvers with authentication checks

## 📋 Requirements

- Python 3.12+
- Docker (optional)
- Docker Compose (optional)

## 🤝 Contributing

This is a template - customize it for your specific needs:
1. Update configuration files
2. Add your business logic
3. Implement your types and resolvers
4. Add tests
5. Update documentation

## 📄 License

This template is provided as-is for educational and development purposes.

---

**Ready to build your GraphQL API!** 🚀

Start by exploring the sample queries in GraphiQL and customizing the types and resolvers in the `src/` directory.