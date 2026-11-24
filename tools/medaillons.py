"""Génère les 13 médaillons-plantes des chambres (vert lierre + rose riso), 200 x 200."""
import math, os, sys

L = "#1f3a2f"      # vert lierre
R = "#e0578f"      # rose riso (réservé aux illustrations)
C = "#fbf8f1"      # papier
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "images", "chambres")
os.makedirs(OUT, exist_ok=True)

S = 'stroke="%s" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"' % L
Sf = 'stroke="%s" stroke-width="1.4" stroke-linejoin="round" stroke-linecap="round"' % L


def frame(body, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" role="img" aria-label="{title}">
<defs>
  <clipPath id="in"><circle cx="100" cy="100" r="85"/></clipPath>
  <pattern id="dots" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="2.5" cy="2.5" r="1" fill="{R}" opacity=".55"/></pattern>
  <pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="5" stroke="{R}" stroke-width="1.2" opacity=".6"/></pattern>
</defs>
<circle cx="100" cy="100" r="95" fill="{C}" stroke="{L}" stroke-width="3"/>
<circle cx="100" cy="100" r="87" fill="none" stroke="{R}" stroke-width="1.3"/>
<g clip-path="url(#in)">
{body}
</g>
</svg>
'''


def rot(el, a, cx=100, cy=100):
    return f'<g transform="rotate({a:.1f} {cx} {cy})">{el}</g>'


def wave(y, x0=14, x1=186, amp=4, step=14, color=L, w=1.6):
    d = f"M{x0} {y}"
    x = x0
    up = True
    while x < x1:
        d += f" q{step/2} {-amp if up else amp} {step} 0"
        x += step
        up = not up
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'


m = {}

# 1 Marguerite : le cœur est un livre ouvert, les feuilles sont des pages
petals = "".join(rot(f'<ellipse cx="100" cy="52" rx="8" ry="21" fill="{C}" {S}/>', i * 360 / 15, 100, 82) for i in range(15))
m[1] = ("Marguerite", f'''
<path d="M100 104 C 99 128 101 146 100 176" fill="none" {S}/>
<path d="M100 150 C 90 142 74 142 62 148 L 62 168 C 74 162 90 162 100 170 Z" fill="{R}" {S}/>
<path d="M100 150 C 110 142 126 142 138 148 L 138 168 C 126 162 110 162 100 170 Z" fill="{C}" {S}/>
<path d="M108 152 h20 M108 158 h22 M108 164 h16" {Sf}/>
{petals}
<circle cx="100" cy="82" r="17" fill="{R}" {S}/>
<path d="M88 80 q6 -4 12 0 q6 -4 12 0 v10 q-6 -4 -12 0 q-6 -4 -12 0 z" fill="{C}" {Sf}/>
<path d="M100 80 v10" {Sf}/>
''')

# 2 Capucine : la feuille ronde est une fenêtre à croisillons, la fleur regarde dehors
veins = "".join(f'<line x1="86" y1="90" x2="{86+40*math.cos(math.radians(a)):.1f}" y2="{90+40*math.sin(math.radians(a)):.1f}" {Sf}/>' for a in range(0, 360, 45))
m[2] = ("Capucine", f'''
<path d="M88 96 C 92 130 104 150 100 178" fill="none" {S}/>
<circle cx="86" cy="90" r="42" fill="url(#dots)" {S}/>
{veins}
<path d="M44 90 H128 M86 48 V132" stroke="{L}" stroke-width="3.2" stroke-linecap="round"/>
<circle cx="86" cy="90" r="5" fill="{L}"/>
<path d="M108 170 C 116 160 126 152 136 142" fill="none" {S}/>
<path d="M140 128 C 150 118 158 106 160 92" fill="none" {S}/>
{"".join(rot(f'<path d="M138 140 C 124 128 128 110 138 108 C 148 110 152 128 138 140 Z" fill="{R}" {S}/>', a, 138, 140) for a in (0, 72, 144, 216, 288))}
<circle cx="138" cy="140" r="5" fill="{L}"/>
''')

# 3 Iris : des lignes simples, et une tige-crayon (le bureau face aux arbres)
m[3] = ("Iris", f'''
<path d="M120 172 L134 116 L126 174 Z" fill="none" {S}/>
<rect x="95" y="104" width="10" height="56" fill="{C}" {S}/>
<path d="M95 112 h10 M95 118 h10" stroke="{R}" stroke-width="3"/>
<path d="M100 120 v40" {Sf}/>
<path d="M95 160 L100 176 L105 160 Z" fill="{C}" {S}/>
<path d="M98.4 171 L100 176 L101.6 171 Z" fill="{L}"/>
<path d="M100 100 L86 62 L100 34 L114 62 Z" fill="{C}" {S}/>
<path d="M98 96 L74 70 L72 50 L90 64 Z" fill="{C}" {S}/>
<path d="M102 96 L126 70 L128 50 L110 64 Z" fill="{C}" {S}/>
<path d="M100 98 C 82 94 58 100 54 126 C 68 132 88 122 100 104 Z" fill="{R}" {S}/>
<path d="M100 98 C 118 94 142 100 146 126 C 132 132 112 122 100 104 Z" fill="{R}" {S}/>
<path d="M66 116 C 76 110 86 106 96 102 M134 116 C 124 110 114 106 104 102 M100 48 v34" {Sf}/>
''')

# 4 Cyprès de Lambert : le cyprès sur une portée, deux notes de Chopin
staff = "".join(f'<line x1="10" y1="{y}" x2="190" y2="{y}" stroke="{R}" stroke-width="1.3"/>' for y in range(84, 125, 10))
chev = "".join(f'<path d="M{100-w} {y} L100 {y-7} L{100+w} {y}" fill="none" stroke="{C}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>' for y, w in ((58, 5), (74, 9), (90, 12), (106, 14), (122, 15), (138, 14), (152, 11)))
def note(x, y):
    return f'<ellipse cx="{x}" cy="{y}" rx="6" ry="4.5" transform="rotate(-20 {x} {y})" fill="{R}" {Sf}/><path d="M{x+5} {y-1} V{y-24} q6 6 10 4" fill="none" {S}/>'
m[4] = ("Cyprès de Lambert", f'''
{staff}
{note(56, 112)}{note(144, 96)}
<rect x="96" y="160" width="8" height="12" fill="{L}"/>
<path d="M70 172 H130" {S}/>
<path d="M100 26 C 116 62 124 104 117 146 C 114 160 86 160 83 146 C 76 104 84 62 100 26 Z" fill="{L}" {S}/>
{chev}
''')

# 5 Valériane : l'ombelle boude, tournée vers le lac juste en face
rays = ""
for i in range(7):
    a = math.radians(-150 + i * 20)
    x, y = 100 + 30 * math.cos(a), 98 + 30 * math.sin(a)
    rays += f'<line x1="100" y1="98" x2="{x:.1f}" y2="{y:.1f}" {Sf}/>'
    for dx, dy in ((-5, -2), (5, -2), (0, -8)):
        rays += f'<circle cx="{x+dx:.1f}" cy="{y+dy:.1f}" r="4.2" fill="{R}" {Sf}/>'
m[5] = ("Valériane", f'''
<rect x="0" y="146" width="200" height="60" fill="url(#hatch)"/>
{wave(146)}{wave(160, step=16)}{wave(174, step=18)}
<path d="M100 98 C 104 118 98 134 102 150" fill="none" {S}/>
<path d="M101 122 C 112 112 122 112 132 118 M101 122 C 92 114 80 114 70 120" fill="none" {S}/>
<g transform="rotate(-12 100 98)">{rays}</g>
''')

# 6 Camélia : sous un ciel de lit drapé, tout en rose
outer = "".join(rot(f'<circle cx="100" cy="98" r="15" fill="{R}" {S}/>', a, 100, 120) for a in range(0, 360, 45))
inner = "".join(rot(f'<circle cx="100" cy="108" r="10" fill="{C}" {S}/>', a + 30, 100, 120) for a in range(0, 360, 60))
m[6] = ("Camélia", f'''
<path d="M10 14 H190 V50 Q145 84 100 52 Q55 84 10 50 Z" fill="url(#hatch)" />
<path d="M18 50 Q55 84 100 52 Q145 84 182 50" fill="none" {S}/>
<path d="M30 58 C 40 86 34 108 24 128 M170 58 C 160 86 166 108 176 128" fill="none" {S}/>
<circle cx="100" cy="52" r="4" fill="{R}" {Sf}/>
<path d="M78 150 C 62 150 50 160 46 172 C 60 172 72 164 78 150 Z M122 150 C 138 150 150 160 154 172 C 140 172 128 164 122 150 Z" fill="{L}" {S}/>
{outer}{inner}
<circle cx="100" cy="120" r="6" fill="{R}" {S}/>
''')

# 7 Gentiane : une clochette fermée par un trou de serrure
m[7] = ("Gentiane", f'''
<path d="M100 160 V178" {S}/>
<path d="M98 172 C 84 168 72 156 68 140 C 82 146 92 156 98 172 Z M102 172 C 116 168 128 156 132 140 C 118 146 108 156 102 172 Z" fill="{L}" {S}/>
<path d="M100 162 C 90 150 76 116 72 74 L128 74 C 124 116 110 150 100 162 Z" fill="{R}" {S}/>
<path d="M72 74 L78 58 L88 70 L100 54 L112 70 L122 58 L128 74 Z" fill="{R}" {S}/>
<ellipse cx="100" cy="74" rx="28" ry="7" fill="{C}" {S}/>
<circle cx="100" cy="106" r="8" fill="{C}" {S}/>
<path d="M96 110 L92 130 H108 L104 110 Z" fill="{C}" {S}/>
<circle cx="100" cy="106" r="3" fill="{L}"/>
''')

# 8 Albizia : la fleur pompon sur une carte postale jamais envoyée
fil = ""
for i in range(26):
    a = math.radians(-180 + i * 7.2)
    ln = 20 + (i % 3) * 3
    x, y = 70 + ln * math.cos(a), 96 + ln * math.sin(a)
    fil += f'<line x1="70" y1="96" x2="{x:.1f}" y2="{y:.1f}" stroke="{R}" stroke-width="1.5" stroke-linecap="round"/><circle cx="{x:.1f}" cy="{y:.1f}" r="1.7" fill="{L}"/>'
leaflets = "".join(f'<path d="M{x} 124 l-3 -6 M{x} 124 l-3 6" {Sf}/>' for x in range(60, 92, 6))
m[8] = ("Albizia", f'''
<g transform="rotate(-8 100 100)">
<rect x="34" y="54" width="132" height="92" fill="{C}" {S}/>
<path d="M106 62 V138" {Sf}/>
<path d="M114 106 h40 M114 116 h40 M114 126 h30" {Sf}/>
<rect x="134" y="62" width="22" height="26" fill="{R}" stroke="{L}" stroke-width="1.4" stroke-dasharray="2 2"/>
<path d="M120 76 q6 -4 12 0 q6 4 12 0 q6 -4 12 0 M120 84 q6 -4 12 0 q6 4 12 0 q6 -4 12 0" fill="none" {Sf}/>
<path d="M70 96 C 72 112 70 128 74 138" fill="none" {S}/>
<path d="M56 124 H94" {Sf}/>{leaflets}
{fil}
<circle cx="70" cy="96" r="3" fill="{L}"/>
</g>
''')

# 9 Dahlia : à minuit, son cœur reste allumé
outer = "".join(rot(f'<path d="M100 66 C 109 80 108 94 100 102 C 92 94 91 80 100 66 Z" fill="{C}" {S}/>', a, 100, 110) for a in range(0, 360, 24))
inner = "".join(rot(f'<path d="M100 86 C 106 94 106 102 100 108 C 94 102 94 94 100 86 Z" fill="{R}" {S}/>', a + 12, 100, 110) for a in range(0, 360, 30))
glow = "".join(rot('<line x1="100" y1="56" x2="100" y2="48" stroke="%s" stroke-width="2" stroke-linecap="round"/>' % R, a, 100, 110) for a in range(-60, 61, 30))
m[9] = ("Dahlia", f'''
<path d="M150 30 A 20 20 0 1 0 168 62 A 16 16 0 1 1 150 30 Z" fill="{R}" {S}/>
<path d="M44 40 v8 M40 44 h8 M70 26 v6 M67 29 h6 M168 96 v6 M165 99 h6" {Sf}/>
<path d="M100 140 C 98 154 102 164 100 180" fill="none" {S}/>
{glow}{outer}{inner}
<circle cx="100" cy="110" r="8" fill="{L}"/><circle cx="100" cy="110" r="3" fill="{C}"/>
''')

# 10 Suite Herbelon : la tour, d'où vient la famille, prise dans le lierre
def ivy(x, y, a, fill):
    return f'<path d="M{x} {y} c -6 -2 -9 -8 -6 -12 c 3 1 4 2 6 4 c 1 -4 3 -7 6 -8 c 2 4 1 7 0 9 c 3 -1 6 -1 8 1 c -3 5 -9 7 -14 6 z" transform="rotate({a} {x} {y})" fill="{fill}" {Sf}/>'
m[10] = ("Suite Herbelon", f'''
<path d="M40 170 H160" {S}/>
<rect x="78" y="66" width="44" height="104" fill="{C}" {S}/>
<path d="M72 66 H128 L100 28 Z" fill="{L}" {S}/>
<path d="M100 28 V12" {S}/>
<path d="M100 12 L124 18 L100 24 Z" fill="{R}" {Sf}/>
<path d="M92 104 v-10 a8 8 0 0 1 16 0 v10 z" fill="{L}"/>
<path d="M90 170 v-18 a10 10 0 0 1 20 0 v18" fill="none" {S}/>
<path d="M76 168 C 70 150 86 140 80 124 C 74 108 90 98 84 84 C 80 74 90 70 92 66" fill="none" stroke="{L}" stroke-width="1.6"/>
{ivy(78,154,-20,R)}{ivy(82,134,30,L)}{ivy(80,114,-30,R)}{ivy(86,94,20,L)}{ivy(88,76,-10,R)}
<path d="M95 116 v16 M105 116 v16 M95 124 h10" stroke="{R}" stroke-width="2.6" stroke-linecap="round" fill="none"/>
''')

# 11 Trèfle : quatre feuilles en plein vent (et quatre alcôves)
heart = f'<path d="M100 92 C 88 84 80 70 86 60 C 92 52 100 56 100 64 C 100 56 108 52 114 60 C 120 70 112 84 100 92 Z" fill="{R}" {S}/><path d="M100 92 V66" {Sf}/>'
m[11] = ("Trèfle", f'''
<path d="M26 64 q22 -10 44 0 q8 4 2 10 M20 84 q18 -8 36 0 M150 132 q14 -6 28 0 q6 3 2 8" fill="none" stroke="{L}" stroke-width="1.6" stroke-dasharray="5 4" stroke-linecap="round"/>
<path d="M100 96 C 104 124 98 150 108 176" fill="none" {S}/>
{"".join(rot(heart, a, 100, 96) for a in (10, 100, 190, 280))}
<circle cx="100" cy="96" r="3" fill="{L}"/>
''')

# 12 Magnolia : six pétales grand ouverts, de la place pour tout le monde
pet = lambda f: f'<path d="M100 130 C 86 104 88 72 100 56 C 112 72 114 104 100 130 Z" fill="{f}" {S}/>'
m[12] = ("Magnolia", f'''
<path d="M100 132 C 98 150 86 162 64 176" fill="none" stroke="{L}" stroke-width="5" stroke-linecap="round"/>
<path d="M88 156 C 104 150 120 154 132 166 C 116 170 100 168 88 156 Z" fill="{L}" {S}/>
<path d="M92 157 C 106 158 118 162 128 166" fill="none" stroke="{C}" stroke-width="1.3"/>
{"".join(rot(pet(R if i % 2 else C), a, 100, 130) for i, a in enumerate((-70, -42, -14, 14, 42, 70)))}
<path d="M94 118 L100 92 L106 118 Z" fill="{L}" {S}/>
''')

# 13 Églantine : une tige-échelle pour monter dans ses appartements
rose = "".join(rot(f'<path d="M100 66 C 88 56 88 40 100 40 C 112 40 112 56 100 66 Z" fill="{R}" {S}/>', a, 100, 66) for a in range(0, 360, 72))
rungs = "".join(f'<path d="M93 {y} H107" {S}/>' for y in range(98, 176, 13))
m[13] = ("Églantine", f'''
<path d="M93 88 V178 M107 88 V178" {S}/>
{rungs}
<path d="M93 124 C 80 120 70 124 62 132 C 74 138 86 134 93 124 Z M107 150 C 120 146 130 150 138 158 C 126 164 114 160 107 150 Z" fill="{L}" {S}/>
{rose}
<circle cx="100" cy="66" r="9" fill="{C}" {S}/>
{"".join(f'<circle cx="{100+5*math.cos(math.radians(a)):.1f}" cy="{66+5*math.sin(math.radians(a)):.1f}" r="1.4" fill="{L}"/>' for a in range(0,360,45))}
''')

for n, (name, body) in m.items():
    with open(os.path.join(OUT, f"{n:02d}.svg"), "w", encoding="utf-8") as f:
        f.write(frame(body, name))
print("ok", len(m))
