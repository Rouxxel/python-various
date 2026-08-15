import { useEffect, useMemo, useState } from "react";
import { fetchTracks } from "../lib/media";
import type { PlayerSource, Track } from "../lib/types";

export interface PlaylistState {
  tracks: Track[];
  loading: boolean;
  /** Short, human-readable error suitable for the LCD readout. */
  error: string | null;
  reload: () => void;
}

/**
 * Loads the playlist from the backend (or the static `tracks` fallback).
 * Memory only — nothing is persisted to storage.
 */
export function usePlaylist(source: PlayerSource): PlaylistState {
  const [tracks, setTracks] = useState<Track[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nonce, setNonce] = useState(0);

  // Stable identity so callers can pass an inline object literal.
  const key = useMemo(
    () =>
      JSON.stringify([
        source.apiBaseUrl ?? "",
        source.listPath ?? "",
        source.tracks?.map((t) => t.id) ?? [],
      ]),
    [source.apiBaseUrl, source.listPath, source.tracks],
  );

  useEffect(() => {
    const ac = new AbortController();
    setLoading(true);
    setError(null);
    fetchTracks(source, ac.signal)
      .then((t) => {
        if (ac.signal.aborted) return;
        setTracks(t);
        setLoading(false);
      })
      .catch((e: unknown) => {
        if (ac.signal.aborted) return;
        setTracks([]);
        setError(e instanceof Error ? e.message : "Playlist unavailable.");
        setLoading(false);
      });
    return () => ac.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, nonce]);

  return { tracks, loading, error, reload: () => setNonce((n) => n + 1) };
}
