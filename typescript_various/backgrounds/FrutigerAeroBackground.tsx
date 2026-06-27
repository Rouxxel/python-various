// A generic ambient background with a hero image, soft gradients, light halo, and floating bubbles.
export function AeroBackground({
  imageSrc = "/hero-background.jpg",
}: {
  imageSrc?: string;
}) {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      {/* Base image: replace with your own hero/background image. */}
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: `url('${imageSrc}')` }}
      />
      {/* Soft tint overlay to unify the palette. */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "linear-gradient(180deg, rgba(150, 180, 255, 0.18) 0%, rgba(255, 255, 255, 0.06) 45%, rgba(180, 220, 190, 0.12) 100%)",
        }}
      />
      {/* Light halo accent. */}
      <div
        className="absolute -top-24 right-10 h-[420px] w-[420px] rounded-full blur-3xl opacity-70"
        style={{ background: "radial-gradient(circle, rgba(255,255,240,0.85), rgba(255,255,230,0) 70%)" }}
      />
      {/* Soft glow blobs. */}
      <div
        className="absolute top-1/4 -left-32 h-[460px] w-[460px] rounded-full blur-3xl opacity-50"
        style={{ background: "radial-gradient(circle, rgba(200,220,255,0.7), transparent 70%)" }}
      />
      <div
        className="absolute bottom-0 left-1/3 h-[380px] w-[380px] rounded-full blur-3xl opacity-40"
        style={{ background: "radial-gradient(circle, rgba(190,240,200,0.65), transparent 70%)" }}
      />

      {/* Floating bubbles for depth. */}
      <Bubble size={140} top="12%" left="22%" delay="0s" />
      <Bubble size={90} top="60%" left="8%" delay="2s" />
      <Bubble size={180} top="30%" left="72%" delay="4s" />
      <Bubble size={60} top="78%" left="55%" delay="1s" />
      <Bubble size={110} top="8%" left="86%" delay="3s" />
      <Bubble size={70} top="48%" left="40%" delay="5s" />
    </div>
  );
}

function Bubble({ size, top, left, delay }: { size: number; top: string; left: string; delay: string }) {
  return (
    <div
      className="absolute rounded-full pointer-events-none"
      style={{
        width: size,
        height: size,
        top,
        left,
        animationDelay: delay,
        background:
          "radial-gradient(circle at 30% 28%, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.35) 18%, rgba(190,220,255,0.18) 45%, rgba(150,180,230,0.10) 70%, rgba(120,150,200,0.05) 100%)",
        boxShadow:
          "inset 0 0 24px rgba(255,255,255,0.55), inset 6px -6px 28px rgba(150,180,230,0.35), 0 8px 28px rgba(80,120,180,0.25)",
        border: "1px solid rgba(255,255,255,0.45)",
        backdropFilter: "blur(2px)",
      }}
    >
      {/* Light reflection highlight. */}
      <div
        className="absolute rounded-full"
        style={{
          top: "12%",
          left: "18%",
          width: "32%",
          height: "22%",
          background: "radial-gradient(ellipse, rgba(255,255,255,0.95), rgba(255,255,255,0) 70%)",
          filter: "blur(1px)",
        }}
      />
    </div>
  );
}
