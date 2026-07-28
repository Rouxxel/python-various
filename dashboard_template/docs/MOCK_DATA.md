# Mock Data Guide

Structure of mock payloads and how to extend them for development.

## Purpose

Mock data allows the dashboard to run without any external services. It's used for:
- Initial development and UI design
- Testing without credentials
- Demonstrating UI patterns
- Demos and prototypes

## Location

Mock data is stored in `backend/app/mock_data/` as JSON files or Python dictionaries.

## Structure

Mock payloads mirror the Pydantic response models defined in the backend. Each endpoint has a corresponding mock file.

### Example: Overview page

**File**: `backend/app/mock_data/overview.json`

```json
{
  "total_users": 1250,
  "active_users": 342,
  "growth_rate": 0.15,
  "revenue": 45000.00,
  "metrics": [
    {
      "title": "Total Users",
      "value": 1250,
      "trend": 0.15,
      "unit": "users"
    }
  ],
  "charts": {
    "growth_over_time": [
      { "date": "2024-01-01", "value": 1000 },
      { "date": "2024-01-02", "value": 1050 }
    ]
  }
}
```

## Mock data patterns

### KPI groups with mixed units

Demonstrates different value types:

```json
{
  "volume_metrics": {
    "title": "Volume",
    "metrics": [
      { "label": "Today", "value": 150, "unit": "count" },
      { "label": "Week", "value": 1050, "unit": "count" },
      { "label": "Month", "value": 4200, "unit": "count" }
    ]
  },
  "rate_metrics": {
    "title": "Rates",
    "metrics": [
      { "label": "Conversion", "value": 0.035, "unit": "pct" },
      { "label": "Retention", "value": 0.72, "unit": "pct" }
    ]
  },
  "currency_metrics": {
    "title": "Revenue",
    "metrics": [
      { "label": "Today", "value": 1250.00, "unit": "usd" },
      { "label": "Week", "value": 8750.00, "unit": "usd" }
    ]
  }
}
```

### Empty states

Demonstrates zero-traffic scenarios:

```json
{
  "total_users": 0,
  "active_users": 0,
  "growth_rate": 0.0,
  "notes": [
    "No data available for this time range",
    "Configure your data source to see live data"
  ]
}
```

### Notes banners

Informational messages for setup instructions:

```json
{
  "metrics": [],
  "notes": [
    "Vercel analytics not configured",
    "Set FEATURE_VERCEL=true and add VERCEL_PROJECT_ID to enable"
  ]
}
```

## How backend serves mock data

### Data source factory

**File**: `backend/app/services/data_source.py`

```python
def get_data_source():
    if settings.dashboard_data_mode == "mock":
        return MockDataSource()
    else:
        return LiveDataSource()

class MockDataSource:
    def get_overview(self, from_date, to_date):
        # Load from mock_data/overview.json
        return load_mock_json("overview.json")
```

### Mock data loading

```python
import json
from pathlib import Path

MOCK_DATA_DIR = Path(__file__).parent.parent / "mock_data"

def load_mock_json(filename):
    path = MOCK_DATA_DIR / filename
    with open(path) as f:
        return json.load(f)
```

## Extending mock data

### Adding mock data for a new endpoint

1. **Create mock file** in `backend/app/mock_data/`
   ```json
   // backend/app/mock_data/my_endpoint.json
   {
     "metric": "example",
     "value": 100
   }
   ```

2. **Add loading method** in `MockDataSource`
   ```python
   class MockDataSource:
       def get_my_endpoint(self, from_date, to_date):
           return load_mock_json("my_endpoint.json")
   ```

3. **Ensure it matches Pydantic model**
   ```python
   class MyEndpointResponse(BaseModel):
       metric: str
       value: float
   ```

### Dynamic mock data

For time-sensitive mock data, use Python functions:

```python
def get_dynamic_mock(from_date, to_date):
    days = (to_date - from_date).days
    return {
        "value": days * 10,
        "date_range": f"{from_date} to {to_date}"
    }
```

## Mock data best practices

### Realistic values

- Use realistic ranges for your domain
- Include edge cases (zero values, very high values)
- Match expected data types (int, float, string)

### Consistent structure

- Match Pydantic models exactly
- Use consistent date formats (ISO 8601)
- Include all required fields

### Documentation

Add comments explaining the mock scenario:

```json
{
  "_comment": "Mock data for healthy production scenario",
  "total_users": 1250,
  "active_users": 342
}
```

### Multiple scenarios

Create separate files for different scenarios:

```
mock_data/
├── overview.json           # Normal scenario
├── overview_empty.json     # Zero traffic
├── overview_error.json    # Error state
└── overview_spike.json     # Traffic spike
```

## Frontend mock data

**File**: `frontend/src/lib/mock-data.ts`

Frontend also has mock data for development without backend:

```typescript
export const mockOverviewData = {
    total_users: 1250,
    active_users: 342,
    // ...
}
```

### When to use frontend vs backend mock

- **Backend mock**: Preferred, single source of truth
- **Frontend mock**: Fallback when backend is unavailable (dev only)

### Frontend mock fallback

```typescript
export async function fetchOverview() {
    try {
        const response = await fetch(`${API_URL}/api/overview`)
        return response.json()
    } catch (error) {
        // Fallback to frontend mock in dev
        if (import.meta.env.DEV) {
            return mockOverviewData
        }
        throw error
    }
}
```

## Testing with mock data

### Backend tests

```python
def test_overview_mock_mode():
    settings.dashboard_data_mode = "mock"
    data_source = get_data_source()
    result = data_source.get_overview(from_date, to_date)
    assert result.total_users > 0
```

### Frontend tests

```typescript
test('renders overview with mock data', () => {
    render(<OverviewPage />)
    expect(screen.getByText('Total Users')).toBeInTheDocument()
})
```

## Switching between mock and live

### Backend

```bash
# In backend/.env
DASHBOARD_DATA_MODE=mock  # Use mock data
DASHBOARD_DATA_MODE=live  # Use live data
```

### Frontend detection

The frontend can detect the mode via API response header:

```typescript
const response = await fetch(`${API_URL}/api/overview`)
const dataMode = response.headers.get('X-Data-Mode')
// "mock" or "live"
```

Display a banner in dev mode:

```typescript
{dataMode === 'mock' && (
    <div className="dev-banner">Mock data mode</div>
)}
```

## Common issues

### Mock data not loading

- Check file path in `load_mock_json()`
- Verify JSON is valid (use JSON linter)
- Ensure file exists in `backend/app/mock_data/`

### Type mismatches

- Compare mock JSON with Pydantic model
- Check field names match exactly
- Verify data types (string vs number)

### Frontend showing wrong data

- Clear browser cache
- Check `VITE_DASHBOARD_API_URL` is correct
- Verify backend is returning mock data
