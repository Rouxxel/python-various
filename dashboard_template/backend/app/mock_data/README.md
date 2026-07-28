# Mock Data

This directory contains mock data files for development and testing without external services.

## Files

- `overview.json` - Overview page metrics and charts
- `users.json` - User analytics data
- `sessions.json` - Session analytics data
- `activity.json` - Activity/events data
- `infrastructure.json` - Infrastructure and hosting metrics
- `costs.json` - Cost tracking data
- `ai_metrics.json` - AI/ML metrics

## Usage

Mock data is automatically loaded when `DASHBOARD_DATA_MODE=mock` in backend/.env.

## Extending

To add mock data for a new endpoint:

1. Create a new JSON file in this directory
2. Structure it to match the Pydantic response model
3. Add a loading method in `MockDataSource` class in `data_source.py`
4. Test with mock mode enabled

## Notes

- Mock data should demonstrate realistic scenarios
- Include edge cases (zero values, empty states)
- Match the exact structure expected by frontend types
- Update this README when adding new files
