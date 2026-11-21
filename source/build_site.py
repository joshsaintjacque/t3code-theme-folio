"""Generate index.html from folio.json so the palette table always matches the theme file."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
t = json.load(open(os.path.join(HERE, "..", "folio.json")))
c = t["colors"]
SITE = "https://joshsaintjacque.github.io/t3code-theme-folio/"
rows = [("canvas", "The desk around the page"), ("chrome", "Window chrome"), ("sidebar", "Thread list"),
        ("surface", "Composer"), ("messageSurface", "Your messages"), ("codeBackground", "Code blocks"),
        ("text", "Ink"), ("textMuted", "Pencil notes"), ("border", "Hairlines"), ("accent", "Send, focus, selection"),
        ("error", "Errors"), ("warning", "Warnings"), ("update", "Updates")]
tr = "".join(
    f"<tr tabindex='0' role='button' data-hex='{c[k].upper()}' aria-label='Copy {c[k].upper()}'><td><i style='background:{c[k]}'></i></td>"
    f"<th scope='row'>{k}</th><td class='use'>{u}</td><td class='hx'>{c[k].upper()}</td></tr>" for k, u in rows)
html = open(os.path.join(HERE, "site.template.html")).read().replace("__PALETTE__", tr).replace("__SITE__", SITE)
open(os.path.join(HERE, "..", "index.html"), "w").write(html)
print("index.html", len(html))
