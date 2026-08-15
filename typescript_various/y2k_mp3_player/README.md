# Y2K MP3 PLAYER — portable drop-in component

A fully functional, self-contained Y2K / early-2000s **car-deck & Winamp style
MP3 player** for React. Copy this one folder into any React + TypeScript project
and you have a working hardware-look audio deck: stamped chrome chassis, corner
rivets, pixel/LCD typography, a live spectrum analyser, L/R VU meters, a rotary
volume knob with a real mechanical travel limit, and physical press-down keys.

---

## 1. What's in the box

```text
y2k_mp3_player/
├── README.md                    this file
├── index.ts                     public barrel export
├── styles.css                   ALL visuals — plain CSS, no Tailwind needed
├── components/
│   ├── DeckPlayer.tsx           the whole unit (chassis, LCD, meters, keys)
│   └── VolumeKnob.tsx           rotary knob, -135°..+135° hard limit
├── hooks/
│   ├── useAudioPlayer.ts        audio element + Web Audio analyser graph
│   └── usePlaylist.ts           async playlist loading (loading/error/reload)
├── lib/
│   ├── types.ts                 Track, TrackDto, PlayerSource
│   ├── media.ts                 backend adapter + helpers
│   └── formatTime.ts            MM:SS formatter
└── example/
    └── Usage.tsx                three copy-paste integration examples
```

### Requirements

- **React 18 or 19** (hooks only, no other runtime dependency)
- **TypeScript** (or strip the types — the code is plain TSX)
- Any bundler that can import a `.css` file (Vite, Next, CRA, Remix, Parcel…)

Explicitly **not** required: Tailwind, a design-token system, a CSS framework,
`styled-components`, or an audio library. Nothing outside this folder is imported.

### Features

| Feature | Detail |
| --- | --- |
| Play / pause | ► / ❚❚ key, latches visually while playing |
| Stop | ■ resets to 00:00 |
| Prev / next track | ◄◄ restarts the track if past 3 s, otherwise goes back |
| Volume | rotary knob, drag in a circle or arrow keys, hard stops at both ends |
| LCD readout | real elapsed time, total duration, `TRK 03 · TITLE`, LIVE/IDLE |
| Spectrum | 32 bars driven by a real `AnalyserNode` FFT |
| VU meters | independent L / R RMS levels via a `ChannelSplitterNode` |
| Amber sub-display | `VOL 070` and `03/07` track counter |
| Press physics | keys drop 3 px, highlight collapses into an inset shadow |
| Playlist source | static list, backend API, or backend-with-fallback |
| Privacy | nothing is written to localStorage/cookies; state is memory only |

---

## 2. Install it in 3 steps

**Step 1 — copy the folder.** Drop `y2k_mp3_player/` anywhere in your source
tree, e.g. `src/y2k_mp3_player/`.

**Step 2 — import the stylesheet once**, at your app entry point (or in the file
that renders the player):

```ts
import "./y2k_mp3_player/styles.css";
```

**Step 3 — render it.**

```tsx
import { DeckPlayer, tracksFromFiles } from "./y2k_mp3_player";

const TRACKS = tracksFromFiles(["song-a.mp3", "song-b.mp3"], "/music");

export default function Page() {
  return <DeckPlayer source={{ tracks: TRACKS }} />;
}
```

Put `song-a.mp3` / `song-b.mp3` in your `public/music/` directory (or wherever
`/music` resolves to on your server). Done — the deck plays.

> Browsers block autoplay: the Web Audio graph is created on the **first click**
> of the play key. That is expected and required.

---

## 3. Component API

```tsx
<DeckPlayer
  source={{ /* see below */ }}
  brand="Y2K PROTOCOL"        // top-left pixel label
  model="DECK-v1.0"           // top-right pixel label
  footerLeft="ZERO-RETENTION"  // bottom strip left  (null hides the strip)
  footerRight="KEY · YOURS"    // bottom strip right
  initialVolume={0.7}          // 0..1
  className="my-wrapper"       // extra class on the outer element
/>
```

### `source: PlayerSource`

```ts
interface PlayerSource {
  apiBaseUrl?: string;                  // "" or undefined → use `tracks`
  listPath?: string;                    // default "/api/v1/media/tracks"
  streamPath?: (id: string) => string;  // default "/api/v1/media/tracks/{id}/stream"
  headers?: Record<string, string>;     // auth headers for the playlist request
  tracks?: Track[];                     // static list and/or fallback
}
```

```ts
interface Track {
  id: string;
  title: string;
  label: string;          // uppercase, shown on the LCD
  artist?: string;
  durationSeconds?: number;
  src: string;            // resolved audio URL
}
```

---

## 4. Wiring it to a backend

