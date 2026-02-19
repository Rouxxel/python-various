# Chrome Extension Templates

Copy-paste templates for building Chrome extensions (Manifest V3). Each template gives you a minimal, runnable starting point with a default UI and optional backend connectivity.

## Templates

| Template | UI type | Description |
|----------|---------|-------------|
| **[popup_template](popup_template/)** | Popup | Clicking the extension icon opens a popup. Good for quick actions and small UIs. |
| **[sidepanel_template](sidepanel_template/)** | Side panel | Clicking the extension icon opens a side panel that stays open while you browse. Good for tools that need to stay visible. |

Both templates include:

- **Default UI**: A single view with the extension logo and a button that counts clicks (state persisted with `chrome.storage.local`).
- **Optional backend**: Documented steps and example code to connect to your own API (e.g. REST). You can enable `host_permissions`, set an API base URL, and use the included "Ping backend" example.

## How to use

1. **Choose a template**: Copy either `popup_template` or `sidepanel_template` into your project (or use the folder as your project root).
2. **Customize**: Update `manifest.json` (name, description, icons), replace the logo in `assets/`, and extend the UI and logic in `popup.html`, `popup.css`, and `popup.js`.
3. **Load in Chrome**: Open `chrome://extensions/`, turn on **Developer mode**, click **Load unpacked**, and select the template folder.

For Quick Start, project structure, and "Connecting to a backend", see each template’s README:

- [popup_template/README.md](popup_template/README.md)
- [sidepanel_template/README.md](sidepanel_template/README.md)

## Requirements

- Google Chrome (or a Chromium-based browser that supports Manifest V3 and the Extension APIs used).
- No build step: both templates use vanilla HTML, CSS, and JavaScript.
