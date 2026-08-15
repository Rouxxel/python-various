import { DeckPlayer, tracksFromFiles } from "..";
// Remember to import the stylesheet once in your app:
// import "../styles.css";

/**
 * EXAMPLE 1 — static files you serve yourself.
 * Put your mp3s in /public/music/ and list them here.
 */
const LOCAL = tracksFromFiles(
  ["track-one.mp3", "track-two.mp3", "track-three.mp3"],
  "/music",
);

export function LocalExample() {
  return <DeckPlayer source={{ tracks: LOCAL }} brand="MY LABEL" model="RX-01" />;
}

/**
 * EXAMPLE 2 — backend-driven playlist with a local fallback.
 * The player calls GET {apiBaseUrl}/api/v1/media/tracks and streams each
 * track from /api/v1/media/tracks/{id}/stream unless the DTO supplies
 * its own `streamUrl`.
 */
export function BackendExample() {
  return (
    <DeckPlayer
      source={{
        apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? "",
        tracks: LOCAL, // used when apiBaseUrl is empty or the list is empty
      }}
      brand="Y2K PROTOCOL"
      model="DECK-v1.0"
      footerLeft="STEREO"
      footerRight="48kHz"
    />
  );
}

/**
 * EXAMPLE 3 — authenticated backend.
 */
export function AuthedExample({ token }: { token: string }) {
  return (
    <DeckPlayer
      source={{
        apiBaseUrl: "https://api.example.com",
        listPath: "/v2/playlist",
        streamPath: (id) => `/v2/playlist/${id}/audio`,
        headers: { Authorization: `Bearer ${token}` },
      }}
    />
  );
}
