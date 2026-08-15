import type { PlayerSource, Track, TrackDto } from "./types";

/**
 * Media API adapter.
 *
 * Backend contract (implement server-side):
 *   GET  {listPath}                 -> { tracks: TrackDto[] }  (or a bare array)
 *   GET  {streamPath(id)}           -> audio/* byte stream
 *
 * Streaming requirements for the analyser (spectrum + VU meters) to work:
 *   - support HTTP Range requests (206 Partial Content)
 *   - send permissive CORS headers when served from another origin:
 *       Access-Control-Allow-Origin: <your site>
 *       Access-Control-Expose-Headers: Content-Length, Content-Range, Accept-Ranges
 *     (the <audio> element uses crossOrigin="anonymous"; without CORS the
 *      Web Audio graph is muted/blocked by the browser)
 */

export const DEFAULT_LIST_PATH = "/api/v1/media/tracks";
export const defaultStreamPath = (id: string) =>
  `/api/v1/media/tracks/${encodeURIComponent(id)}/stream`;

export class MediaError extends Error {
  code: string;
  constructor(code: string, message: string) {
    super(message);
    this.name = "MediaError";
    this.code = code;
  }
}

function labelFrom(dto: TrackDto): string {
  const base = dto.title?.trim() || dto.id;
  return (dto.artist ? `${dto.artist} — ${base}` : base).toUpperCase();
}

/** Map a backend DTO onto the shape the player consumes. */
export function toTrack(dto: TrackDto, source: PlayerSource): Track {
  const stream = source.streamPath ?? defaultStreamPath;
  return {
    id: dto.id,
    title: dto.title ?? dto.id,
    artist: dto.artist,
    label: labelFrom(dto),
    durationSeconds: dto.durationSeconds,
    src: dto.streamUrl ?? `${source.apiBaseUrl ?? ""}${stream(dto.id)}`,
  };
}

/**
 * Fetch the playlist. With no `apiBaseUrl` it resolves to `source.tracks`
 * (or an empty list), so the UI never blocks on a backend during development.
 */
export async function fetchTracks(
  source: PlayerSource,
  signal?: AbortSignal,
): Promise<Track[]> {
  if (!source.apiBaseUrl) return source.tracks ?? [];

  const url = `${source.apiBaseUrl}${source.listPath ?? DEFAULT_LIST_PATH}`;
  const res = await fetch(url, {
    signal,
    headers: { Accept: "application/json", ...(source.headers ?? {}) },
  });
  if (!res.ok) {
    throw new MediaError(`HTTP_${res.status}`, `Playlist request failed (${res.status})`);
  }

  const body = (await res.json()) as { tracks?: TrackDto[] } | TrackDto[];
  const dtos = Array.isArray(body) ? body : (body.tracks ?? []);
  if (!dtos.length) {
    if (source.tracks?.length) return source.tracks;
    throw new MediaError("EMPTY_PLAYLIST", "No tracks returned.");
  }
  return dtos.map((d) => toTrack(d, source));
}

/**
 * Helper to build a static playlist from files you serve yourself
 * (e.g. /public/music/*.mp3).
 */
export function tracksFromFiles(files: string[], baseDir = "/music"): Track[] {
  const toLabel = (file: string) =>
    file
      .replace(/\.[a-z0-9]+$/i, "")
      .replace(/-\d+$/, "")
      .replace(/[-_]/g, " ")
      .toUpperCase();

  return files.map((f) => ({
    id: f.replace(/\.[a-z0-9]+$/i, ""),
    title: toLabel(f),
    label: toLabel(f),
    src: `${baseDir}/${encodeURIComponent(f)}`,
  }));
}
