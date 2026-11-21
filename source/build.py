"""Build the Folio theme for T3 Code: folio.json (e-reader greyscale on warm paper)."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
INK = "#1c1b18"
INK2 = "#24221e"
PAGE = "#f4f1e8"       # the page (reading column)
DESK = "#e9e5da"       # canvas around the page
CHROME = "#e4dfd3"
HAIR = "#bcb5a5"
SERIF = '"Iowan Old Style","Palatino Linotype",Palatino,Charter,Georgia,serif'
LOOP = 24              # seconds: one fill, then HOLD (never loops)
N = 48                 # dots in the progress bar
FILL = 100             # percent of LOOP spent filling


def p(x):
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return s + "%"


def data_uri(svg):
    out = svg.replace("%", "%25").replace("#", "%23").replace('"', "'").replace("<", "%3C")
    return 'url("data:image/svg+xml,' + out + '")'


# ------------------------------------------------------------ SVG: folio card (page number + dots)
# Margin art is a set of STATIC frames. The outer CSS steps between them with background-position keyframes,
# because an SVG image's own animation timeline does not restart on the second turn.
CARD_CSS = (f"text{{fill:{INK};font-family:{SERIF}}}"
            ".big{font-size:54px;font-weight:600}.sm{font-size:11px;letter-spacing:.14em;fill-opacity:.75}")
CARD_DEFS = f"<defs><pattern id='dt' width='4' height='4' patternUnits='userSpaceOnUse'><path d='M0 0h1v1h-1zM2 2h1v1h-1z' fill='{INK}'/></pattern></defs>"


def card_body(num, nfill, label, ghost=False, defs=True):
    b = (f"<path d='M2 2H118L148 32V126H2Z' fill='{PAGE}' stroke='{INK}' stroke-width='1.6' stroke-linejoin='miter'/>"
         + (CARD_DEFS if defs else "") +
         f"<path d='M118 2V32H148' fill='url(#dt)' stroke='{INK}' stroke-width='1.6'/>"
         f"<text class='sm' x='14' y='22'>{label}</text>")
    if ghost:   # ghost of the previous page, left behind like e-paper after a refresh
        b += "<text class='big' x='12' y='82' style='opacity:.09'>147</text>"
    b += f"<text class='big' x='12' y='82'>{num}</text>"
    for k in range(12):
        x = 15 + 10.8 * k
        b += f"<circle cx='{x:.1f}' cy='116' r='3' fill='url(#dt)' stroke='{INK}' stroke-width='1' stroke-opacity='.6'/>"
        if k < nfill:
            b += f"<circle cx='{x:.1f}' cy='116' r='3' fill='{INK}'/>"
    return b


def card_svg(num=148, nfill=12, label="AT REST", ghost=True):
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 150 128'><style>{CARD_CSS}</style>{card_body(num, nfill, label, ghost)}</svg>"


# 13 working frames: 0..11 = fill, 12 = hold alternate (12th dot lit). Frame 13 in the sprite = at rest.
NF = 6   # fill steps (4s apart); frame NF = hold alternate (12th dot lit); frame NF+1 in the sprite = at rest
CARD_FRAMES = [(142 + round(min(i, NF - 1) * 6 / (NF - 1)), round(min(i, NF - 1) * 11 / (NF - 1)) if i < NF else 12) for i in range(NF + 1)]


def card_frame_svg(i):
    n, d = CARD_FRAMES[i]
    return card_svg(n, d, "IN PROGRESS", False)


def card_sprite():
    parts = [card_body(n, d, "IN PROGRESS", False, defs=(i == 0)) for i, (n, d) in enumerate(CARD_FRAMES)]
    parts.append(card_body(148, 12, "AT REST", True, defs=False))
    g = "".join(f"<g transform='translate(0 {128*i})'>{b}</g>" for i, b in enumerate(parts))
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 150 {128*len(parts)}'><style>{CARD_CSS}</style>{g}</svg>"


# ------------------------------------------------------------ SVG: contents scrubber (left gutter)
ROMANS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
SY0, SDY = 54, 40
SYS = [SY0 + SDY * i for i in range(9)]


def scrub_svg(mi=5, pulse=False):
    top, bot = SYS[0], SYS[-1]
    css = (f"text{{fill:{INK};font-family:{SERIF}}}.r{{font-size:15px;fill-opacity:.8}}.cap{{font-size:10px;letter-spacing:.2em;fill-opacity:.7}}")
    body = (f"<path d='M26 {top}V{bot}' stroke='{INK}' stroke-width='2.4' stroke-opacity='.5' stroke-linecap='round' stroke-dasharray='.1 6'/>"
            f"<rect x='25' y='{top}' width='2' height='{SYS[mi]-top}' fill='{INK}'/>")
    for y, r in zip(SYS, ROMANS):
        body += f"<path d='M26 {y}H36' stroke='{INK}' stroke-width='1.4'/>"
    y = SYS[mi]
    body += (f"<rect x='20' y='{y-6}' width='12' height='12' fill='{INK}' transform='rotate(45 26 {y})'/>"
             f"<circle cx='26' cy='{y}' r='2' fill='{INK if pulse else PAGE}'/>")
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 130 {bot+36}'><style>{css}</style>{body}</svg>"


def dither(frac_pixels, size=4):
    """Ordered-dither tile (Bayer 4x4 subset) as an svg data URI; rendered crisp."""
    bayer = [(0, 0), (2, 2), (2, 0), (0, 2), (1, 1), (3, 3), (3, 1), (1, 3)]
    d = "".join(f"M{x} {y}h1v1h-1z" for x, y in bayer[:frac_pixels])
    return data_uri(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {size} {size}' shape-rendering='crispEdges'><path d='{d}' fill='{INK2}'/></svg>")


def dots3():
    c = "".join(f"<circle cx='{3+8*i}' cy='3' r='1.9' fill='none' stroke='{INK}' stroke-width='.9' stroke-opacity='.6'/>" for i in range(3))
    return data_uri(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 22 6'>{c}</svg>")


# ------------------------------------------------------------ theme colours
colors = {
    "canvas": DESK, "chrome": CHROME, "toolbar": "#e7e3d8", "toolbarForeground": INK,
    "toolbarBorder": "#c4bdad", "toolbarControl": "#ddd7c9", "toolbarControlForeground": INK,
    "toolbarControlHover": "#d0c9b9", "surface": "#f8f6ef", "surfaceRaised": "#faf8f2",
    "surfaceOverlay": "#fbf9f4", "text": INK, "textMuted": "#55514a", "border": "#c4bdad",
    "input": "#8b8575", "focus": INK, "accent": INK2, "accentForeground": "#f4f0e6",
    "secondary": "#ddd7c9", "secondaryForeground": INK, "muted": "#e0dbce",
    "mutedForeground": "#58544c", "placeholder": "#77726a", "secondaryLabel": "#58544c",
    "iconMuted": "#5f5b53", "error": "#8c2f25", "errorForeground": "#7a241b", "errorSurface": "#efdcd5",
    "warning": "#7d5b14", "warningForeground": "#6b4d0e", "warningSurface": "#eee2c6",
    "update": "#35495c", "updateForeground": "#2b3d4e", "updateSurface": "#dde3e6",
    "accentSurface": "#d8d2c3", "accentSurfaceForeground": INK, "messageSurface": "#e2dccd",
    "messageForeground": INK, "messageAction": INK2, "messageActionForeground": "#f4f0e6",
    "messageActionHover": "#3f3c36", "codeBackground": "#e8e3d6", "codeForeground": INK,
    "searchMatchBackground": "#cfc8b2", "searchMatchForeground": INK,
    "searchMatchActiveBackground": INK2, "searchMatchActiveForeground": "#f4f0e6",
    "sidebar": "#e5e0d4", "sidebarForeground": INK, "sidebarMutedForeground": "#55514a",
    "sidebarControlSurface": "#efebe1", "sidebarRowHover": "#dad4c6", "sidebarRowActive": "#d3ccbc",
    "sidebarRowSelected": "#d3ccbc", "sidebarBorder": "#c4bdad", "terminalBackground": "#ebe7dc",
    "terminalForeground": INK, "terminalCursor": INK, "terminalSelection": "#c5bfae",
    "terminalScrollbar": "#bdb6a6", "terminalScrollbarHover": "#8f897b",
}

# ------------------------------------------------------------ CSS
CW = "var(--chat-content-max-width,46rem)"
G = f"(100% - {CW})/2"
BUSY = ('body:has([data-timeline-row-kind="working"])',
        'body:has([data-thread-item] [aria-busy="true"][aria-current]:not([aria-current="false"]))')


def busy(sel):
    return ",".join(f"{b} {sel}" for b in BUSY)


def gutter_size(threshold, maxw):
    return f"min({maxw}px,clamp(0px,({G} - {threshold}px)*1000,{G} - 40px)) auto"


PAGEGRAD = (f"linear-gradient(90deg,transparent calc(50% - {CW}/2 - 28px),{HAIR} calc(50% - {CW}/2 - 28px) calc(50% - {CW}/2 - 27px),{PAGE} calc(50% - {CW}/2 - 27px) calc(50% + {CW}/2 + 27px),{HAIR} calc(50% + {CW}/2 + 27px) calc(50% + {CW}/2 + 28px),transparent calc(50% + {CW}/2 + 28px))")
PAPER_VEIL = "rgba(228,223,211,.82)"   # header colour at 82%: unfilled dots read as pale grey
DOT = f"radial-gradient(circle,{INK} 2.6px,transparent 3.2px)"
DITH = dither(4)
DITH_LIGHT = dither(2)
DITH2 = dither(1, 4)
DESKDITH = data_uri(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 4 4' shape-rendering='crispEdges'><path d='M0 0h1v1h-1z' fill='{INK2}' fill-opacity='.4'/></svg>")
CHECK = data_uri(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 2 2' shape-rendering='crispEdges'><path d='M0 0h1v1H0zM1 1h1v1H1z' fill='{INK2}'/></svg>")

fl = lambda name, dur=".7s": f"animation:{name} {dur} step-end 1 both"


# one-shot "page turn" on turn END only: --fo-f transitions busy(1) -> idle(0) in steps; a = f(1-f) peaks mid-way.
# A transition never runs on mount or thread switch, only when the busy selector stops matching.
def amt(k):
    return f"calc(var(--fo-f)*(1 - var(--fo-f))*{k}%)"


SCRIM = "linear-gradient(rgba(229,224,212,.62),rgba(229,224,212,.62))"
FLASH_T = "transition:--fo-f .5s steps(8,end) .25s,background-position 0s step-end .25s"
DESKC = f"color-mix(in srgb,#8b8575 {amt(240)},{DESK})"
HEADC = f"color-mix(in srgb,#8b8575 {amt(160)},#e7e3d8)"


# ---- margin art: stacked static layers, one visible at a time; outer-CSS keyframes step background-position
OFF = "-9999px 0"


def layer_vars():
    v = {"fo-s0": scrub_svg(5), "fo-s1": scrub_svg(6), "fo-s2": scrub_svg(7), "fo-s3": scrub_svg(7, True),
         "fo-cr": card_svg(), "fo-sp": card_sprite()}
    for i in range(NF + 1):
        v[f"fo-c{i}"] = card_frame_svg(i)
    return ":root{" + ";".join(f"--{k}:" + data_uri(x) for k, x in v.items()) + "}"


def pos_list(n, on, on_pos, tail=None):
    ps = [on_pos if i == on else OFF for i in range(n)]
    if tail:
        ps.append(tail)
    return ",".join(ps)


def kf(name, stops):
    return f"@keyframes {name}{{" + "".join(f"{p(t)}{{background-position:{v}}}" for t, v in stops) + "}"


SCR_ON, CARD_ON = "left 18px top 58px", "right 18px bottom 22px"
SC_LAYERS = ["--fo-s0", "--fo-s1", "--fo-s2", "--fo-s3"]
CD_LAYERS = ["--fo-cr"] + [f"--fo-c{i}" for i in range(NF + 1)]
SC_SIZE = gutter_size(175, 130)
CD_SIZE = gutter_size(190, 150)
SC_FILL = [(0, pos_list(4, 0, SCR_ON, "0 0")), (100 / 3, pos_list(4, 1, SCR_ON, "0 0")), (200 / 3, pos_list(4, 2, SCR_ON, "0 0"))]
NL = NF + 2   # card layers in the scroller
CD_FILL = [(i * 100 / NF, pos_list(NL, i + 1, CARD_ON, "0 0")) for i in range(NF)]
DOCK_H = 84 * 128 / 150          # frame height in the sprite at 84px wide
HOLD = 8                          # seconds per hold step (the unfinished-turn signal)


def dock_pos(f):
    return f"0 {-DOCK_H * f:.2f}px"


css = (
    "@property --fo-f{syntax:'<number>';inherits:false;initial-value:0}" + layer_vars() +
    # --- the desk and the page: left gutter holds the contents scrubber, right gutter the folio card.
    # Longhands: image/size/repeat/colour are important; position is not, so the keyframes can step it.
    "[data-workspace-area=\"conversation\"]{background-color:" + DESKC + "!important;background-image:" + ",".join(f"var({n})" for n in SC_LAYERS) + "," + DESKDITH + "!important;"
    "background-size:" + ",".join([SC_SIZE] * 4) + ",4px 4px!important;background-repeat:no-repeat,no-repeat,no-repeat,no-repeat,repeat!important;"
    "background-position:" + pos_list(4, 0, SCR_ON, "0 0") + ";--fo-f:0;" + FLASH_T + "}"
    + busy('[data-workspace-area="conversation"]') + f"{{--fo-f:1;transition:none;animation:fo-sc {LOOP}s step-end 1 forwards,fo-sch {2*HOLD}s step-end {LOOP}s infinite}}"
    + kf("fo-sc", SC_FILL) + kf("fo-sch", [(0, pos_list(4, 2, SCR_ON, "0 0")), (50, pos_list(4, 3, SCR_ON, "0 0"))])
    + "[data-workspace-area=\"conversation\"] .messages-timeline-scroll{background-color:transparent!important;background-image:" + ",".join(f"var({n})" for n in CD_LAYERS) + "," + PAGEGRAD + "!important;"
    "background-size:" + ",".join([CD_SIZE] * NL) + ",auto!important;background-repeat:no-repeat!important;"
    "background-position:" + pos_list(NL, 0, CARD_ON, "0 0") + "}"
    + busy('[data-workspace-area="conversation"] .messages-timeline-scroll') + f"{{animation:fo-cd {LOOP}s step-end 1 forwards,fo-cdh {2*HOLD}s step-end {LOOP}s infinite}}"
    + kf("fo-cd", CD_FILL) + kf("fo-cdh", [(0, pos_list(NL, NF - 1 + 1, CARD_ON, "0 0")), (50, pos_list(NL, NF + 1, CARD_ON, "0 0"))]) +
    # --- header: a bar of dots fills while a turn runs (stepped), drains when it ends
    f"[data-chat-header]{{--fo-f:0;{FLASH_T};background-color:{HEADC}!important;background-image:linear-gradient(90deg,transparent 50%,{PAPER_VEIL} 50%),{DOT}!important;"
    f"background-repeat:no-repeat,repeat-x!important;background-size:200% 9px,calc(100%/{N}) 9px!important;background-position:100% 100%,0 100%;"
    f"border-bottom:1px solid #b7b0a0!important;font-family:{SERIF};font-variant:small-caps;letter-spacing:.04em}}"
    + busy("[data-chat-header]") + f"{{--fo-f:1;transition:none;animation:fo-fill {LOOP}s steps(44) 1 forwards,fo-hold 4s step-end {LOOP}s infinite}}"
    f"@keyframes fo-fill{{0%{{background-position:100% 100%,0 100%}}100%{{background-position:8.33% 100%,0 100%}}}}"
    "@keyframes fo-hold{0%{background-position:8.33% 100%,0 100%}50%{background-position:4.17% 100%,0 100%}}"
    # --- busy thread / working row: three hollow dots, one filled, stepping (not a marching line)
    "[data-thread-item] [aria-busy=\"true\"],[data-timeline-row-kind=\"working\"]{background-image:radial-gradient(circle," + INK + " 1.9px,transparent 2.4px)," + dots3() + "!important;"
    "background-repeat:no-repeat!important;background-size:8px 6px,22px 6px!important;background-position:0 100%,0 100%;animation:fo-3 1.5s step-end infinite}"
    "[data-thread-item] [aria-busy=\"true\"]{background-position:10px calc(100% - 1px),10px calc(100% - 1px);animation-name:fo-3t}"
    "@keyframes fo-3{0%{background-position:0 100%,0 100%}33%{background-position:8px 100%,0 100%}66%{background-position:16px 100%,0 100%}}"
    "@keyframes fo-3t{0%{background-position:10px calc(100% - 1px),10px calc(100% - 1px)}33%{background-position:18px calc(100% - 1px),10px calc(100% - 1px)}66%{background-position:26px calc(100% - 1px),10px calc(100% - 1px)}}"
    # --- sidebar
    "[data-slot=\"sidebar-inner\"]{background:#e5e0d4!important;box-shadow:inset -1px 0 0 #c4bdad}"
    # narrow windows: no gutter, so the folio card docks at the foot of the sidebar
    "@media (max-width:1459px){[data-slot=\"sidebar-inner\"]::after{content:\"\";display:block;flex:none;width:84px;height:" + f"{DOCK_H:.2f}" + "px;margin:8px 8px 0 auto;background:var(--fo-sp) " + dock_pos(NF + 1) + "/84px auto no-repeat}"
    + busy('[data-slot="sidebar-inner"]::after') + f"{{animation:fo-dk {LOOP}s step-end 1 forwards,fo-dkh {2*HOLD}s step-end {LOOP}s infinite}}"
    + kf("fo-dk", [(i * 100 / NF, dock_pos(i)) for i in range(NF)]) + kf("fo-dkh", [(0, dock_pos(NF - 1)), (50, dock_pos(NF))]) + "}"
    f"[data-thread-item]{{background-image:linear-gradient({INK},{INK});background-repeat:no-repeat;background-position:3px 50%;background-size:2px 0;transition:background-size .15s steps(3)}}"
    "[data-thread-item]:hover{background-size:2px 62%}"
    f"[data-thread-item] [aria-current]:not([aria-current=\"false\"]){{box-shadow:inset 3px 0 {INK}}}"
    f"[data-slot=\"project-monogram\"]{{background:{INK2}!important;color:#f4f0e6!important;border-radius:2px!important}}"
    # --- conversation
    f"[data-user-message-bubble]{{background:#e2dccd!important;border:1px solid {INK2}!important;border-radius:2px!important;font-family:{SERIF};font-size:1.04em}}"
    f"[data-slot=\"composer-host\"]{{background:#f8f6ef!important;border:1px solid {INK2}!important;border-radius:2px!important;transition:box-shadow .15s steps(2)}}"
    f"[data-slot=\"composer-host\"]:focus-within{{box-shadow:inset 0 0 0 2px #f8f6ef,inset 0 0 0 3px {INK2}}}"
    f".composer-tiptap{{font-family:{SERIF};font-size:1.04em}}"
    f".chat-markdown{{font-family:{SERIF};line-height:1.72;font-size:1.04em;text-wrap:pretty;hyphens:auto}}"
    f".chat-markdown :is(h1,h2,h3,h4){{font-family:{SERIF};font-weight:700;letter-spacing:.005em}}"
    f".chat-markdown h1{{border-bottom:3px double {INK2};padding-bottom:.25em}}"
    f".chat-markdown h2{{border-bottom:1px solid {HAIR};padding-bottom:.2em}}"
    ".chat-markdown h3{font-variant:small-caps;letter-spacing:.06em}"
    f".chat-markdown :not(pre)>code{{background:#e4dfd1;border:1px solid #c9c2b2;padding:.02em .32em;border-radius:1px;font-size:.88em}}"
    f".chat-markdown a{{color:{INK}!important;text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}}"
    f".chat-markdown a:hover{{background:{INK2};color:#f4f0e6!important;text-decoration:none}}"
    f".chat-markdown blockquote{{border-left:3px double {INK2}!important;font-style:italic;padding-left:1em}}"
    f".chat-markdown hr{{border:0!important;height:6px;background:{DITH_LIGHT} repeat-x center/8px 8px}}"
    f".chat-markdown table :is(th,td){{border-color:{HAIR}!important}}"
    f".chat-markdown-codeblock{{background:{DITH_LIGHT} top left/8px 8px repeat-x,#e8e3d6!important;background-size:8px 4px,auto!important;background-repeat:repeat-x,no-repeat!important;"
    f"border:1px solid {INK2}!important;border-radius:0!important}}"
    "svg.lucide{stroke-width:1.5;stroke-linecap:square;stroke-linejoin:miter}"
    f"::selection{{background:{INK2};color:#f4f0e6}}"
    f":focus-visible{{outline:2px solid {INK2}!important;outline-offset:2px!important}}"
    f"[data-slot=\"dialog-popup\"],[data-slot=\"popover-popup\"],[data-slot=\"menu-popup\"]{{border-radius:2px!important;border:1px solid {INK2}!important;box-shadow:4px 4px 0 rgba(28,27,24,.16)!important}}"
    f"[data-slot=\"tooltip-popup\"]{{background:{INK2}!important;color:#f4f0e6!important;border-radius:2px!important;border:0!important}}"
    "[data-slot=\"button\"],[data-slot=\"input\"],[data-slot=\"select-trigger\"]{border-radius:2px!important}"
    "[data-slot=\"select-trigger\"],:is([data-slot=\"dialog-popup\"],[data-slot=\"popover-popup\"],[data-settings-page-scroll]) [data-slot=\"button\"]{border:1px solid rgba(36,34,30,.55)!important}"
    ".chat-markdown ul>li::marker{content:\"\\2013  \";color:" + INK + "}.chat-markdown ol>li::marker{font-variant-numeric:oldstyle-nums;font-variant:small-caps;color:" + INK + "}"
    f"[data-slot=\"switch\"]{{border-radius:2px!important}}"
    f"[data-thread-details-card],[data-thread-terminal-drawer]{{border-radius:2px!important;border-color:{HAIR}!important}}"
    f"::-webkit-scrollbar-thumb,[data-slot=\"scroll-area-thumb\"]{{background:{CHECK} 0 0/4px 4px!important;border:1px solid {INK2}!important;border-radius:0!important}}"
    "::-webkit-scrollbar-track{background:transparent!important}"
    # --- sidebar in the same book: serif titles, hairline between rows, italic working label, dithered open row
    f"[data-slot=\"sidebar-inner\"]{{font-family:{SERIF}}}"
    "[data-thread-item]{border-bottom:1px solid rgba(188,181,165,.55)}"
    "[data-thread-item] [aria-busy=\"true\"]{font-style:italic}"
    f"[data-thread-item] [aria-current]:not([aria-current=\"false\"]):not([aria-busy=\"true\"]){{background-image:{DITH2};background-size:4px 4px;background-repeat:repeat-x;background-position:0 100%}}"
    # --- user bubble: dithered drop edge
    f"[data-user-message-bubble]{{background-image:{DITH_LIGHT}!important;background-repeat:repeat-x!important;background-position:left bottom!important;background-size:8px 8px!important}}"
    # --- controls: ink hairlines, inverted hover/active, doubled input focus, square switch
    ":is([data-slot=\"dialog-popup\"],[data-slot=\"popover-popup\"],[data-settings-page-scroll]) [data-slot=\"button\"]:hover:not(:disabled),[data-slot=\"select-trigger\"]:hover{background:" + INK2 + "!important;color:#f4f0e6!important}"
    "[data-slot=\"button\"]:active:not(:disabled){transform:translate(1px,1px)}"
    f"[data-slot=\"input\"]{{border:1px solid {INK2}!important}}"
    f"[data-slot=\"input\"]:focus-visible,[data-slot=\"select-trigger\"]:focus-visible{{box-shadow:inset 0 0 0 1px {INK2}!important;outline:none!important}}"
    "[data-slot=\"composer-host\"] :focus-visible{outline:none!important}"
    f"[data-slot=\"switch\"]{{border:1px solid {INK2}!important}}"
    "[data-slot=\"switch\"] > span{border-radius:0!important}"
    f"[data-slot=\"menu-popup\"] [role=\"menuitem\"]:hover,[data-slot=\"menu-popup\"] [role=\"menuitem\"]:focus-visible{{background:{INK2}!important;color:#f4f0e6!important}}"
    f"[data-settings-page-scroll] :is(h1,h2,h3){{font-family:{SERIF};letter-spacing:.005em}}"
    "[data-timeline-row-kind=\"work\"]{font-family:" + SERIF + ";font-style:italic}"
    # --- reduced motion: a good still. Swap the animated SVGs for the static ones from out here, and show the
    # working state as a half-filled header bar instead of motion.
    "@media (prefers-reduced-motion:reduce){[data-workspace-area=\"conversation\"],[data-workspace-area=\"conversation\"] .messages-timeline-scroll,[data-chat-header],"
    "[data-thread-item],[data-thread-item] [aria-busy],[data-timeline-row-kind],[data-slot=\"composer-host\"]{transition:none!important;animation:none!important}"
    + busy('[data-slot="sidebar-inner"]::after') + f"{{animation:none!important;background-position:{dock_pos(3)}!important}}"
    + busy('[data-workspace-area="conversation"] .messages-timeline-scroll') + "{animation:none!important;background-position:" + pos_list(NL, 4, CARD_ON, "0 0") + "!important}"
    + busy('[data-workspace-area="conversation"]') + "{animation:none!important;background-position:" + pos_list(4, 1, SCR_ON, "0 0") + "!important}"
    + busy("[data-chat-header]") + "{background-position:50% 100%,0 100%!important}}"
)

theme = {"version": 1, "id": "folio", "name": "Folio", "appearance": "light", "accent": INK2, "canvas": DESK,
         "colors": colors, "css": css}
with open(os.path.join(HERE, "..", "folio.json"), "w") as fh:
    json.dump(theme, fh, ensure_ascii=False)
print("css chars:", len(css))
os.makedirs(os.path.join(HERE, "..", "assets", "svg"), exist_ok=True)
for n, s in (("scrubber", scrub_svg(5)), ("card", card_svg())):
    with open(os.path.join(HERE, "..", "assets", "svg", f"{n}.svg"), "w") as fh:
        fh.write(s)
