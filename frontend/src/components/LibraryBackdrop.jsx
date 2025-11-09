import React from 'react';

const LeftBookshelf = () => (
  <svg width="100%" height="100%" viewBox="0 0 500 900" preserveAspectRatio="xMidYMid slice" aria-hidden>
    <defs>
      <linearGradient id="woodL" x1="0" x2="1">
        <stop offset="0%" stopColor="#8d5b3b" />
        <stop offset="100%" stopColor="#6b3f28" />
      </linearGradient>
    </defs>
    <rect x="0" y="0" width="500" height="900" fill="url(#woodL)" />
    {/* multiple shelves */}
    <g fill="#4a2e1e">
      <rect x="10" y="80" width="480" height="12" />
      <rect x="10" y="220" width="480" height="12" />
      <rect x="10" y="360" width="480" height="12" />
      <rect x="10" y="500" width="480" height="12" />
      <rect x="10" y="640" width="480" height="12" />
    </g>
    {/* books on left */}
    <g>
      {Array.from({ length: 28 }).map((_, i) => {
        const shelf = Math.floor(i / 7);
        const col = i % 7;
        const x = 20 + col * 66 + (shelf % 2) * 6;
        const y = 90 + shelf * 140;
        const h = 60 + ((i * 23) % 120);
        const color = ['#e8c7a4', '#c48a5b', '#b36c40', '#d9a67b', '#9a6b45'][i % 5];
        return <rect key={i} x={x} y={y + (80 - h)} width={40} height={h} rx="3" fill={color} />;
      })}
    </g>
  </svg>
);

const FilmReel = ({ size = 140 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" aria-hidden>
    <circle cx="50" cy="50" r="45" fill="#2b2b2b" />
    <circle cx="50" cy="50" r="30" fill="#f5f5f5" />
    <g fill="#2b2b2b">
      <circle cx="50" cy="20" r="6" />
      <circle cx="80" cy="50" r="6" />
      <circle cx="50" cy="80" r="6" />
      <circle cx="20" cy="50" r="6" />
    </g>
  </svg>
);

const MoviePoster = ({ title = 'Classic Cinema' }) => (
  <svg width="160" height="240" viewBox="0 0 160 240" aria-hidden>
    <rect x="0" y="0" width="160" height="240" rx="8" fill="#0b1220" />
    <rect x="10" y="10" width="140" height="120" rx="6" fill="#663d1f" />
    <text x="20" y="160" fill="#ffd08a" fontSize="16" fontFamily="serif">{title}</text>
    <rect x="10" y="190" width="140" height="30" rx="6" fill="#8c5a3b" />
  </svg>
);

const Projector = () => (
  <svg width="180" height="120" viewBox="0 0 180 120" aria-hidden>
    <rect x="10" y="30" width="90" height="60" rx="6" fill="#3f3f3f" />
    <rect x="110" y="40" width="50" height="40" rx="4" fill="#2b2b2b" />
    <circle cx="130" cy="60" r="10" fill="#ffd77a" opacity="0.9" />
    <rect x="125" y="55" width="40" height="8" fill="#ffefc9" opacity="0.15" transform="rotate(-12 125 55)" />
  </svg>
);

const Armchair = () => (
  <svg width="200" height="140" viewBox="0 0 200 140" aria-hidden>
    <rect x="10" y="40" width="180" height="70" rx="18" fill="#6b3f28" />
    <rect x="30" y="20" width="60" height="50" rx="12" fill="#7e4c31" />
    <rect x="110" y="20" width="60" height="50" rx="12" fill="#7e4c31" />
    <rect x="70" y="70" width="60" height="40" rx="8" fill="#5a2f1b" />
  </svg>
);

const DustParticles = () => (
  <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden>
    {Array.from({ length: 18 }).map((_, i) => (
      <circle key={i} cx={(i * 17) % 100} cy={(i * 23) % 100} r={(i % 4) + 0.6} fill="rgba(255,244,220,0.18)" />
    ))}
  </svg>
);

export default function LibraryBackdrop() {
  return (
    <div className="pointer-events-none library-backdrop">
      {/* Left bookish large shelf */}
      <div className="bookshelf-left" aria-hidden>
        <LeftBookshelf />
      </div>

      {/* Right movie area */}
      <div className="movie-right" aria-hidden>
        <div className="poster-wrap">
          <MoviePoster />
        </div>
        <div className="reel-wrap">
          <FilmReel />
        </div>
        <div className="projector-wrap">
          <Projector />
        </div>
        <div className="armchair-wrap">
          <Armchair />
        </div>
      </div>

      {/* Plants and lamp to flavor center area */}
      <div className="lamp-wrap" aria-hidden>
        <div className="lamp-glow">
          <svg width="300" height="300" viewBox="0 0 300 300" aria-hidden>
            <defs>
              <radialGradient id="g1" cx="50%" cy="40%" r="50%">
                <stop offset="0%" stopColor="#fff1d6" stopOpacity="0.9" />
                <stop offset="100%" stopColor="#ffd07a" stopOpacity="0" />
              </radialGradient>
            </defs>
            <circle cx="150" cy="80" r="80" fill="url(#g1)" />
          </svg>
        </div>
      </div>

      {/* floating dust */}
      <div className="dust" aria-hidden>
        <DustParticles />
      </div>

      <div className="vignette" aria-hidden />
    </div>
  );
}
