"""Build light_mode.svg and dark_mode.svg for PedroPini/PedroPini,
mirroring Andrew6rant's layout: ASCII-art portrait left, neofetch-style info right.

Usage (only needed when changing the photo or the static info lines;
the GitHub Action updates the stats without this script):
    pip install pillow
    curl -L "https://github.com/PedroPini.png?size=460" -o avatar.png
    python build_svgs.py
Values must be short enough that each line fits in 60 characters;
the script errors out if a line is too long.
"""
import os
from PIL import Image, ImageEnhance, ImageOps
from xml.sax.saxutils import escape

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
AVATAR = os.path.join(OUT_DIR, "avatar.png")
ROWS, COLS = 25, 38
CELL_ASPECT = 20 / 8.8
RAMP_LIGHT = "@$#%WMB8&gm*aoezr|;:~-,. "
RAMP_DARK = RAMP_LIGHT[::-1]
WIDTH = 60  # visible chars per info line, same as Andrew's


def ascii_lines(ramp):
    img = Image.open(AVATAR).convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    w, h = img.size
    needed_w = int(h * (COLS / (ROWS * CELL_ASPECT)))
    if needed_w < w:
        left = (w - needed_w) // 2
        img = img.crop((left, 0, left + needed_w, h))
    img = img.resize((COLS, ROWS), Image.LANCZOS)
    px = img.load()
    return [
        "".join(ramp[min(px[x, y] * len(ramp) // 256, len(ramp) - 1)] for x in range(COLS)).rstrip()
        for y in range(ROWS)
    ]


def key_markup(key):
    """Languages.Real -> <tspan class="key">Languages</tspan>.<tspan class="key">Real</tspan>"""
    return ".".join(f'<tspan class="key">{escape(part)}</tspan>' for part in key.split("."))


def dots_for(key, value):
    n = WIDTH - 2 - len(key) - 1 - 2 - len(value)
    assert n >= 0, f"line too long: {key}: {value}"
    return "." * n


def info_line(y, key, value, dots_id=None, value_id=None):
    dots = dots_for(key, value)
    did = f' id="{dots_id}"' if dots_id else ""
    vid = f' id="{value_id}"' if value_id else ""
    return (
        f'<tspan x="390" y="{y}" class="cc">. </tspan>{key_markup(key)}:'
        f'<tspan class="cc"{did}> {dots} </tspan>'
        f'<tspan class="value"{vid}>{escape(value)}</tspan>'
    )


def blank_line(y):
    return f'<tspan x="390" y="{y}" class="cc">. </tspan>'


def header_line(y, text, dashes):
    return f'<tspan x="390" y="{y}">{escape(text)}</tspan> {dashes}'


def jdots(length, value):
    """Same as today.py justify_format: field width `length`, pad with dots."""
    n = max(0, length - len(value))
    return {0: "", 1: " ", 2: ". "}.get(n, " " + "." * n + " ")


def stat_lines():
    repos, contrib, stars, commits, followers = "104", "104", "14", "0", "14"
    loc, loc_add, loc_del = "0", "0", "0"
    l1 = (
        f'<tspan x="390" y="470" class="cc">. </tspan><tspan class="key">Repos</tspan>:'
        f'<tspan class="cc" id="repo_data_dots">{jdots(6, repos)}</tspan>'
        f'<tspan class="value" id="repo_data">{repos}</tspan> '
        f'{{<tspan class="key">Contributed</tspan>: <tspan class="value" id="contrib_data">{contrib}</tspan>}} | '
        f'<tspan class="key">Stars</tspan>:'
        f'<tspan class="cc" id="star_data_dots">{jdots(14, stars)}</tspan>'
        f'<tspan class="value" id="star_data">{stars}</tspan>'
    )
    l2 = (
        f'<tspan x="390" y="490" class="cc">. </tspan><tspan class="key">Commits</tspan>:'
        f'<tspan class="cc" id="commit_data_dots">{jdots(23, commits)}</tspan>'
        f'<tspan class="value" id="commit_data">{commits}</tspan> | '
        f'<tspan class="key">Followers</tspan>:'
        f'<tspan class="cc" id="follower_data_dots">{jdots(10, followers)}</tspan>'
        f'<tspan class="value" id="follower_data">{followers}</tspan>'
    )
    l3 = (
        f'<tspan x="390" y="510" class="cc">. </tspan><tspan class="key">Lines of Code on GitHub</tspan>:'
        f'<tspan class="cc" id="loc_data_dots">{jdots(9, loc)}</tspan>'
        f'<tspan class="value" id="loc_data">{loc}</tspan> ( '
        f'<tspan class="addColor" id="loc_add">{loc_add}</tspan><tspan class="addColor">++</tspan>, '
        f'<tspan id="loc_del_dots">{jdots(7, loc_del)}</tspan>'
        f'<tspan class="delColor" id="loc_del">{loc_del}</tspan><tspan class="delColor">--</tspan> )'
    )
    return [l1, l2, l3]


THEMES = {
    "light_mode.svg": {
        "ramp": RAMP_LIGHT,
        "bg": "#f6f8fa", "fg": "#24292f",
        "key": "#953800", "value": "#0a3069",
        "add": "#1a7f37", "del": "#cf222e", "cc": "#c2cfde",
    },
    "dark_mode.svg": {
        "ramp": RAMP_DARK,
        "bg": "#161b22", "fg": "#c9d1d9",
        "key": "#ffa657", "value": "#a5d6ff",
        "add": "#3fb950", "del": "#f85149", "cc": "#616e7f",
    },
}

# name header is 2 chars shorter than andrew@grant, so 2 extra em-dashes
NAME_DASHES = "-—————————————————————————————————————————————-—-"
CONTACT_DASHES = "-——————————————————————————————————————————————-—-"
STATS_DASHES = "-—————————————————————————————————————————-—-"

for filename, t in THEMES.items():
    art = "\n".join(
        f'<tspan x="15" y="{30 + i * 20}">{escape(line)}</tspan>'
        for i, line in enumerate(ascii_lines(t["ramp"]))
    )
    info = [
        header_line(30, "pedro@pini", NAME_DASHES),
        info_line(50, "OS", "macOS, Linux"),
        info_line(70, "Uptime", "31 years, 6 months, 9 days", "age_data_dots", "age_data"),
        info_line(90, "Host", "Perth, Western Australia"),
        info_line(110, "Kernel", "Software Engineer"),
        info_line(130, "IDE", "Kiro, Antigravity"),
        blank_line(150),
        info_line(170, "Languages.Programming", "JavaScript, TypeScript, Python"),
        info_line(190, "Languages.Computer", "Next.js, CSS, SQL, JSON, YAML"),
        info_line(210, "Languages.Real", "Portuguese, English"),
        blank_line(230),
        info_line(250, "Hobbies.Software", "AI & Automation Experiments"),
        info_line(270, "Hobbies.Content", "YouTube (@askpedro)"),
        header_line(310, "- Contact", CONTACT_DASHES),
        info_line(330, "Email.Personal", "pedropini.tech@gmail.com"),
        info_line(350, "Website", "pedropini.com"),
        info_line(370, "LinkedIn", "pedropini"),
        info_line(390, "YouTube", "@askpedro"),
        header_line(450, "- GitHub Stats", STATS_DASHES),
        *stat_lines(),
    ]
    svg = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="985px" height="530px" font-size="16px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {t["key"]};}}
.value {{fill: {t["value"]};}}
.addColor {{fill: {t["add"]};}}
.delColor {{fill: {t["del"]};}}
.cc {{fill: {t["cc"]};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="985px" height="530px" fill="{t["bg"]}" rx="15"/>
<text x="15" y="30" fill="{t["fg"]}" class="ascii">
{art}
</text>
<text x="390" y="30" fill="{t["fg"]}">
{chr(10).join(info)}
</text>
</svg>"""
    path = f"{OUT_DIR}/{filename}"
    with open(path, "w") as f:
        f.write(svg)
    print("wrote", path)
