import { useCallback, useEffect, useRef, useState } from "react";
import type { Track } from "../lib/types";

/**
 * Drives an <audio> element plus a Web Audio graph for spectrum + L/R levels.
 * Presentation only — no persistence, no storage writes.
 */
export function useAudioPlayer(tracks: Track[], initialVolume = 0.7) {
  const tracksRef = useRef(tracks);
  tracksRef.current = tracks;
  const count = tracks.length;

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const ctxRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const leftRef = useRef<AnalyserNode | null>(null);
  const rightRef = useRef<AnalyserNode | null>(null);
  const gainRef = useRef<GainNode | null>(null);

  const [trackIndex, setTrackIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(initialVolume);

  // Create the audio element (client only).
  useEffect(() => {
    const el = new Audio();
    el.preload = "metadata";
    el.crossOrigin = "anonymous";
    el.volume = 1;
    audioRef.current = el;

    const onTime = () => setCurrentTime(el.currentTime);
    const onMeta = () => setDuration(el.duration || 0);
    const onEnd = () =>
      setTrackIndex((i) =>
        tracksRef.current.length ? (i + 1) % tracksRef.current.length : 0,
      );
    const onPlay = () => setPlaying(true);
    const onPause = () => setPlaying(false);

    el.addEventListener("timeupdate", onTime);
    el.addEventListener("loadedmetadata", onMeta);
    el.addEventListener("ended", onEnd);
    el.addEventListener("play", onPlay);
    el.addEventListener("pause", onPause);

    return () => {
      el.pause();
      el.removeEventListener("timeupdate", onTime);
      el.removeEventListener("loadedmetadata", onMeta);
      el.removeEventListener("ended", onEnd);
      el.removeEventListener("play", onPlay);
      el.removeEventListener("pause", onPause);
      audioRef.current = null;
      ctxRef.current?.close().catch(() => {});
      ctxRef.current = null;
    };
  }, []);

  /** Lazily build the Web Audio graph on first play (autoplay policy). */
  const ensureGraph = useCallback(() => {
    const el = audioRef.current;
    if (!el || ctxRef.current) return;
    const AC: typeof AudioContext =
      window.AudioContext ??
      (window as unknown as { webkitAudioContext: typeof AudioContext })
        .webkitAudioContext;
    if (!AC) return;

    const ctx = new AC();
    const source = ctx.createMediaElementSource(el);
    const gain = ctx.createGain();
    gain.gain.value = volume;

    const analyser = ctx.createAnalyser();
    analyser.fftSize = 128;
    analyser.smoothingTimeConstant = 0.75;

    const splitter = ctx.createChannelSplitter(2);
    const left = ctx.createAnalyser();
    const right = ctx.createAnalyser();
    left.fftSize = 256;
    right.fftSize = 256;

    source.connect(gain);
    gain.connect(analyser);
    gain.connect(splitter);
    splitter.connect(left, 0);
    splitter.connect(right, 1);
    gain.connect(ctx.destination);

    ctxRef.current = ctx;
    gainRef.current = gain;
    analyserRef.current = analyser;
    leftRef.current = left;
    rightRef.current = right;
  }, [volume]);

  // Load a new track when the index (or playlist) changes.
  const firstLoad = useRef(true);
  useEffect(() => {
    const el = audioRef.current;
    if (!el) return;
    const t = tracks[trackIndex];
    if (!t) return;
    el.src = t.src;
    setCurrentTime(0);
    setDuration(0);
    if (firstLoad.current) {
      firstLoad.current = false;
      return;
    }
    if (playing) void el.play().catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [trackIndex, tracks]);

  // Keep the index valid when the playlist changes (e.g. backend reload).
  useEffect(() => {
    setTrackIndex((i) => (count === 0 ? 0 : Math.min(i, count - 1)));
  }, [count]);

  useEffect(() => {
    if (gainRef.current) gainRef.current.gain.value = volume;
    const el = audioRef.current;
    if (el && !gainRef.current) el.volume = volume; // graph-less fallback
  }, [volume]);

  const play = useCallback(async () => {
    const el = audioRef.current;
    if (!el) return;
    ensureGraph();
    await ctxRef.current?.resume().catch(() => {});
    try {
      await el.play();
    } catch {
      /* autoplay blocked */
    }
  }, [ensureGraph]);

  const toggle = useCallback(() => {
    const el = audioRef.current;
    if (!el) return;
    if (el.paused) void play();
    else el.pause();
  }, [play]);

  const stop = useCallback(() => {
    const el = audioRef.current;
    if (!el) return;
    el.pause();
    el.currentTime = 0;
    setCurrentTime(0);
  }, []);

  const seekBy = useCallback((delta: number) => {
    const el = audioRef.current;
    if (!el) return;
    const next = Math.min(
      Math.max(0, el.currentTime + delta),
      el.duration || Number.MAX_SAFE_INTEGER,
    );
    el.currentTime = next;
    setCurrentTime(next);
  }, []);

  const prev = useCallback(() => {
    const el = audioRef.current;
    if (el && el.currentTime > 3) {
      el.currentTime = 0;
      setCurrentTime(0);
      return;
    }
    setTrackIndex((i) =>
      tracksRef.current.length
        ? (i - 1 + tracksRef.current.length) % tracksRef.current.length
        : 0,
    );
  }, []);

  const next = useCallback(() => {
    setTrackIndex((i) =>
      tracksRef.current.length ? (i + 1) % tracksRef.current.length : 0,
    );
  }, []);

  /** Read live analyser data. Returns null when the graph isn't running. */
  const read = useCallback((bars: number) => {
    const analyser = analyserRef.current;
    if (!analyser) return null;

    const freq = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(freq);
    const spectrum: number[] = [];
    const per = Math.max(1, Math.floor(freq.length / bars));
    for (let i = 0; i < bars; i++) {
      let sum = 0;
      for (let j = 0; j < per; j++) sum += freq[i * per + j] ?? 0;
      spectrum.push(sum / per / 255);
    }

    const rms = (node: AnalyserNode | null) => {
      if (!node) return 0;
      const buf = new Float32Array(node.fftSize);
      node.getFloatTimeDomainData(buf);
      let acc = 0;
      for (let i = 0; i < buf.length; i++) acc += buf[i] * buf[i];
      return Math.min(1, Math.sqrt(acc / buf.length) * 3.2);
    };

    return { spectrum, l: rms(leftRef.current), r: rms(rightRef.current) };
  }, []);

  return {
    track: tracks[trackIndex] ?? null,
    trackIndex,
    trackCount: count,
    playing,
    currentTime,
    duration,
    volume,
    setVolume,
    toggle,
    play,
    stop,
    seekBy,
    prev,
    next,
    read,
  };
}
