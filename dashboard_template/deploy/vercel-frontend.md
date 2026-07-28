# Vercel Frontend Deployment

Deploy the frontend to Vercel.

## Prerequisites

1. Install Vercel CLI: `npm i -g vercel`
2. Build the frontend: `cd frontend && npm run build`

## Deploy

```bash
cd frontend
vercel deploy
```

## Environment Variables

Set these in Vercel project settings:

```
VITE_DASHBOARD_API_URL=https://your-backend-url.com
```

## Custom Domain

1. Add custom domain in Vercel dashboard
2. Update DNS records as instructed
3. Update `FRONTEND_URL` in backend `.env`

## Automatic Deployments

Connect your GitHub repo to Vercel for automatic deployments on push.

## Build Configuration

The frontend uses standard Vercel build settings. No `vercel.json` is required for basic deployments.

For advanced configuration, create `frontend/vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install"
}
```
