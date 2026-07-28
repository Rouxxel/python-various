# Cloudflare Pages Deployment

Deploy the frontend to Cloudflare Pages.

## Prerequisites

1. Install Wrangler CLI: `npm install -g wrangler`
2. Build the frontend: `cd frontend && npm run build`

## Deploy

```bash
cd frontend
wrangler pages publish dist
```

## Environment Variables

Set these in Cloudflare Pages dashboard:

```
VITE_DASHBOARD_API_URL=https://your-backend-url.com
```

## Custom Domain

1. Add custom domain in Cloudflare Pages dashboard
2. Update DNS records (Cloudflare handles this automatically)
3. Update `FRONTEND_URL` in backend `.env`

## Git Integration

Connect your GitHub repo to Cloudflare Pages for automatic deployments on push.

## Configuration

For advanced configuration, create `wrangler.toml`:

```toml
name = "analytics-dashboard"
compatibility_date = "2024-01-01"

[env.production]
vars = { ENVIRONMENT = "production" }
```

## Build Settings

In Cloudflare Pages dashboard:
- Build command: `cd frontend && npm run build`
- Build output directory: `frontend/dist`
- Root directory: `/`
