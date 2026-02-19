# Popup Template

A minimal Chrome extension (Manifest V3) that opens a **popup** when you click the toolbar icon. Default UI: logo and a click counter. Optional backend connectivity.

## Features

- **Manifest V3** with popup action
- **Vanilla HTML, CSS, and JavaScript** – no build step
- **Click counter** – persisted in `chrome.storage.local` so it survives closing the popup
- **Optional backend** – set a base URL to show a "Ping backend" button and example `fetch` usage

## Project Structure

```
popup_template/
├── manifest.json     # MV3: action.default_popup, storage, background
├── popup.html        # Popup UI: logo, count display, Count button
├── popup.css         # Minimal styling
├── popup.js          # Counter logic + optional backend ping
├── background.js     # Service worker (minimal; extend as needed)
├── assets/
│   └── icon.png      # Extension icon (replace with your own)
└── README.md
```

## Quick Start

1. **Copy** this folder into your project (or use it as the project root).
2. **Load in Chrome**:
   - Open `chrome://extensions/`
   - Turn on **Developer mode**
   - Click **Load unpacked**
   - Select the `popup_template` folder
3. Click the extension icon in the toolbar to open the popup. Use **Count** to increment; the value is saved across opens.

## Connecting to a Backend

To call your own API (e.g. REST) from the popup:

1. **Add host permissions** in `manifest.json`:
   ```json
   "host_permissions": ["http://localhost:8000/*"]
   ```
   Adjust the origin to match your backend.

2. **Set the API base URL** in one of two ways:
   - In `popup.js`, set `BACKEND_BASE_URL = 'http://localhost:8000'` (or leave empty to hide the backend section), or
   - At runtime: open the popup, open DevTools (right‑click popup → Inspect), then in the console run:
     ```js
     chrome.storage.local.set({ backendBaseUrl: 'http://localhost:8000' });
     ```
     Reload the popup; the "Ping backend" section will appear.

3. **Use the example**: The "Ping backend" button sends `GET {baseUrl}/health`. Implement a `/health` (or similar) endpoint on your backend, or change the path in `popup.js` (`base + '/health'`) to match your API.

4. **Add your own API calls**: Use `fetch()` from `popup.js` the same way as the ping example. Use `getBackendBase()` (or read `backendBaseUrl` from storage) to build full URLs.

## Customization

- **Name and description**: Edit `manifest.json` (`name`, `description`, `action.default_title`).
- **Icons**: Replace `assets/icon.png` with your own; use 16×16, 48×48, and 128×128 for best results (or one 48×48/128×128 and reference it for all sizes as in the template).
- **UI**: Edit `popup.html`, `popup.css`, and `popup.js` to build your popup UI and logic.

## Requirements

- Google Chrome (or Chromium) with Manifest V3 support.
