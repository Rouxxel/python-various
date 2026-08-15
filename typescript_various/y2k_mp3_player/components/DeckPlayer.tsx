import { useEffect, useRef } from "react";
import { useAudioPlayer } from "../hooks/useAudioPlayer";
import { usePlaylist } from "../hooks/usePlaylist";
import { formatTime } from "../lib/formatTime";
import type { PlayerSource } from "../lib/types";
import { VolumeKnob } from "./VolumeKnob";

const BARS = 32;
const LEDS = 18;

export interface DeckPlayerProps {
  /** Where tracks come from: a backend, a static list, or both. */
  source?: PlayerSource;
  /** Top-left hardware label. */
  brand?: string;
  /** Top-right hardware label (model / version). */
  model?: string;
  /** Bottom strip labels. Pass `null` to hide the strip. */
  footerLeft?: string | null;
  footerRight?: string | null;
  /** Initial volume, 0..1. */
  initialVolume?: number;
  className?: string;
}

/**
 * Y2K car-deck / Winamp style MP3 player.
 * Fully functional: play/pause, stop, prev/next, rotary volume with a
 * mechanical limit, live spectrum + L/R VU meters, LCD time & track readout.
 */
export function DeckPlayer({
  source = {},
  brand = "Y2K PROTOCOL",
  model = "DECK-v1.0",
  footerLeft = "ZERO-RETENTION",
  footerRight = "KEY · YOURS",
  initialVolume = 0.7,
  className,
}: DeckPlayerProps) {
  const { tracks, loading, error, reload } = usePlaylist(source);
  const p = useAudioPlayer(tracks, initialVolume);

  const barsRef = useRef<(HTMLSpanElement | null)[]>([]);
  const ledLRef = useRef<(HTMLSpanElement | null)[]>([]);
  const ledRRef = useRef<(HTMLSpanElement | null)[]>([]);

  const playingRef = useRef(p.playing);
  playingRef.current = p.playing;

  useEffect(() => {
    let raf = 0;
    const paint = () => {
      raf = requestAnimationFrame(paint);
      const data = playingRef.current ? p.read(BARS) : null;

      for (let i = 0; i < BARS; i++) {
        const el = barsRef.current[i];
        if (!el) continue;
        const v = data ? data.spectrum[i] : 0;
        el.style.height = `${8 + v * 92}%`;
        el.style.opacity = data ? String(0.45 + v * 0.55) : "0.3";
      }

      const paintMeter = (arr: (HTMLSpanElement | null)[], level: number) => {
        const lit = Math.round(level * LEDS);
        for (let i = 0; i < LEDS; i++) {
          const el = arr[i];
          if (!el) continue;
          const on = i < lit;
          el.style.background = on
            ? i < LEDS * 0.55
              ? "oklch(0.75 0.2 145)"
              : i < LEDS * 0.8
                ? "oklch(0.85 0.2 90)"
                : "oklch(0.7 0.22 25)"
            : "oklch(0.35 0.05 30)";
          el.style.boxShadow = on
            ? "0 0 4px oklch(0.8 0.2 120 / 0.7), inset 0 1px 0 oklch(1 0 0 / 0.5)"
            : "inset 0 1px 1px oklch(0 0 0 / 0.7)";
        }
      };

      paintMeter(ledLRef.current, data ? data.l : 0);
      paintMeter(ledRRef.current, data ? data.r : 0);
    };
    raf = requestAnimationFrame(paint);
    return () => cancelAnimationFrame(raf);
  }, [p.read]);

  const trackNo = String(p.trackIndex + 1).padStart(2, "0");
  const readout = loading
    ? "LOADING PLAYLIST…"
    : error
      ? `ERR · ${error.toUpperCase()}`
      : p.track
        ? `TRK ${trackNo} · ${p.track.label}`
        : "NO MEDIA";
  const ready = !loading && !error && !!p.track;

  return (
    <div className={`y2k-deck${className ? ` ${className}` : ""}`}>
      <div aria-hidden="true" className="y2k-bloom" />

      <div className="y2k-face y2k-panel-chrome">
        {/* Corner rivets */}
        <span aria-hidden className="y2k-rivet y2k-rivet-tl" />
        <span aria-hidden className="y2k-rivet y2k-rivet-tr" />
        <span aria-hidden className="y2k-rivet y2k-rivet-bl" />
        <span aria-hidden className="y2k-rivet y2k-rivet-br" />

        {/* Brand strip */}
        <div className="y2k-brand">
          <span className="y2k-pixel y2k-brand-left">{brand}</span>
          <span className="y2k-pixel y2k-brand-right">{model}</span>
        </div>

        {/* Main LCD */}
        <div className="y2k-lcd y2k-lcd-main y2k-scanlines y2k-bevel-inner">
          <div className="y2k-lcd-row">
            <span className="y2k-time" aria-label="Elapsed time">
              {formatTime(p.currentTime)}
            </span>
            <span className="y2k-state">
              <span className={p.playing ? "y2k-blink" : undefined}>●</span>{" "}
              {p.playing ? "LIVE" : "IDLE"}
            </span>
          </div>
          <div className="y2k-lcd-meta">
            <span className="y2k-lcd-title">{readout}</span>
            <span>{formatTime(p.duration)}</span>
          </div>

          {/* Spectrum */}
          <div className="y2k-spectrum">
            {Array.from({ length: BARS }).map((_, i) => (
              <span
                key={i}
                className="y2k-bar"
                ref={(el) => {
                  barsRef.current[i] = el;
                }}
              />
            ))}
          </div>
        </div>

        {/* L / R VU meters */}
        <div className="y2k-vu y2k-bevel-inner">
          <div className="y2k-vu-grid">
            <span className="y2k-vu-label">L</span>
            <div className="y2k-vu-row">
              {Array.from({ length: LEDS }).map((_, i) => (
                <span
                  key={i}
                  className="y2k-led"
                  ref={(el) => {
                    ledLRef.current[i] = el;
                  }}
                />
              ))}
            </div>
            <span className="y2k-vu-label">R</span>
            <div className="y2k-vu-row">
              {Array.from({ length: LEDS }).map((_, i) => (
                <span
                  key={i}
                  className="y2k-led"
                  ref={(el) => {
                    ledRRef.current[i] = el;
                  }}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Knob + transport + amber sub-readout */}
        <div className="y2k-controls">
          <VolumeKnob value={p.volume} onChange={p.setVolume} label="Volume" />

          <div className="y2k-transport">
            <TransportKey label="Previous track" onClick={p.prev} disabled={!ready}>
              ◄◄
            </TransportKey>
            <TransportKey label="Stop" onClick={p.stop} disabled={!ready}>
              ■
            </TransportKey>
            <TransportKey
              label={p.playing ? "Pause" : "Play"}
              onClick={error ? reload : p.toggle}
              pressed={p.playing}
              disabled={loading || (!ready && !error)}
            >
              {p.playing ? "❚❚" : "►"}
            </TransportKey>
            <TransportKey label="Next track" onClick={p.next} disabled={!ready}>
              ►►
            </TransportKey>
          </div>

          <div className="y2k-lcd y2k-lcd-amber y2k-sub y2k-scanlines y2k-bevel-inner">
            <div className="y2k-sub-1">
              VOL {String(Math.round(p.volume * 100)).padStart(3, "0")}
            </div>
            <div className="y2k-sub-2">
              {trackNo}/{String(p.trackCount).padStart(2, "0")}
            </div>
          </div>
        </div>

        {/* Footer strip */}
        {(footerLeft || footerRight) && (
          <div className="y2k-footer y2k-bevel-inner">
            <span>{footerLeft}</span>
            <span>{footerRight}</span>
          </div>
        )}
      </div>
    </div>
  );
}

function TransportKey({
  children,
  label,
  onClick,
  pressed,
  disabled,
}: {
  children: React.ReactNode;
  label: string;
  onClick: () => void;
  pressed?: boolean;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onClick={onClick}
      disabled={disabled}
      data-pressed={pressed ? "true" : undefined}
      className="y2k-key y2k-panel-chrome y2k-press"
    >
      {children}
    </button>
  );
}
