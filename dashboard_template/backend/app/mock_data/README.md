# Mock Data

JSON payloads for **mock mode** (`DASHBOARD_DATA_MODE=mock`). No external services required.

## Configuration

File names and directory are centralized in `app/core_specs/configuration/config_file.json`:

```json
{
  "defaults": { "mock_data_path": "app/mock_data" },
  "mock_data": {
    "overview": "overview.json",
    "users": "users.json"
  }
}
```

`MockDataSource` loads files via `app/utils/secure_file_io.read_json` (path-confined reads).

## Files

| File | Used by |
|------|---------|
| `overview.json` | `/api/overview` |
| `users.json` | `/api/users` |
| `sessions.json` | `/api/sessions` |
| `activity.json` | `/api/activity` |
| `infrastructure.json` | `/api/infrastructure` |
| `costs.json` | `/api/costs` |
| `ai_metrics.json` | `/api/ai` |

## Adding mock data for a new endpoint

1. Add a JSON file in this directory.
2. Register the mapping under `"mock_data"` in `config_file.json`.
3. Add a loader method on `MockDataSource` in `app/services/data_source.py`.
4. Match the shape expected by the frontend types in `frontend/src/lib/api.ts`.

## Notes

- Include realistic values and empty-state examples where useful.
- Keep structures aligned with live-mode builders in `app/services/live/`.
