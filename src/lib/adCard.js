// Free, quota-less ad creative: renders a designed 1080x1080 PNG in the browser.
const PALETTES = [["#1d4ed8", "#7c3aed"], ["#047857", "#0ea5e9"], ["#be123c", "#f59e0b"], ["#0f172a", "#2563eb"], ["#7c2d12", "#f59e0b"]];

function wrap(ctx, text, maxW) {
  const lines = []; let line = "";
  for (const w of String(text || "").split(/\s+/).filter(Boolean)) {
    const t = line ? `${line} ${w}` : w;
    if (ctx.measureText(t).width > maxW && line) { lines.push(line); line = w; } else line = t;
  }
  if (line) lines.push(line);
  return lines;
}

export function renderAdCard({ headline, text, cta, brand, seed = 0 }) {
  const S = 1080, c = document.createElement("canvas");
  c.width = c.height = S;
  const ctx = c.getContext("2d");
  const [a, b] = PALETTES[seed % PALETTES.length];
  const g = ctx.createLinearGradient(0, 0, S, S);
  g.addColorStop(0, a); g.addColorStop(1, b);
  ctx.fillStyle = g; ctx.fillRect(0, 0, S, S);
  ctx.globalAlpha = 0.12; ctx.fillStyle = "#fff";
  ctx.beginPath(); ctx.arc(S - 120, 160, 260, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.arc(120, S - 100, 200, 0, Math.PI * 2); ctx.fill();
  ctx.globalAlpha = 1; ctx.fillStyle = "#fff"; ctx.textBaseline = "top";
  const F = "system-ui, -apple-system, Segoe UI, sans-serif";
  ctx.font = `600 38px ${F}`; ctx.fillText(String(brand || "").toUpperCase(), 80, 80);
  ctx.font = `800 92px ${F}`; let y = 240;
  for (const l of wrap(ctx, headline, S - 160).slice(0, 4)) { ctx.fillText(l, 80, y); y += 104; }
  ctx.font = `400 40px ${F}`; ctx.globalAlpha = 0.92; y += 30;
  for (const l of wrap(ctx, text, S - 160).slice(0, 4)) { ctx.fillText(l, 80, y); y += 56; }
  ctx.globalAlpha = 1; ctx.font = `700 40px ${F}`;
  const label = cta || "Learn more", w = ctx.measureText(label).width + 80;
  ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.roundRect(80, S - 200, w, 90, 45); ctx.fill();
  ctx.fillStyle = a; ctx.fillText(label, 120, S - 176);
  return c.toDataURL("image/png");
}
