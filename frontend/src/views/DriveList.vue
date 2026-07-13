<template>
  <div class="board">
    <header class="board-head">
      <p class="eyebrow">Placement Cell // Control Room</p>
      <h2 class="headline">Placement Drives</h2>
      <p class="sub">Browse all approved drives here.</p>
    </header>

    <div class="note">
      <span class="note-dot"></span>
      <div class="note-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
          <path d="M6 3v18"/>
          <path d="M6 4h12l-3 4 3 4H6"/>
        </svg>
      </div>
      <p class="note-title">No drives pinned up yet</p>
      <p class="note-text">Approved drives will land here as soon as companies post them.</p>
    </div>
  </div>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&display=swap");

.board {
  --ink: #14132b;
  --paper: #efedf7;
  --accent: #ffc857;
  min-height: 100%;
  background: var(--ink);
  background-image:
    radial-gradient(circle at 1px 1px, rgba(255,255,255,0.06) 1px, transparent 1px);
  background-size: 22px 22px;
  padding: 3rem 2rem 4rem;
  font-family: "Inter", sans-serif;
  color: var(--paper);
}

.board-head {
  max-width: 640px;
  margin: 0 auto 2.75rem;
  text-align: left;
}

.eyebrow {
  font-family: "Space Grotesk", sans-serif;
  font-size: 0.8rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #ff6b4a;
  margin: 0 0 0.5rem;
}

.headline {
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: clamp(2rem, 4vw, 2.75rem);
  margin: 0 0 0.4rem;
  letter-spacing: -0.01em;
}

.sub {
  margin: 0;
  color: rgba(239, 237, 247, 0.6);
  font-size: 0.95rem;
}

.note {
  position: relative;
  max-width: 420px;
  margin: 0 auto;
  background: var(--paper);
  color: var(--ink);
  border-radius: 10px;
  padding: 2.25rem 2rem;
  text-align: center;
  transform: rotate(1.5deg);
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.35);
}

.note-dot {
  position: absolute;
  top: -9px;
  left: 50%;
  transform: translateX(-50%);
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.35);
}

.note-icon {
  width: 38px;
  height: 38px;
  margin: 0 auto 1rem;
  color: var(--accent);
}

.note-icon svg {
  width: 100%;
  height: 100%;
}

.note-title {
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  font-size: 1.15rem;
  margin: 0 0 0.4rem;
}

.note-text {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(20, 19, 43, 0.65);
  line-height: 1.5;
}
</style>