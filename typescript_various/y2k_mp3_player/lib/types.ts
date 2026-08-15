/**
 * Public types for the Y2K MP3 player.
 * Keep `TrackDto` in sync with your backend's JSON shape.
 */

/** Wire shape returned by the playlist endpoint. */
export interface TrackDto {
  id: string;
  title?: string;
  artist?: string;
  /** Total length in seconds, if the backend knows it. */
  durationSeconds?: number;
  /**
   * Optional direct/signed URL. When omitted the client streams from
   * `${apiBaseUrl}${streamPath(id)}`.
   */
  streamUrl?: string;
}

/** Normalised track consumed by the player UI. */
export interface Track {
  id: string;
  title: string;
  artist?: string;
  /** Short LCD-friendly label (uppercase). */
  label: string;
  durationSeconds?: number;
  /** Resolved audio URL. */
  src: string;
}

/** Configuration for loading a playlist from a backend. */
export interface PlayerSource {
  /** e.g. "https://api.example.com" — leave empty to use `tracks` only. */
  apiBaseUrl?: string;
  /** Playlist endpoint path. Default: "/api/v1/media/tracks" */
  listPath?: string;
  /** Stream endpoint builder. Default: `/api/v1/media/tracks/${id}/stream` */
  streamPath?: (id: string) => string;
  /** Extra headers (auth tokens, etc.) for the playlist request. */
  headers?: Record<string, string>;
  /** Static tracks. Used as-is when no `apiBaseUrl` is given, or as fallback. */
  tracks?: Track[];
}
