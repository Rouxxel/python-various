# C# REST API Template

A production-ready **ASP.NET Core 8** REST API template with config-driven endpoints and rate limits, CoreSpecs JSON, secure utility helpers, OpenAPI, Docker, and reference CRUD layers.

## Features

- ASP.NET Core controllers, OpenAPI JSON, and development Swagger UI.
- Central `CoreSpecs` JSON for network binding, logging, email policy, static data, endpoint paths, tags, and limits.
- Per-endpoint fixed-window rate limiting by client IP.
- Uniform JSON errors for 400, 404, 429, and 500 responses.
- Create/Update/Response DTO separation, service/repository layers, and a thread-safe in-memory example store.
- Configured custom file/console logger, validators, secure file I/O, RSA key generation, Docker, and xUnit tests.

## Quick start

```powershell
cd templates/csharp_rest_api_template
Copy-Item .env.example .env
dotnet restore RestApiTemplate.sln
dotnet run --project src/RestApiTemplate
```

Requirements: .NET SDK 8+ and the matching **x64 ASP.NET Core 8 runtime**. Docker Desktop is optional for containers.

Once running:

- API root: `http://localhost:8080/`
- Health: `http://localhost:8080/health`
- Swagger UI (Development): `http://localhost:8080/docs`
- OpenAPI JSON (Development): `http://localhost:8080/api-docs/v1.json`

The helper scripts offer the same workflows:

```powershell
./start.ps1 dev
./start.ps1 test
./start.ps1 release
./start.ps1 docker
```

```sh
./start.sh dev
./start.sh test
```

## Project structure

```text
src/RestApiTemplate/
├── Configuration/       # CoreSpecs bridge, rate-limit attribute, utility startup
├── Controllers/         # Root plus one folder per endpoint group
├── CoreSpecs/           # Typed JSON loaders/models
├── DTOs/ Entities/      # API contracts and persisted representation
├── Errors/ Middleware/  # Uniform JSON errors and rate limiting
├── Repositories/        # Persistence abstraction + in-memory reference store
├── Services/            # Business logic
├── Utils/               # Adapted helpers from cs_various_utils
└── Resources/CoreSpecs/ # config_file.json and general_data.json
tests/RestApiTemplate.Tests/
```

## CoreSpecs configuration

`src/RestApiTemplate/Resources/CoreSpecs/Configuration/config_file.json` is loaded once before the host is built. It controls:

| Section | Responsibility |
|---|---|
| `network` | Host, bound port, optional context-path value |
| `logging` | Custom logger level, directory, and filename prefix |
| `email_validation` | Allowed providers and TLDs for `Validators` |
| `endpoints` | Prefix, route, OpenAPI tag, request limit, and time unit |
| `defaults` | Location of static `general_data.json` |

Example endpoint specification:

```json
"example_endpoint_1": {
  "request_limit": 10,
  "unit_of_time_for_limit": "m",
  "endpoint_prefix": "/subsection",
  "endpoint_tag": "example-items",
  "endpoint_route": "/items"
}
```

The template uses the endpoint key in three places: `Program.cs` builds the conventional route from `endpoint_prefix` plus `endpoint_route`; Swagger tags are derived from `endpoint_tag`; and `RateLimit("example_endpoint_1")` resolves the configured limit. Units are `s`, `m`, `h`, and `d`.

`general_data.json` is static, non-environment-specific reference data. The example item list logs its configured supported languages through `DataLoader`.

## Example API

| Method | Path | Description |
|---|---|---|
| GET | `/` | Root health response |
| GET | `/health` | ASP.NET health-check response |
| GET | `/subsection/items` | List example items |
| POST | `/subsection/items` | Create an item; optional `contactEmail` query value |
| GET | `/subsection/items/{id}` | Get one item |
| PATCH | `/subsection/items/{id}` | Partial update |
| DELETE | `/subsection/items/{id}` | Delete an item |
| GET | `/subsection/status` | Second endpoint-group example |

## Adding an endpoint group

1. Add a uniquely named entry under `endpoints` in `config_file.json`.
2. Add a controller in its own `Controllers/<Group>/` folder.
3. Add `RateLimit("your_endpoint_key")` to every handler.
4. Register config-derived conventional route mappings in `Program.cs` using the new prefix and route values.
5. Add Create/Update/Response DTOs and, when persistence is required, entity, repository, and service classes.
6. Add integration tests for success, validation, not-found, and configured rate-limit behavior.

## Layers and utilities

- `DTOs`: request and response contracts; do not expose storage models directly.
- `Entities`: full persisted shape including server-controlled IDs.
- `Services`: business rules, ID generation, mapping, and not-found behavior.
- `Repositories`: swap `InMemoryExampleItemRepository` for EF Core, `SecureFileIo`, or another store.

The `Utils/` files are copied and namespace-adapted from the repository's `cs_various_utils/` folder. `UtilityStartup` configures `CustomLogger`, `Validators`, and `SecureFileIo` from CoreSpecs. Application code uses `CustomLogger`; ASP.NET Core framework diagnostics retain their built-in logger.

`SecureFileIo` is confined to `Resources/`. Its YAML helpers are optional and require the consuming project to add `YamlDotNet`.

Generate development RSA keys only when an API feature needs them:

```powershell
dotnet run --project src/RestApiTemplate -- --generate-rsa-keys
```

The generated PEM files are ignored. The supplied C# utilities do not include an encryption helper; add a reviewed RSA OAEP-SHA256 implementation only when an API contract requires encrypted fields.

## Errors, logging, and scaling

Errors use `{ status, error, detail }`. The rate limiter is correct for a single instance; replace its in-memory counter with Redis or a distributed limiter for multiple instances. Replace the example repository with EF Core/JPA-style persistence and add migrations under `Resources/Db/Migrations` when needed.

At startup, `CustomLogger.Setup` creates `logs/<log_file_name>_<timestamp>.log`, writes startup entries, and receives application messages. `ApplicationStopping` flushes and closes the writer. Configure it with the `logging` CoreSpecs section; never commit logs or secrets.

## Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Compose publishes `${HOST_PORT:-8080}:8080` and mounts `./logs`. The image builds/tests/publishes with the .NET 8 SDK, runs as a non-root user, and checks `/health`. The compose file includes commented PostgreSQL and Redis extension points.

## Tests and release checks

```powershell
dotnet build RestApiTemplate.sln
dotnet test RestApiTemplate.sln
dotnet publish src/RestApiTemplate --configuration Release --output ./publish
```

The suite covers CoreSpecs loading, utility configuration and path protection, rate limiting, CRUD services, and HTTP 200/201/400/404/429/500 responses.

## Environment variables

`.env` is used by Docker Compose and local tooling. `HOST_PORT` publishes the container port; `API_TITLE`, `API_VERSION`, and `API_DESCRIPTION` set OpenAPI metadata. The actual bound application host/port remain controlled by `CoreSpecs.network`.

## License

Provided as-is for educational and development purposes.