The player is API-driven out of the box. Set `apiBaseUrl` and it switches from
local files to your server with **no component changes**.

```tsx
<DeckPlayer source={{ apiBaseUrl: import.meta.env.VITE_API_BASE_URL }} />
```

### Endpoints to implement

**`GET {apiBaseUrl}{listPath}`** → JSON. Either shape is accepted:

```json
{ "tracks": [
  { "id": "a1", "title": "Cartier Hyperpop", "artist": "JayStacks", "durationSeconds": 184 },
  { "id": "a2", "title": "Space Drip", "streamUrl": "https://cdn.example.com/signed/a2.mp3" }
] }
```

- `id` is the only required field.
- Supply `streamUrl` to stream from a CDN / signed URL and skip your API.
- Omit `streamUrl` and the player requests `{apiBaseUrl}{streamPath(id)}`.

**`GET {apiBaseUrl}{streamPath(id)}`** → the audio bytes. This endpoint must:

1. Send a correct `Content-Type` (`audio/mpeg`, `audio/mp4`, …).
2. **Support HTTP Range requests** (`Accept-Ranges: bytes`, reply `206 Partial
   Content`). Without it, seeking and duration reporting break in Safari.
3. If it is served from a **different origin** than your site, send CORS
   headers — the `<audio>` element uses `crossOrigin="anonymous"`, and without
   CORS the browser silently gives you a **flat spectrum and dead VU meters**:

```http
Access-Control-Allow-Origin: https://your-site.example
Access-Control-Allow-Headers: Range, Authorization
Access-Control-Expose-Headers: Content-Length, Content-Range, Accept-Ranges
```

### Storing audio in a database

Keep the metadata row (id, title, artist, duration) and the blob separately or
together; the frontend never cares. The stream handler just needs to read the
blob, honour the `Range` header, and pipe bytes. Example (ASP.NET Core):

```csharp
[HttpGet("/api/v1/media/tracks/{id}/stream")]
public IActionResult Stream(string id)
{
    var track = _db.Tracks.Find(id);
    if (track is null) return NotFound();
    // enableRangeProcessing gives you 206 + seeking for free
    return File(new MemoryStream(track.Audio), "audio/mpeg", enableRangeProcessing: true);
}
```

### Loading / error behaviour

- While fetching, the LCD shows `LOADING PLAYLIST…` and keys are disabled.
- On failure it shows `ERR · <MESSAGE>` and the **play key becomes a retry
  button** (it calls `reload()`).
- If the API returns an empty list and you passed `source.tracks`, the fallback
  list is used instead of erroring.

### Using the hooks directly

Want your own chassis? Skip `DeckPlayer` and use the engine:

```tsx
const { tracks, loading, error, reload } = usePlaylist({ apiBaseUrl });
const p = useAudioPlayer(tracks);
// p.playing, p.currentTime, p.duration, p.volume, p.setVolume,
// p.toggle, p.stop, p.prev, p.next, p.seekBy, p.read(bars)
```

`p.read(bars)` returns `{ spectrum: number[], l: number, r: number }` (all
values 0..1) or `null` when the graph isn't running yet — call it inside a
`requestAnimationFrame` loop and write straight to DOM styles, as `DeckPlayer`
does, to avoid re-rendering React 60 times a second.

---

## 5. Re-skinning it

Every colour and font lives in CSS custom properties at the top of
`styles.css`, scoped to `.y2k-deck`. Override them from your own CSS:

```css
.y2k-deck {
  --y2k-lcd-cyan: oklch(0.9 0.18 70);   /* amber main LCD */
  --y2k-radius: 8px;                     /* squarer chassis */
  --y2k-font-pixel: "Press Start 2P", monospace;
}
```

- Class names are all `y2k-` prefixed, so nothing collides with your app.
- Fonts are pulled from Google Fonts via the `@import` at the top of
  `styles.css` (Silkscreen, VT323, Orbitron). Delete that line if you self-host
  or already load them.
- Structural pieces you may want to touch: `.y2k-panel-chrome` (the chassis
  gradient), `.y2k-lcd` (screen glass), `.y2k-press` (the press-down physics),
  `.y2k-rivet` (screws), `.y2k-knob*` (the knob).

## 6. Notes & gotchas

- **Client-only.** The audio element is created in `useEffect`, so the component
  is SSR-safe, but the deck only comes alive after hydration.
- **No persistence.** Volume and track position are memory only, by design.
- **`prefers-reduced-motion`** disables the float animation, blink, and bar
  transitions automatically.
- **Responsive.** The unit is fluid up to `max-width: 440px`; change
  `.y2k-deck { max-width }` to make it bigger.
- **License.** The code here is yours to reuse. Audio files are *not* included —
  supply your own royalty-free or licensed tracks.
