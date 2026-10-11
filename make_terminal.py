#!/usr/bin/env python3
"""Generate an animated terminal-window SVG for the GitHub profile.

Pure SVG + CSS animations (no JS, no foreignObject) so it animates
inside GitHub's <img> rendering. Typewriter effect via per-character
<tspan> reveals with staggered delays, plus a blinking block cursor.
"""
import html

W, H = 900, 470
BG, BAR, BORDER = "#16161e", "#1f2335", "#2a2f45"
GREEN, BLUE, GRAY, WHITE, ACCENT = "#9ece6a", "#7aa2f7", "#565f89", "#c0caf5", "#bb9af7"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
FS, LH, X0, Y0 = 17, 27, 34, 86
CHAR_W = FS * 0.6

# (kind, text, color) — kind "cmd" gets a green "$ " prompt
LINES = [
    ("cmd", "whoami", WHITE),
    ("out", "ankur_batta — machine learning engineer", ACCENT),
    ("cmd", "cat mission.txt", WHITE),
    ("out", "I build ML & LLM systems that run in production,", BLUE),
    ("out", "and hold them to the numbers.", BLUE),
    ("cmd", "ls ~/stack", WHITE),
    ("out", "python/  tensorflow/  pytorch/  sklearn/  aws/  docker/", GRAY),
    ("cmd", "./quizmark --stats", WHITE),
    ("out", "150 students graded  ·  r = 0.80 vs instructor  ·  $22 spend", GREEN),
    ("cmd", "./hire_me --now", WHITE),
]

CMD_CPS, OUT_CPS, LINE_GAP, START_DELAY = 34, 70, 0.45, 0.7  # chars/sec & pauses


def esc(s):
    return html.escape(s, quote=False)


parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
             f'font-family="{FONT}" role="img" aria-label="Animated terminal">')
parts.append("<style>"
             "@keyframes tw{to{opacity:1}}"
             "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
             "@keyframes pulse{0%,100%{opacity:.45}50%{opacity:.9}}"
             "</style>")
# defs: glow filter + gradient accent
parts.append("<defs>"
             '<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">'
             '<feGaussianBlur stdDeviation="22" result="b"/>'
             '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
             "</filter>"
             '<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="#58A6FF"/>'
             '<stop offset=".5" stop-color="#bb9af7"/>'
             '<stop offset="1" stop-color="#9ece6a"/>'
             "</linearGradient>"
             "</defs>")
# pulsing neon glow behind the window
parts.append(f'<rect x="14" y="14" width="{W-28}" height="{H-28}" rx="18" fill="none" '
             f'stroke="url(#accent)" stroke-width="5" filter="url(#glow)" '
             f'style="animation:pulse 4s ease-in-out infinite"/>')
# window
parts.append(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>')
parts.append(f'<rect x="2" y="2" width="{W-4}" height="46" rx="14" fill="{BAR}"/>')
parts.append(f'<rect x="2" y="32" width="{W-4}" height="16" fill="{BAR}"/>')  # square off bar bottom
for cx, col in ((30, "#ff5f56"), (54, "#febc2e"), (78, "#27c93f")):
    parts.append(f'<circle cx="{cx}" cy="25" r="7.5" fill="{col}"/>')
parts.append(f'<text x="{W/2}" y="31" text-anchor="middle" font-size="14" fill="{GRAY}">ankur@github — zsh</text>')
parts.append(f'<rect x="2" y="46" width="{W-4}" height="3.5" fill="url(#accent)" opacity="0.85"/>')

t = START_DELAY
y = Y0
for kind, text, color in LINES:
    if kind == "cmd":
        prompt, pcolor, cps = "$ ", GREEN, CMD_CPS
    else:
        prompt, pcolor, cps = "", color, OUT_CPS
    full = prompt + text
    spans = []
    for i, ch in enumerate(full):
        delay = t + i / cps
        ch_esc = esc(ch)
        if ch == " ":
            ch_esc = "&#160;"
        col = pcolor if i < len(prompt) else color
        spans.append(
            f'<tspan fill="{col}" style="opacity:0;animation:tw .01s linear {delay:.3f}s forwards">{ch_esc}</tspan>')
    parts.append(f'<text x="{X0}" y="{y}" font-size="{FS}">' + "".join(spans) + "</text>")
    t += len(full) / cps + LINE_GAP
    y += LH

# blinking block cursor after the last command
last = "$ ./hire_me --now "
cx = X0 + len(last) * CHAR_W
cy = y - LH
parts.append(
    f'<rect x="{cx:.1f}" y="{cy - FS + 4:.1f}" width="10" height="{FS}" fill="{GREEN}" opacity="0" '
    f'style="animation:blink 1.06s step-end infinite;animation-delay:{t:.3f}s"/>')

parts.append("</svg>")
svg = "\n".join(parts)
with open("terminal.svg", "w") as f:
    f.write(svg)
print(f"wrote terminal.svg ({len(svg)//1024} KB), total animation ~{t:.1f}s")
