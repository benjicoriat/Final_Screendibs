import React from 'react';

function HolographicShelf() {
  return (
    <svg viewBox="0 0 600 600" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" aria-hidden>
      <defs>
        <linearGradient id="hg1" x1="0" x2="1">
          <stop offset="0%" stopColor="#7ef0ff" stopOpacity="0.18" />
          <stop offset="50%" stopColor="#b58bff" stopOpacity="0.08" />
          <stop offset="100%" stopColor="#ff5dc1" stopOpacity="0.06" />
        </linearGradient>
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="8" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <rect x="0" y="0" width="100%" height="100%" fill="url(#hg1)" opacity="0.06" />

      {/* Holographic shelves */}
      {Array.from({ length: 4 }).map((_, row) => (
        <g key={row} transform={`translate(0, ${80 + row * 110})`} opacity="0.95">
          <rect x="12" y="0" width="420" height="6" fill="rgba(255,255,255,0.04)" />
          {/* floating book spines */}
          {Array.from({ length: 10 }).map((__, i) => {
            const x = 20 + i * 40 + (row % 2 ? 6 : 0);
            const h = 36 + ((i * 13 + row * 7) % 60);
            const colors = ['#6ef3ff', '#8a7bff', '#ff6ec7', '#5af3c7'];
            return (
              <rect
                key={i}
                x={x}
                y={-h}
                width={18}
                height={h}
                rx={2}
                fill={colors[(i + row) % colors.length]}
                style={{ mixBlendMode: 'screen' }}
                filter="url(#glow)"
                className="holo-spine"
              />
            );
          })}
        </g>
      ))}

      {/* data streams */}
      {Array.from({ length: 6 }).map((_, i) => (
        <rect
          key={i}
          x={440 + i * 18}
          y={40}
          width={4}
          height={420}
          fill={`rgba(110,240,255,${0.06 + (i % 3) * 0.04})`}
          className={`data-stream ds-${i}`}
        />
      ))}
    </svg>
  );
}

function MovieCluster() {
  return (
    <svg viewBox="0 0 600 600" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" aria-hidden>
      <defs>
        <linearGradient id="neonA" x1="0" x2="1">
          <stop offset="0%" stopColor="#00f6ff" />
          <stop offset="100%" stopColor="#ff46ff" />
        </linearGradient>
        <linearGradient id="neonB" x1="0" x2="1">
          <stop offset="0%" stopColor="#00ffd1" />
          <stop offset="100%" stopColor="#6a77ff" />
        </linearGradient>
      </defs>

      {/* neon panels */}
      <g transform="translate(40,30)">
        <rect x="0" y="0" rx="10" width="200" height="120" fill="rgba(255,255,255,0.03)" stroke="url(#neonA)" strokeWidth="2" className="neon-panel" />
        <rect x="20" y="140" rx="6" width="140" height="84" fill="rgba(0,0,0,0.18)" stroke="url(#neonB)" strokeWidth="2" className="neon-screen" />

        {/* floating holographic reel */}
        <g transform="translate(260,40) scale(0.9)" className="reel-group">
          <circle cx="80" cy="80" r="52" fill="#0e0f14" opacity="0.9" />
          <circle cx="80" cy="80" r="36" fill="#ffffff" opacity="0.06" />
          {Array.from({ length: 6 }).map((_, k) => (
            <rect key={k} x={80 + Math.cos((k / 6) * Math.PI * 2) * 40 - 6} y={80 + Math.sin((k / 6) * Math.PI * 2) * 40 - 6} width={12} height={12} rx={3} fill="#dfefff" opacity={0.9} />
          ))}
        </g>
      </g>
    </svg>
  );
}

export default function FuturisticBackdrop() {
  return (
    <div className="pointer-events-none futuristic-backdrop">
      <div className="left-half">
        <div className="shelf-wrap">
          <HolographicShelf />
        </div>
        <div className="knowledge-flow" aria-hidden>
          {/* animated SVG lines are handled via CSS */}
          <svg viewBox="0 0 400 600" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
            <g stroke="#9ef6ff" strokeWidth="1.2" strokeOpacity="0.28" fill="none">
              {Array.from({ length: 10 }).map((_, i) => (
                <path key={i} d={`M ${20 + i * 36} 0 C ${40 + i * 36} 120, ${10 + i * 36} 240, ${30 + i * 36} 360`} className={`stream stream-${i}`} />
              ))}
            </g>
          </svg>
        </div>
      </div>

      <div className="right-half">
        <div className="movie-wrap"><MovieCluster /></div>
        <div className="glass-panels">
          <div className="glass card-1" />
          <div className="glass card-2" />
        </div>
      </div>

      <div className="particles" aria-hidden>
        {Array.from({ length: 36 }).map((_, i) => (
          <div key={i} className={`particle p-${i}`} />
        ))}
      </div>

      <div className="vignette-strong" aria-hidden />
    </div>
  );
}
