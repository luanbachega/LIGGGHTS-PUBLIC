"""Pranchas do 153 no padrão T & L (mesma identidade dos estudos 151)."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'estudo-151-studios', 'gerador'))
import pymupdf
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle
import render as R            # helpers do 151 (Overlay, redact, br, mi, stamp de Marielen)
import model153 as M

br, mi, W, H = R.br, R.mi, R.W, R.H
TEMPLATE = R.SRC['A']
NAVY = R.NAVY
REV, DATE = 'R00', 'out.26'
ADDR = 'R. Alexandre Wisocki, 249 – Fazenda Velha – Araucária/PR'

C_LOT = (0.89, 0.93, 0.82)      # jardim / permeável
C_PAVE = (0.99, 0.83, 0.50)     # circulação / estacionamento
C_LAZ = (0.70, 0.69, 0.84)      # lazer
C_RAMP = (0.97, 0.75, 0.54)
C_CORE = (0.84, 0.84, 0.89)
C_2Q = (0.93, 0.95, 0.77)
C_3Q = (0.80, 0.90, 0.80)
C_ST = (0.98, 0.89, 0.68)
C_VAGA = (0.79, 0.64, 0.29)
EDGE = (0.33, 0.33, 0.33)
GREY, TXT = R.GREY, R.TXT
NORTH = (0.656, -0.755)          # norte em coordenadas locais (frente = eixo x)


# ------------------------------------------------------------------ moldura / carimbo
def blank(page, title):
    R.redact(page, [(0, 0, W, 735), (560, 725, 1108, 841), (560, 812, 1170, 841)])
    ov = R.Overlay()
    ov.text(977.9, 739.8, title, size=13, color=TXT, ha='right')
    ov.text(977.9, 768.2, '153 •  Estudo de Viabilidade', size=11, weight='bold', color=TXT, ha='right')
    return ov


def stamp(ov, sub):
    ov.text(977.9, 786.6, f"{sub}  .  {REV}     {DATE}", size=8.5, color=TXT, ha='right')
    ov.text(1158.8, 819.2, 'a viabilidade técnico-legal do estudo deve ser confirmada através de consulta formal junto aos órgãos '
            'públicos e da confrontação com levantamento planialtimétrico a ser fornecido pelo proprietário',
            size=4.8, color=GREY, ha='right')
    ov.line(206, 776, 206, 797, lw=0.4, color='#9aa3ad')
    ov.text(214, 783.5, 'Marielen Ferri', size=8.0, weight='bold', color='#1e3556')
    ov.text(214, 793.7, 'Arquitetura', size=6.5, color=GREY)


def cover(page, sub):
    R.redact(page, [(440, 576, 750, 626)], fill=NAVY)
    ov = R.Overlay()
    ov.text(W / 2, 592.5, sub, size=11, color='white', ha='center')
    ov.text(W / 2, 617.0, ADDR, size=8.5, color='#c9d2df', ha='center')
    ov.apply(page)


# ------------------------------------------------------------------ desenho em planta (coord. locais)
class Plan:
    def __init__(self, ov, ox, oy, s):
        self.ov, self.ox, self.oy, self.s = ov, ox, oy, s

    def P(self, x, y):
        return (self.ox + self.s * x, self.oy - self.s * y)

    def poly(self, pts, fc='none', ec=EDGE, lw=0.35, ls='-', alpha=1, hatch=None, z=1):
        self.ov.ax.add_patch(MPoly([self.P(*p) for p in pts], closed=True, fc=fc, ec=ec, lw=lw, ls=ls,
                                   alpha=alpha, hatch=hatch, zorder=z))

    def rect(self, x0, y0, x1, y1, **kw):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], **kw)

    def text(self, x, y, s, size=5.0, **kw):
        px, py = self.P(x, y)
        kw.setdefault('ha', 'center'); kw.setdefault('va', 'center'); kw.setdefault('color', TXT)
        self.ov.ax.text(px, py, s, fontsize=size, **kw)

    def line(self, a, b, lw=0.35, color=EDGE, ls='-'):
        pa, pb = self.P(*a), self.P(*b)
        self.ov.ax.plot([pa[0], pb[0]], [pa[1], pb[1]], lw=lw, color=color, ls=ls)


def north(ov, cx, cy, r=16):
    ov.ax.add_patch(Circle((cx, cy), r, fc='none', ec='#222222', lw=0.6))
    dx, dy = NORTH[0], -NORTH[1]
    ov.ax.annotate('', xy=(cx + dx * r, cy + dy * r), xytext=(cx - dx * r, cy - dy * r),
                   arrowprops=dict(arrowstyle='-|>', lw=0.8, color='#222222'))
    ov.text(cx + dx * (r + 7), cy + dy * (r + 7), 'N', size=8, weight='bold', ha='center', va='center')


def scalebar(ov, x, y, s):
    for i, (a, b) in enumerate([(0, 5), (5, 10), (10, 20)]):
        ov.rect(x + a * s, y, x + b * s, y + 3, fc='#333333' if i != 1 else 'white', ec='#333333', lw=0.4)
    for v in (0, 5, 10, 20):
        ov.text(x + v * s, y - 3, str(v), size=5, ha='center')
    ov.text(x, y + 12, 'escala 1:500  (m)', size=5.5)


def dim(pl, a, b, txt, off=1.6, size=4.6):
    ax_, ay = a; bx, by = b
    dx, dy = bx - ax_, by - ay
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * off, dx / L * off
    pl.line((ax_ + nx, ay + ny), (bx + nx, by + ny), lw=0.3, color='#555555')
    for p in (a, b):
        pl.line((p[0] + nx * 0.4, p[1] + ny * 0.4), (p[0] + nx * 1.25, p[1] + ny * 1.25), lw=0.3, color='#555555')
    ang = math.degrees(math.atan2(dy, dx))
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    pl.text((ax_ + bx) / 2 + nx * 1.9, (ay + by) / 2 + ny * 1.9, txt, size=size, rotation=ang, color='#333333')


def site(pl, o, level='terreo'):
    """lote + entorno + recuos (comum a térreo e subsolo)."""
    LOT = M.LOT
    if level == 'terreo':
        pl.rect(-14, -17, 38, -1.0, fc=(0.95, 0.95, 0.95), ec=(0.73, 0.73, 0.73))
        pl.text(12, -9, 'RUA ALEXANDRE WISOCKI (16,00)', size=5.0, color=GREY)
        # Rua Zdenko Gayer (fundos) – trecho de 19,26 m
        b1, b2 = M.B1, M.B2
        n = (8.5 / 25.46, 24 / 25.46)
        pl.poly([b1, b2, (b2[0] + n[0] * 14, b2[1] + n[1] * 14), (b1[0] + n[0] * 14, b1[1] + n[1] * 14)],
                fc=(0.95, 0.95, 0.95), ec=(0.73, 0.73, 0.73))
        pl.text((b1[0] + b2[0]) / 2 + n[0] * 8, (b1[1] + b2[1]) / 2 + n[1] * 8, 'RUA ZDENKO GAYER', size=4.6,
                color=GREY, rotation=-19.5)
        pl.text(-10.5, 33, 'LOTE 10', size=5.0, color=GREY, rotation=90)
        pl.text(34.5, 30, 'LOTE 07', size=5.0, color=GREY, rotation=90)
        pl.text(2.5, 72.5, 'lote 03\nqd. H', size=4.2, color=GREY)
        pl.text(26.5, 61.5, 'lote 01\nqd. C', size=4.2, color=GREY)
    pl.poly(LOT, fc=C_LOT if level == 'terreo' else (0.97, 0.97, 0.97), ec='#222222', lw=0.7, z=2 if level != 'terreo' else 1)


def terreo(pl, o):
    site(pl, o, 'terreo')
    Lt = o['L']
    # fundos: lazer descoberto
    yb0 = max(M.Y_T0 + Lt + 1.0, o['aisle_end'] + o['back_off'] - 1.5)
    pl.poly([(4.0, yb0), (24.0, yb0), (24.0, M.y_back(24)), (4.0, M.y_back(4))], fc=C_LAZ, ec='none', z=2)
    pl.text(13, (yb0 + M.y_back(13)) / 2, 'Lazer', size=5.5)
    # estacionamento / circulação sob pilotis
    pl.rect(9.0, 5.0, 14.0, yb0, fc=C_PAVE, ec='none', z=2)          # corredor
    pl.rect(9.0, 5.0, 19.0, 10.0, fc=C_PAVE, ec='none', z=2)         # acesso transversal
    pl.rect(19.0, 0.0, 24.0, 10.0, fc=C_PAVE, ec='none', z=2)        # acesso de veículos
    pl.rect(19.0, 10.0, 24.0, 28.0, fc=C_RAMP, ec=EDGE, lw=0.3, z=2)  # rampa
    pl.text(21.5, 19, 'rampa\n↓ subsolo', size=4.2)
    used = set(o['ground'])
    for r in o['g_all']:
        if r in used:
            pl.rect(r[0], r[1], r[2], r[3], fc=C_PAVE, ec=C_VAGA, lw=0.3, z=3)
        else:
            pl.rect(r[0], r[1], r[2], r[3], fc=C_LAZ, ec='none', z=3)
    # torre (projeção) + hall
    yc = o['y_core']
    pl.rect(4.0, yc - 3.0, 9.0, yc + M.CORE + 3.0, fc=C_CORE, ec=EDGE, z=4)
    pl.text(6.5, yc + 1.9, 'hall', size=4.4)
    pl.rect(4.0, M.Y_T0, 19.0, M.Y_T0 + Lt, fc='none', ec='#333333', lw=0.5, ls=(0, (2, 1)), z=5)
    pl.text(11.5, M.Y_T0 + Lt - 2.0, 'projeção da torre', size=4.4, color='#333333')
    # guarita / lixo / gás no recuo
    pl.rect(9.5, 0.6, 17.5, 3.6, fc=(0.81, 0.81, 0.81), ec=(0.47, 0.47, 0.47), z=4)
    pl.text(13.5, 2.1, 'guarita • lixo • gás', size=3.8)
    # passeio de pedestres
    pl.rect(0.6, 0.0, 2.1, yc, fc=(0.96, 0.9, 0.77), ec='none', z=3)
    # recuos
    pl.line((0, 5), (24, 5), lw=0.4, color=(0.44, 0.66, 0.86), ls=(0, (3, 2)))
    b1, b2 = M.B1, M.B2
    n = (-8.5 / 25.46, -24 / 25.46)
    pl.line((b1[0] + 5 * n[0], b1[1] + 5 * n[1]), (b2[0] + 5 * n[0], b2[1] + 5 * n[1]), lw=0.4,
            color=(0.44, 0.66, 0.86), ls=(0, (3, 2)))
    for x in (o['afast'], 24 - o['afast']):
        pl.line((x, 5), (x, M.y_back(x) - 1), lw=0.3, color=(0.75, 0.4, 0.4), ls=(0, (1, 2)))
    # acessos
    for (x, t) in ((1.35, 'ACESSO\nPRINCIPAL'), (21.5, 'ACESSO\nVEÍCULOS')):
        px, py = pl.P(x, 0)
        pl.ov.ax.annotate('', xy=(px, py), xytext=(px, py + 20), arrowprops=dict(arrowstyle='-|>', lw=0.6, color='black'))
        pl.ov.text(px, py + 29, t, size=4.2, ha='center', color='black', linespacing=1.1)
    # cotas
    dim(pl, (0, 0), (24, 0), '24,00', off=-2.2)
    dim(pl, (24, 0), (24, M.L_NE), '59,25', off=-2.4)
    dim(pl, (0, M.L_SW), (0, 0), '67,75', off=-2.4)
    dim(pl, M.B1, M.B2, '19,26', off=-2.0)
    pl.line((0, 0), (0, 0))


def subsolo(pl, o, lvl):
    site(pl, o, 'sub')
    ae, bo = o['aisle_end'], o['back_off']
    poly = [(4.0, 5.0), (24.0, 5.0), (24.0, M.y_back(24) - bo), (4.0, M.y_back(4) - bo)]
    pl.poly(poly, fc=(0.99, 0.92, 0.75), ec='#222222', lw=0.6, z=3)
    pl.rect(9.0, 5.0, 14.0, ae, fc=C_PAVE, ec='none', z=4)
    if lvl == 0:
        pl.rect(19.0, 10.0, 24.0, 28.0, fc=C_RAMP, ec=EDGE, lw=0.3, z=4)
        pl.rect(14.0, 28.0, 24.0, 33.0, fc=C_PAVE, ec='none', z=4)
        pl.text(21.5, 19, 'rampa', size=4.0)
        if o['nsub'] > 1:
            pl.rect(19.0, 33.0, 24.0, 51.0, fc=C_RAMP, ec=EDGE, lw=0.3, z=4)
            pl.text(21.5, 42, 'rampa\n↓ S2', size=4.0)
        else:
            pl.rect(19.0, 33.0, 24.0, M.y_back(24) - bo, fc=(0.85, 0.85, 0.85), ec=EDGE, lw=0.3, z=4)
            pl.text(21.5, 45, 'técnica\nreserv.\nbicicl.', size=3.8)
    else:
        pl.rect(14.0, 51.0, 24.0, 56.0, fc=C_PAVE, ec='none', z=4)
        pl.rect(19.0, 5.0, 24.0, 51.0, fc=(0.85, 0.85, 0.85), ec=EDGE, lw=0.3, z=4)
        pl.text(21.5, 28, 'técnica\nbicicl.', size=3.8)
    for r in o['sub'][lvl]:
        pl.rect(r[0], r[1], r[2], r[3], fc=(0.99, 0.92, 0.75), ec=C_VAGA, lw=0.3, z=5)
    yc = o['y_core']
    pl.rect(4.0, yc, 9.0, yc + M.CORE, fc=C_CORE, ec=EDGE, z=6)


# ------------------------------------------------------------------ pavimento tipo (1:250, horizontal)
def tipo(ov, o, kind, x0, y0, s):
    L, Wt, S, du, c = o['L'], M.W_T, o['S'], o['du'], M.CORR
    X = lambda u: x0 + u * s
    Y = lambda v: y0 + v * s

    def box(u0, u1, v0, v1, fc, lab=None, fs=4.6):
        ov.rect(X(u0), Y(v0), X(u1), Y(v1), fc=fc, ec=EDGE, lw=0.35)
        if lab:
            ov.text((X(u0) + X(u1)) / 2, (Y(v0) + Y(v1)) / 2, lab, size=fs, ha='center', va='center', linespacing=1.2)

    alas = o['FLOORS'][kind]
    wings = [(0.0, S, 0), (0.0, S, 1), (S + M.CORE, L, 0), (S + M.CORE, L, 1)]   # (u0,u1,row)
    for (u0, u1, row), al in zip(wings, alas):
        v0, v1 = (0.0, du) if row == 0 else (du + c, Wt)
        items = o['AL'][al]
        tot = sum(a for _, a in items)
        left = u0 < S
        seq = items if not left else list(reversed(items))     # 2Q junto ao núcleo, 3Q na ponta
        u = u0
        for t, a in seq:
            w = (u1 - u0) * a / tot
            fc = {'2Q': C_2Q, '3Q': C_3Q, 'ST': C_ST}[t]
            lab = {'2Q': 'Ap. 2Q', '3Q': 'Ap. 3Q', 'ST': 'Studio'}[t] + f"\n{br(a)}m²"
            box(u, u + w, v0, v1, fc, lab, 4.3 if t == 'ST' else 4.6)
            u += w
    box(0, S, du, du + c, C_PAVE, 'Circulação', 4.0)
    box(S + M.CORE, L, du, du + c, C_PAVE, 'Circulação', 4.0)
    box(S, S + M.CORE, 0, Wt, C_CORE, 'Hall\nescada\nelev.', 4.2)


def rooftop(ov, o, x0, y0, s):
    L, Wt = o['L'], M.W_T
    at = o['atico']
    ul = at / Wt
    u0 = (L - ul) / 2
    ov.rect(x0, y0, x0 + L * s, y0 + Wt * s, fc=(0.95, 0.9, 0.77), ec=EDGE)
    ov.rect(x0 + u0 * s, y0, x0 + (u0 + ul) * s, y0 + Wt * s, fc=(0.91, 0.94, 0.69), ec=EDGE)
    ov.text(x0 + (u0 + ul / 2) * s, y0 + Wt * s / 2, f"Salão de festas / gourmet\n(ático {br(at)} m² ≤ 1/3)", size=4.6,
            ha='center', va='center')
    ov.text(x0 + u0 * s / 2, y0 + Wt * s / 2, 'Terraço / lazer', size=4.6, ha='center', va='center')
    ov.text(x0 + (u0 + ul + (L - u0 - ul) / 2) * s, y0 + Wt * s / 2, 'Terraço / lazer', size=4.6, ha='center', va='center')


def occupation(page, o, sub):
    ov = blank(page, 'Estudo de ocupação')
    s5 = 72 / 25.4 * 2            # 1:500
    s25 = s5 * 2                  # 1:250
    north(ov, 52, 92)
    pl = Plan(ov, 92, 520, s5)
    terreo(pl, o)
    ov.text(92 + 12 * s5, 640, 'Pavimento Térreo', size=11, color='black', ha='center')
    if o['nsub']:
        pl2 = Plan(ov, 300, 520, s5)
        subsolo(pl2, o, 0)
        nm = 'Subsolo' if o['nsub'] == 1 else 'Subsolos S1 e S2 (S1 mostrado)'
        ov.text(300 + 12 * s5, 640, nm, size=11, color='black', ha='center')
        ov.text(300 + 12 * s5, 652, f"{o['nsub_v']} vagas" + (f" ({len(o['sub'][0])} + {len(o['sub'][1])})" if o['nsub'] > 1 else ''),
                size=7, color=GREY, ha='center')
    scalebar(ov, 34, 700, s5)
    # coluna direita: tipos + rooftop
    kinds = sorted(set(o['seq']))
    names = {'A': 'Pavimento Tipo 2Q + 3Q', 'B': 'Pavimento Tipo 2Q c/ suíte', 'M': 'Pavimento Tipo misto 2Q + studios',
             'S': 'Pavimento Tipo studios + 2Q'}
    panels = [(k, names[k] + f"  ({o['seq'].count(k)}x)") for k in kinds] + [('R', 'Rooftop – ático')]
    x0 = 1160 - o['L'] * s25
    y = 70
    gap = (650 - 70) / len(panels)
    for k, t in panels:
        if k == 'R':
            rooftop(ov, o, x0, y, s25)
        else:
            tipo(ov, o, k, x0, y, s25)
        ov.text(x0 + o['L'] * s25 / 2, y + M.W_T * s25 + 18, t, size=10, color='black', ha='center')
        y += gap
    # legenda
    ly = 668
    for i, (c, t) in enumerate([(C_2Q, 'Ap. 2 quartos'), (C_3Q, 'Ap. 3 quartos'),
                                (C_ST, 'Studio – ambiente único ≤ 30 m² úteis + banho (LC 26/2020, art. 258)'),
                                (C_LAZ, 'Lazer'), (C_LOT, 'Jardim / área permeável')]):
        if (c == C_3Q and not o['n3']) or (c == C_ST and not o['nst']) or (c == C_2Q and not o['n2']):
            continue
        ov.rect(560 + 0, ly - 5, 569, ly + 1, fc=c, ec=EDGE)
        ov.text(573, ly, t, size=5.4)
        ly += 9
    ov.text(560, ly + 6, 'Linhas tracejadas azuis: recuo frontal de 5,00 m (as duas testadas). Pontilhado vermelho: afastamento '
            f"H/8 = {br(o['afast'])} m.", size=5.0, color=GREY)
    stamp(ov, sub)
    ov.apply(page)


# ------------------------------------------------------------------ diagrama axonométrico
def diagram(page, o, sub):
    ov = blank(page, 'Diagrama')
    ov.text(34.0, 82.2, 'DIAGRAMA', size=30, weight='bold', color='#6e6e6e')
    phi = math.radians(-38)
    s, k = 8.4, 0.55
    ox, oy = 610, 625

    def P(x, y, z=0.0):
        X = x * math.cos(phi) - y * math.sin(phi)
        Y = x * math.sin(phi) + y * math.cos(phi)
        return (ox + s * X, oy - s * (Y * k + z))

    def depth(x, y):
        return x * math.sin(phi) + y * math.cos(phi)

    def face(pts3, fc, ec=EDGE, lw=0.35, z=1):
        ov.ax.add_patch(MPoly([P(*p) for p in pts3], closed=True, fc=fc, ec=ec, lw=lw, zorder=z))

    LOT = M.LOT
    # laje do terreno
    for a, b in zip(LOT, LOT[1:] + LOT[:1]):
        mx, my = (a[0] + b[0]) / 2 - 12, (a[1] + b[1]) / 2 - 33
        nx, ny = b[1] - a[1], -(b[0] - a[0])
        if (nx * math.sin(phi) + ny * math.cos(phi)) < 0:
            face([(a[0], a[1], 0), (b[0], b[1], 0), (b[0], b[1], -2.2), (a[0], a[1], -2.2)], (0.1, 0.1, 0.1), (0, 0, 0))
    face([(x, y, 0) for x, y in LOT], (0.91, 0.91, 0.91), (0, 0, 0))
    g = [(0, 5), (4, 5), (4, M.y_back(4)), (0, M.L_SW)]
    face([(x, y, 0) for x, y in g], (0.87, 0.91, 0.78), 'none')
    face([(0, 0, 0), (19, 0, 0), (19, 5, 0), (0, 5, 0)], (0.87, 0.91, 0.78), 'none')
    yb0 = max(M.Y_T0 + o['L'] + 1.0, o['aisle_end'] + o['back_off'] - 1.5)
    face([(4, yb0, 0), (24, yb0, 0), (24, M.y_back(24), 0), (4, M.y_back(4), 0)], (0.87, 0.91, 0.78), 'none')
    face([(19, 10, 0), (24, 10, 0), (24, 28, 0), (19, 28, 0)], (0.80, 0.80, 0.80), (0.5, 0.5, 0.5))

    def box(x0, y0, x1, y1, z0, z1, top, side, side2, lines=0, step=0.0, zo=5):
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        faces = []
        for a, b in zip(pts, pts[1:] + pts[:1]):
            nx, ny = b[1] - a[1], -(b[0] - a[0])
            if (nx * math.sin(phi) + ny * math.cos(phi)) < 0:
                faces.append((a, b, nx))
        for a, b, nx in faces:
            col = side if abs(nx) > 1e-6 and nx < 0 or (abs(nx) < 1e-6) else side2
            face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], col, z=zo)
            for i in range(1, lines):
                zz = z0 + i * step
                pa, pb = P(a[0], a[1], zz), P(b[0], b[1], zz)
                ov.ax.plot([pa[0], pb[0]], [pa[1], pb[1]], lw=0.25, color=(0.67, 0.67, 0.67), zorder=zo)
        face([(x, y, z1) for x, y in pts], top, z=zo)

    L = o['L']
    zt = M.TERREO + o['n'] * M.TIPO_H
    box(5.0, M.Y_T0 + 1.0, 18.0, M.Y_T0 + L - 1.0, 0, M.TERREO, (0.81, 0.81, 0.85), (0.73, 0.73, 0.78),
        (0.73, 0.73, 0.78), zo=5)
    box(4.0, M.Y_T0, 19.0, M.Y_T0 + L, M.TERREO, zt, (1.0, 1.0, 1.0), (0.97, 0.97, 0.97), (0.97, 0.97, 0.97),
        lines=o['n'], step=M.TIPO_H, zo=6)
    ul = o['atico'] / M.W_T
    u0 = M.Y_T0 + (L - ul) / 2
    box(4.0, u0, 19.0, u0 + ul, zt, zt + M.ATICO, (0.91, 0.94, 0.69), (0.89, 0.92, 0.65), (0.89, 0.92, 0.65), zo=7)

    # rótulos com linhas de chamada
    def lab(z, t):
        px, py = P(4.0, M.Y_T0 + L, z)
        py = py if z else py
        ov.ax.plot([34, 400], [py + 4, py + 4], lw=0.4, color=(0.6, 0.6, 0.6), ls=(0, (1, 1)))
        ov.text(34, py, t, size=8.5, color=GREY)
    tipos = ', '.join(f"{o['seq'].count(k)}x {dict(A='2Q+3Q', B='2Q c/ suíte', M='misto 2Q+studios', S='studios+2Q')[k]}"
                      for k in sorted(set(o['seq'])))
    lab(zt + M.ATICO * 0.5, 'Rooftop – salão de festas/gourmet + terraço')
    lab(M.TERREO + o['n'] * M.TIPO_H / 2, f"Pav. tipo {o['n']}x – {tipos}")
    lab(1.5, 'Térreo – pilotis / hall / estacionamento / lazer')
    if o['nsub']:
        px, py = P(4.0, M.Y_T0 + L, 0)
        ov.ax.plot([34, 400], [py + 26, py + 26], lw=0.4, color=(0.6, 0.6, 0.6), ls=(0, (1, 1)))
        ov.text(34, py + 22, f"{'Subsolo' if o['nsub'] == 1 else str(o['nsub']) + ' subsolos'} – {o['nsub_v']} vagas "
                f"(não representado)", size=8.5, color=GREY)
    ov.text(34, 690, f"Altura estimada H = {br(o['H'])} m (térreo 3,00 + {o['n']} × 2,88 + ático 3,00)  •  "
            f"afastamento H/8 = {br(o['afast'])} m", size=6.5, color=GREY)
    stamp(ov, sub)
    ov.apply(page)


# ------------------------------------------------------------------ quadro numérico
RESSALVAS = [
    'Lote desenhado a partir da matrícula 39.537 (sem levantamento): laterais tomadas perpendiculares à frente (área 1.524,00 m² confere); '
    'fundos calculados 25,46 m × 25,38 m na matrícula.',
    'Ordem dos segmentos dos fundos (1,20 / 19,18 / 5,00 m) e largura da R. Zdenko Gayer a confirmar; recuo de 5,00 m adotado também nessa testada.',
    'Cadastro (CND) registra 498,22 m² construídos e a matrícula “sem benfeitorias”: prever demolição e averbação/baixa antes da aprovação.',
    'CA máximo (3,0) depende da Compensação Paisagística, “a ser regulamentada por lei específica” (LC 25/2020) — confirmar na SMUR.',
    'Altura máxima subordinada à infraestrutura existente (nota D da ZR3); subsolo a 0 m da divisa com o lote 07 exige contenção — sondagem SPT.',
    'Preços de venda e custos são premissas do estudo 151 (3Q a R$ 6.800/m²), não validados em pesquisa de mercado local.',
]


def quadro(page, o, sub, all_opts):
    ov = blank(page, 'Quadro numérico')
    T = ov.text
    T(34.0, 48.2, 'PARÂMETROS URBANÍSTICOS', size=8.5, weight='bold', color='black')
    T(1020.5, 48.2, 'ZR3', size=8.5, color='black')
    T(1156.5, 48.2, '1.524,00m²', size=8.5, color='black', ha='right')
    ov.line(34, 52.4, 1156.5, 52.4, 0.6)
    T(34.0, 66.6, 'R. ALEXANDRE WISOCKI, 249 – Fazenda Velha – Araucária • Paraná   •   Lote 08-A (Pl. Jardim Orly)   •   Matrícula 39.537'
      '   •   Insc. 01.01.00.099.0257   •   LC 25/2020, LC 26/2020 e LC 30/2023', size=7.5, color='black')
    ov.line(34, 72.3, 1156.5, 72.3, 0.6)

    def kv(y, a, b, v, bold=False):
        w = 'bold' if bold else 'normal'
        if a: T(36.9, y, a, size=7.5, color='black', weight=w)
        if b: T(332.8, y, b, size=7.5, color='black')
        T(513.1, y, v, size=7.5, color='black', ha='right', weight=w)

    mx = o['ca_mode'] == 'max'
    y = 92
    for a, b1, v1, b2, v2 in [
        ('Coeficiente Básico', 'índice', '2,50', 'área (m²)', '3.810,00'),
        ('Coeficiente Máximo (Compensação Paisagística)', 'índice', '3,00', 'área (m²)', '4.572,00'),
        ('Coeficiente Utilizado', 'índice', br(o['ca']), 'área (m²)', br(o['comp'])),
        ('Tx. de Ocupação – torre', 'máx.', '50%' if mx else '65%', 'utilizada', br(o['to_torre'] * 100, 1) + '%'),
        ('Tx. de Permeabilidade', 'mín.', '25%' if mx else '20%', 'utilizada', br(o['perm'] * 100, 1) + '%')]:
        kv(y, a, b1, v1); kv(y + 15.5, '', b2, v2); ov.line(34, y + 21, 515.9, y + 21); y += 31
    kv(y, 'Altura Padrão / Utilizada (pavimentos)', '', f"14 / {o['n'] + 1}")
    kv(y + 15.5, 'Afastamento torre (H/8, mín. 2,00) – adotado', '', f"{br(o['afast'])} / 4,00 m")

    y = 290
    T(36.9, y, 'Torre única', size=7.5, weight='bold', color='black'); ov.line(34, y + 5, 515.9, y + 5)
    for i, (a, v, b) in enumerate([('Área Privativa Total', br(o['priv']), False),
                                   ('Área de Lazer (térreo + rooftop)', br(o['lazer']), False),
                                   ('Área Computável Total', br(o['comp']), False),
                                   ('Área Construída Total', br(o['constr']), True)]):
        kv(y + 16 + 15.5 * i, a, '', v, b)

    y = 378
    cols = [(36.9, 'left', 'pavimento'), (283.5, 'right', 'rep.'), (368.5, 'right', 'computável'),
            (453.5, 'right', 'não comp.'), (544.2, 'right', 'construída'), (629.3, 'right', 'privativa')]
    for x, ha, t in cols:
        T(x, y, t, size=7.5, weight='bold', color='black', ha=ha)
    ov.line(34, y + 5, 635, y + 5, 0.5)
    y += 18
    for (lab, rep, cp, nc, co, un) in o['rows']:
        pv = sum(a * q for (t, a), q in un.items()) if un else 0
        for (x, ha, _), v in zip(cols, [lab, f'{rep}x', br(cp * rep), br(nc * rep), br(co * rep), br(pv * rep)]):
            T(x, y, v, size=6.6, color='black', ha=ha)
        y += 14.5
    ov.line(34, y - 7, 635, y - 7, 0.5)
    y += 4
    for (x, ha, _), v in zip(cols, ['TOTAIS', '', br(o['comp']), br(o['ncomp']), br(o['constr']), br(o['priv'])]):
        T(x, y, v, size=7.5, weight='bold', color='black', ha=ha)
    T(34.0, y + 13, 'Área computável conforme LC 26/2020, art. 151 (subsolo de estacionamento, ático ≤ 1/3, escada enclausurada, '
      'poço de elevador, guarita, lixo e gás não computáveis).', size=5.8, color=GREY)

    # ressalvas
    y = 600
    T(34, y, 'RESSALVAS', size=7.5, weight='bold', color='#9a1b1b')
    for i, t in enumerate(RESSALVAS):
        T(34, y + 12 + 10.3 * i, f'{i + 1}. ' + t, size=5.5, color=TXT)

    # ---- coluna direita
    X0, X1, xr = 657.6, 1156.5, 1153.7
    y = 90
    T(X0, y, 'Resumo Tipologias', size=8.0, weight='bold', color='black'); ov.line(X0, y + 5, X1, y + 5)
    y += 18
    for (t, a), q in sorted(o['units'].items(), key=lambda kv: ({'ST': 0, '2Q': 1, '3Q': 2}[kv[0][0]], kv[0][1])):
        nm = {'2Q': 'Ap. 2 quartos', '3Q': 'Ap. 3 quartos', 'ST': 'Studio (conjugado + banho)'}[t]
        T(660.5, y, f"{nm} – {br(a)} m²", size=7.2, color='black'); T(xr, y, str(q), size=7.2, color='black', ha='right'); y += 13
    T(660.5, y, 'TOTAL', size=7.5, weight='bold', color='black'); T(xr, y, str(o['nun']), size=7.5, weight='bold', color='black', ha='right')
    y += 26
    T(X0, y, 'Vagas de estacionamento', size=8.0, weight='bold', color='black'); ov.line(X0, y + 5, X1, y + 5)
    y += 18
    if o['nsub']:
        for i, s_ in enumerate(o['sub']):
            T(660.5, y, f"Subsolo S{i + 1}", size=7.2, color='black'); T(xr, y, str(len(s_)), size=7.2, color='black', ha='right'); y += 13
    T(660.5, y, 'Térreo (sob pilotis)', size=7.2, color='black'); T(xr, y, str(len(o['ground'])), size=7.2, color='black', ha='right'); y += 13
    vx = o['vx']
    T(660.5, y, f"TOTAL (exigidas: {vx['total']})", size=7.5, weight='bold', color='black')
    T(xr, y, str(o['vagas']), size=7.5, weight='bold', color='black', ha='right'); y += 11
    T(660.5, y, f"exigência: aptos 1 vaga/un. ({o['n2'] + o['n3']}) + studios 1 a cada 3 ({math.ceil(o['nst'] / 3)}) "
      f"+ visitantes 5% ({vx['vis']})   •   bicicletas: {vx['bici']}   •   capacidade livre no térreo: {len(o['g_all']) - len(o['ground'])} vagas",
      size=5.6, color=GREY)

    y += 26
    T(X0, y, 'Comparativo das opções (obra • VGV • resultado)', size=8.0, weight='bold', color='black')
    y += 16
    hdr = [(660.5, 'left', 'Opção'), (840, 'right', 'Unid.'), (872, 'right', 'Vagas'), (935, 'right', 'Custo obra'),
           (1000, 'right', 'VGV'), (1070, 'right', 'Resultado*'), (1110, 'right', 'Marg.'), (1156.5, 'right', 'EIV')]
    for x, ha, t in hdr:
        T(x, y, t, size=6.6, weight='bold', color='black', ha=ha)
    ov.line(X0, y + 4, X1, y + 4, 0.5)
    y += 14
    for r in all_opts:
        cur = r['key'] == o['key']
        if cur:
            ov.rect(X0, y - 9, X1, y + 3.5, fc=(0.94, 0.92, 0.88))
        w = 'bold' if cur else 'normal'
        for (x, ha, _), v in zip(hdr, [r['label'].replace('Estudo ', 'E'), str(r['nun']), str(r['vagas']), mi(r['custo']),
                                       mi(r['vgv']), mi(r['resultado']), f"{r['margem'] * 100:.0f}%", r['eiv']]):
            T(x, y, v, size=6.2, weight=w, color='black', ha=ha)
        y += 12.5
    ov.line(X0, y - 8, X1, y - 8, 0.4)
    p = M.P
    for i, n in enumerate([
            f"VGV: 2Q R$ {br(p['preco_2q'], 0)}/m² • 3Q R$ {br(p['preco_3q'], 0)}/m² • studio R$ {br(p['preco_st'], 0)}/m² • vaga excedente R$ {br(p['preco_vaga'] / 1000, 0)} mil.",
            f"Custo: R$ {br(p['custo_torre'], 0)}/m² construído (torre, térreo, ático) • subsolo R$ {br(p['custo_subsolo'], 0)}/m² • +R$ {br(p['custo_st_extra'] / 1000, 0)} mil/studio • demolição R$ 40 mil. CUB-PR ago/2026 (R8-N), ±20%.",
            "*Resultado = VGV − custo da obra − contrapartida EIV. Não inclui terreno, impostos, projetos/aprovação e comercialização."]):
        T(X0, y + 4 + 7.5 * i, n, size=5.3, color=GREY)

    y += 40
    T(X0, y, 'Verificação legal', size=8.0, weight='bold', color='black'); ov.line(X0, y + 5, X1, y + 5)
    y += 17
    for a, b, ok in M.checks(o):
        T(660.5, y, a, size=6.6, color='black')
        T(xr, y, b + ('  ✓' if ok else '  ✗'), size=6.6, color='black' if ok else '#b00020', ha='right')
        y += 11.5
    stamp(ov, sub)
    ov.apply(page)


def back(page):
    ov = R.Overlay()
    ov.text(850.4, 712.0, 'Marielen Ferri', size=11, weight='bold', color='white')
    ov.text(850.4, 727.0, 'Arquitetura e Urbanismo', size=9, color='#c9d2df')
    ov.apply(page)


def build(o, out):
    sub = o['label']
    doc = pymupdf.open(TEMPLATE)
    cover(doc[0], sub)
    diagram(doc[1], o, sub)
    occupation(doc[2], o, sub)
    quadro(doc[3], o, sub, M.OPTS)
    back(doc[4])
    doc.set_metadata(dict(title=f'153 Estudo de Viabilidade – {sub}', author='T & L Engenharia / Marielen Ferri Arquitetura',
                          creator='T & L Engenharia', producer='T & L Engenharia'))
    doc.save(out, garbage=4, deflate=True)
    print('ok', out)


if __name__ == '__main__':
    outdir = sys.argv[1]
    keys = sys.argv[2:] or [o['key'] for o in M.OPTS]
    os.makedirs(outdir, exist_ok=True)
    names = {'E1': '153 ESTUDO 1 - 2Q E 3Q - CA BASICO.pdf', 'E2': '153 ESTUDO 2 - 2Q E 3Q - CA MAXIMO.pdf',
             'E3': '153 ESTUDO 3 - 2Q E 3Q - CA MAXIMO 2 SUBSOLOS.pdf', 'E4': '153 ESTUDO 4 - 2Q E STUDIOS - CA BASICO.pdf',
             'E5': '153 ESTUDO 5 - 2Q E STUDIOS - CA MAXIMO.pdf', 'E6': '153 ESTUDO 6 - STUDIOS E 2Q - CA MAXIMO.pdf'}
    for o in M.OPTS:
        if o['key'] in keys:
            build(o, os.path.join(outdir, names[o['key']]))
