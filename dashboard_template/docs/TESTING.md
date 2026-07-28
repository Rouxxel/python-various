# Testing Guide

This document describes the testing procedures for the dashboard template.

## Phase 10 Testing Matrix

### 10.1 Mock Mode Testing

**Objective**: Verify all navigation pages load without 500 errors in mock mode.

**Procedure**:
1. Set `DASHBOARD_DATA_MODE=mock` in backend `.env`
2. Start backend: `cd backend && uv run python -m app.server`
3. Start frontend: `cd frontend && npm run dev`
4. Navigate to each route in the sidebar:
   - Overview
   - Metrics
   - Charts
   - Tables
   - Infrastructure
5. Verify each page loads without errors
6. Check browser console for JavaScript errors
7. Check backend logs for API errors

**Expected Result**: All pages load successfully with mock data.

### 10.2 Live Mode Testing

**Objective**: Verify graceful empty states when credentials are missing.

**Procedure**:
1. Set `DASHBOARD_DATA_MODE=live` in backend `.env`
2. Leave provider credentials unset (e.g., SUPABASE_URL not set)
3. Start backend and frontend
4. Navigate to pages that require providers
5. Verify empty states or setup instructions are shown
6. Verify no 500 errors occur

**Expected Result**: Pages show helpful empty states or setup instructions instead of crashing.

### 10.3 Feature Flags Testing

**Objective**: Verify each feature flag's off state is documented and visually clear.

**Procedure**:
1. Test each feature flag individually:
   - `FEATURE_SUPABASE=false`
   - `FEATURE_VERCEL=false`
   - `FEATURE_HOST_HEALTH=false`
   - `FEATURE_STORAGE_METRICS=false`
   - `FEATURE_COSTS_MODULE=false`
2. For each flag:
   - Set to false
   - Restart backend
   - Navigate to relevant pages
   - Verify feature is hidden or shows setup instructions
3. Check documentation for each feature flag

**Expected Result**: All features respect their flags and provide clear guidance when disabled.

### 10.4 Test/Prod Switch Testing

**Objective**: Verify test/prod switch works when `feature_test_prod_switch=true`.

**Procedure**:
1. Set `FEATURE_TEST_PROD_SWITCH=true` in backend `.env`
2. Start backend and frontend
3. Locate environment switcher in UI
4. Toggle between test and production
5. Verify API calls use correct environment

**Expected Result**: Switcher toggles correctly and API calls respect the selected environment.

### 10.5 Frontend Build Testing

**Procedure**:
```bash
cd frontend
npm run build
```

**Expected Result**: Build completes without errors.

### 10.6 Backend Tests

**Procedure**:
```bash
cd backend
uv run pytest -m "not integration"
```

**Expected Result**: All unit tests pass.

## Documentation Review Checklist

### Root README
- [ ] Readable by frontend-only developer
- [ ] Clear setup instructions
- [ ] Links to all relevant documentation
- [ ] Prerequisites clearly stated

### Backend README
- [ ] Readable by backend-only developer
- [ ] API documentation clear
- [ ] Mock vs live mode explained
- [ ] Environment variables documented

### Frontend README
- [ ] Readable without opening backend code
- [ ] Component usage examples
- [ ] Routing documentation
- [ ] Build/deployment instructions

### Routes README
- [ ] Sufficient to add a page without asking questions
- [ ] Route structure explained
- [ ] Component patterns documented
- [ ] Data fetching patterns shown

## Running Tests

### Quick Test (Mock Mode Only)
```bash
# Backend
cd backend
DASHBOARD_DATA_MODE=mock uv run python -m app.server

# Frontend (in another terminal)
cd frontend
npm run dev
```

### Full Test Suite
```bash
# Backend tests
cd backend
uv run pytest

# Frontend build
cd frontend
npm run build
```

### Type Safety Check
```bash
python scripts/type_check.py
```

## Known Limitations

- TypeScript lint errors are expected due to missing component files (template nature)
- Some tests require actual provider credentials (integration tests)
- Frontend build requires all dependencies to be installed
