import { useCallback, useEffect, useRef } from "react";

interface KnobProps {
  /** 0..1 */
  value: number;
  onChange: (v: number) => void;
  label?: string;
}

const MIN_ANGLE = -135;
const MAX_ANGLE = 135;

/**
 * Rotary volume knob with a real mechanical travel limit (-135deg..+135deg).
 * Drag in a circle (or use arrow keys) to turn it.
 */
export function VolumeKnob({ value, onChange, label = "Volume" }: KnobProps) {
  const ref = useRef<HTMLDivElement | null>(null);
  const dragging = useRef(false);
  const angle = MIN_ANGLE + value * (MAX_ANGLE - MIN_ANGLE);

  const fromPointer = useCallback(
    (clientX: number, clientY: number) => {
      const el = ref.current;
      if (!el) return;
      const r = el.getBoundingClientRect();
      const cx = r.left + r.width / 2;
      const cy = r.top + r.height / 2;
      // 0deg = pointing up, clockwise positive.
      let deg = (Math.atan2(clientX - cx, cy - clientY) * 180) / Math.PI;
      deg = Math.max(MIN_ANGLE, Math.min(MAX_ANGLE, deg));
      onChange((deg - MIN_ANGLE) / (MAX_ANGLE - MIN_ANGLE));
    },
    [onChange],
  );

  useEffect(() => {
    const move = (e: PointerEvent) => {
      if (!dragging.current) return;
      e.preventDefault();
      fromPointer(e.clientX, e.clientY);
    };
    const up = () => {
      dragging.current = false;
    };
    window.addEventListener("pointermove", move, { passive: false });
    window.addEventListener("pointerup", up);
    return () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
  }, [fromPointer]);

  return (
    <div
      ref={ref}
      role="slider"
      tabIndex={0}
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(value * 100)}
      className="y2k-knob y2k-bevel-outer"
      onPointerDown={(e) => {
        dragging.current = true;
        (e.target as HTMLElement).setPointerCapture?.(e.pointerId);
        fromPointer(e.clientX, e.clientY);
      }}
      onKeyDown={(e) => {
        if (e.key === "ArrowUp" || e.key === "ArrowRight") {
          e.preventDefault();
          onChange(Math.min(1, value + 0.05));
        } else if (e.key === "ArrowDown" || e.key === "ArrowLeft") {
          e.preventDefault();
          onChange(Math.max(0, value - 0.05));
        }
      }}
    >
      <div
        className="y2k-knob-body"
        style={{ transform: `rotate(${angle}deg)`, transition: "transform 60ms linear" }}
      >
        <span className="y2k-knob-notch" />
        <span className="y2k-knob-cap" />
      </div>
    </div>
  );
}
