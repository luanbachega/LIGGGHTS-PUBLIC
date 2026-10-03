"""Gera as pranchas das versões com studios a partir das pranchas R00 originais (vetoriais).

Estratégia: cada página original é mantida como base; o que muda é removido por redaction
(somente o que está integralmente dentro da área) e redesenhado em Matplotlib/DejaVu Sans,
mesmo motor e fonte dos originais.
"""
import io, glob, math, copy, sys, os
import pymupdf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Polygon as MPoly
from shapely.geometry import Polygon, MultiPoint
from shapely.ops import unary_union
import model as M

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['text.parse_math'] = False
plt.rcParams['lines.scale_dashes'] = False
plt.rcParams['hatch.linewidth'] = 0.3

UP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'originais-R00')
SRC = {k: glob.glob(os.path.join(UP, f'151 ESTUDO {k} -*.pdf'))[0] for k in 'ABCD'}
W, H = 1190.55, 841.89
NAVY = (30 / 255, 53 / 255, 86 / 255)
DATE = 'out.26'
REV = 'R00'

C_UNIT = (0.93, 0.95, 0.77)
C_STUD = (0.98, 0.89, 0.68)
C_HALL = (0.84, 0.84, 0.89)
C_CIRC = (0.99, 0.83, 0.50)
C_EDGE = (0.33, 0.33, 0.33)
TXT = '#333333'
GREY = '#6e6e6e'


def br(x, d=2):
    s = f"{x:,.{d}f}"
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')


def mi(x):
    return 'R$ ' + br(x / 1e6, 1) + ' mi'


# ------------------------------------------------------------------ overlay helpers
class Overlay:
    def __init__(self):
        self.fig = plt.figure(figsize=(W / 72, H / 72), dpi=72)
        self.fig.patch.set_alpha(0)
        ax = self.fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, W)
        ax.set_ylim(H, 0)
        ax.axis('off')
        ax.patch.set_alpha(0)
        self.ax = ax

    def text(self, x, y, s, size=7.5, color=TXT, weight='normal', ha='left', va='baseline', **kw):
        return self.ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, **kw)

    def line(self, x0, y0, x1, y1, lw=0.4, color='black', **kw):
        self.ax.plot([x0, x1], [y0, y1], lw=lw, color=color, solid_capstyle='butt', **kw)

    def rect(self, x0, y0, x1, y1, fc='none', ec='none', lw=0.35, **kw):
        self.ax.add_patch(MPoly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True, fc=fc, ec=ec, lw=lw, **kw))

    def apply(self, page):
        buf = io.BytesIO()
        self.fig.savefig(buf, format='pdf', transparent=True)
        plt.close(self.fig)
        ov = pymupdf.open('pdf', buf.getvalue())
        page.show_pdf_page(page.rect, ov, 0, overlay=True)


def redact(page, rects, fill=(1, 1, 1)):
    for r in rects:
        page.add_redact_annot(pymupdf.Rect(*r), fill=fill)
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                          graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                          text=pymupdf.PDF_REDACT_TEXT_REMOVE)


def spans(page):
    return [s for b in page.get_text('dict')['blocks'] for l in b.get('lines', []) for s in l['spans']]


# ------------------------------------------------------------------ vector replay
def draw_to_path(d, xf=None):
    verts, codes, last = [], [], None
    P = (lambda p: (p.x, p.y)) if xf is None else (lambda p: xf((p.x, p.y)))

    def mv(p):
        nonlocal last
        q = P(p)
        if last is None or abs(last[0] - q[0]) + abs(last[1] - q[1]) > 1e-4:
            verts.append(q); codes.append(Path.MOVETO)
        last = q

    for it in d['items']:
        op = it[0]
        if op == 'l':
            mv(it[1]); q = P(it[2]); verts.append(q); codes.append(Path.LINETO); last = q
        elif op == 'c':
            mv(it[1])
            for p in it[2:5]:
                verts.append(P(p)); codes.append(Path.CURVE4)
            last = P(it[4])
        elif op == 're':
            r = it[1]
            pts = [P(r.tl), P(r.tr), P(r.br), P(r.bl)]
            verts += pts + [pts[0]]; codes += [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]; last = None
        elif op == 'qu':
            q = it[1]
            pts = [P(q.ul), P(q.ur), P(q.lr), P(q.ll)]
            verts += pts + [pts[0]]; codes += [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]; last = None
    if d.get('closePath') and verts:
        verts.append(verts[0]); codes.append(Path.CLOSEPOLY)
    return verts, codes


def replay(ax, d, verts=None, codes=None):
    if verts is None:
        verts, codes = draw_to_path(d)
    if not verts:
        return
    path = Path(verts, codes)
    fill = d.get('fill') if 'f' in d['type'] else None
    stroke = d.get('color') if 's' in d['type'] else None
    ls = '-'
    dashes = d.get('dashes')
    if stroke and dashes and dashes.strip() not in ('[] 0', '[ ] 0'):
        arr = dashes.split(']')[0].strip(' [').split()
        if arr:
            ls = (0, tuple(float(a) for a in arr))
    pp = PathPatch(path, fc=fill if fill else 'none', ec=stroke if stroke else 'none',
                   lw=(d.get('width') or 0) if stroke else 0, ls=ls,
                   alpha=None, joinstyle='miter', capstyle='butt')
    if fill is not None and d.get('fill_opacity') not in (None, 1):
        pp.set_alpha(d['fill_opacity'])
    ax.add_patch(pp)


def rnd(c):
    return c and tuple(round(x, 2) for x in c)


# ------------------------------------------------------------------ page 0 / stamp / back
def stamp(page, ov, sub):
    """troca a linha de subtítulo do carimbo + adiciona Marielen Ferri."""
    ov.text(977.9, 786.6, f"{sub}  .  {REV}     {DATE}", size=8.5, color=TXT, ha='right')
    ov.line(206, 776, 206, 797, lw=0.4, color='#9aa3ad')
    ov.text(214, 783.5, 'Marielen Ferri', size=8.0, weight='bold', color='#1e3556')
    ov.text(214, 793.7, 'Arquitetura', size=6.5, color=GREY)


def stamp_rects():
    return [(735, 777, 990, 790)]


def cover(page, sub):
    redact(page, [(470, 576, 720, 600)], fill=NAVY)
    ov = Overlay()
    ov.text(W / 2, 592.5, sub, size=11, color='white', ha='center')
    ov.apply(page)


def back(page):
    ov = Overlay()
    ov.text(850.4, 712.0, 'Marielen Ferri', size=11, weight='bold', color='white')
    ov.text(850.4, 727.0, 'Arquitetura e Urbanismo', size=9, color='#c9d2df')
    ov.apply(page)


# ------------------------------------------------------------------ page 1 diagram
def isoface_top_shift(verts, dy, top=True):
    """desloca os vértices superiores (menor y em cada par de mesmo x) de um paralelogramo vertical."""
    pts = verts[:4]
    xs = sorted(set(round(p[0], 1) for p in pts))
    out = list(verts)
    for x in xs:
        idx = [i for i, p in enumerate(pts) if round(p[0], 1) == x]
        if len(idx) == 2:
            i_top = min(idx, key=lambda i: pts[i][1])
            out[i_top] = (pts[i_top][0], pts[i_top][1] + dy)
    if len(out) > 4:
        out[4] = out[0]
    return out, [pts[i] for x in xs for i in [min([j for j, p in enumerate(pts) if round(p[0], 1) == x],
                                                  key=lambda j: pts[j][1])]]


def diagram(page, key, cfg):
    REG = (421, 135, 1170, 712)
    dr = page.get_drawings()
    keep = [d for d in dr if d['rect'].x0 >= REG[0] and d['rect'].y0 >= REG[1]
            and d['rect'].x1 <= REG[2] and d['rect'].y1 <= REG[3]]
    labels = [s for s in spans(page) if s['origin'][0] < 60 and 300 < s['origin'][1] < 650]
    rects = [REG] + [(32, s['origin'][1] - 9, 420, s['origin'][1] + 2.5) for s in labels
                     if any(k in s['text'] for k in cfg.get('relabel', {}))]
    if cfg.get('drop_label'):
        for s in labels:
            if cfg['drop_label'] in s['text']:
                rects.append((32, s['origin'][1] - 9, 880, s['origin'][1] + 5))
    redact(page, rects + stamp_rects())

    # ---- agrupa faces
    items = []
    for d in keep:
        v, c = draw_to_path(d)
        items.append(dict(d=d, v=v, c=c, fill=rnd(d.get('fill')), col=rnd(d.get('color'))))
    towers, cur = [], None
    garage = []
    for i, it in enumerate(items):
        if it['fill'] == (0.81, 0.81, 0.85):
            cur = dict(idx=[i]); towers.append(cur); continue
        if it['fill'] in ((0.96, 0.87, 0.69), (0.94, 0.78, 0.49)) or (
                garage and it['col'] == (0.67, 0.67, 0.67) and i == garage[-1] + 1 and cur is None):
            garage.append(i); continue
        if cur is not None:
            cur['idx'].append(i)

    def faces_lines(idx, face_fill):
        out = []
        for i in idx:
            it = items[i]
            if it['fill'] in face_fill:
                out.append([i, []])
            elif it['col'] == (0.67, 0.67, 0.67) and it['fill'] is None and out:
                out[-1][1].append(i)
        return out

    def spacing(lines):
        ys = sorted(items[j]['v'][0][1] + 0 for j in lines)
        # todas as linhas de uma face partem do mesmo x: o passo em y é constante
        diffs = [b - a for a, b in zip(ys, ys[1:])]
        return sorted(diffs)[len(diffs) // 2] if diffs else 23.0

    extra = []   # (after_index, verts) novas linhas
    removed = set()

    def raise_group(idx, n, side_fill, top_fill_test, line_style_from):
        fl = faces_lines(idx, side_fill)
        dy = spacing(max(fl, key=lambda f: len(f[1]))[1])
        for k in range(n):
            for f, lines in fl:
                it = items[f]
                newv, tops = isoface_top_shift(it['v'], -dy)
                extra.append((lines[-1] if lines else f, [tops[0], tops[1]], line_style_from))
                it['v'] = newv
                # próximos níveis partem do novo topo
                lines.append(None)
            for i in idx:
                it = items[i]
                if top_fill_test(it):
                    it['v'] = [(x, y - dy) for x, y in it['v']]
        return dy

    if cfg.get('raise_T2'):
        def nlines(t):
            fl = faces_lines(t['idx'], ((0.97, 0.97, 0.97),))
            return max(len(l) for _, l in fl)
        t2 = min(towers, key=nlines)
        style = next(items[i]['d'] for i in t2['idx'] if items[i]['col'] == (0.67, 0.67, 0.67))
        raise_group(t2['idx'], cfg['raise_T2'], ((0.97, 0.97, 0.97),),
                    lambda it: it['fill'] in ((1.0, 1.0, 1.0), (0.91, 0.94, 0.69), (0.89, 0.92, 0.65)), style)

    if cfg.get('lower_garage'):
        fl = faces_lines(garage, ((0.94, 0.78, 0.49),))
        dy = spacing(max(fl, key=lambda f: len(f[1]))[1])
        for f, lines in fl:
            it = items[f]
            it['v'], _ = isoface_top_shift(it['v'], dy * cfg['lower_garage'])
            top_lines = sorted(lines, key=lambda j: items[j]['v'][0][1])[:cfg['lower_garage']]
            removed.update(top_lines)
        for i in garage:
            if items[i]['fill'] == (0.96, 0.87, 0.69):
                items[i]['v'] = [(x, y + dy * cfg['lower_garage']) for x, y in items[i]['v']]
        # linha de chamada do rótulo
        for it in items:
            if it['col'] == (0.6, 0.6, 0.6) and it['d']['type'] == 's':
                v = it['v']
                j = max(range(len(v)), key=lambda k: v[k][1])
                v[j] = (v[j][0], v[j][1] + dy * cfg['lower_garage'])

    ov = Overlay()
    for i, it in enumerate(items):
        if i in removed:
            continue
        replay(ov.ax, it['d'], it['v'], it['c'])
        for after, seg, sty in extra:
            if after == i:
                replay(ov.ax, sty, seg, [Path.MOVETO, Path.LINETO])
    for s in labels:
        for k, new in cfg.get('relabel', {}).items():
            if k in s['text']:
                ov.text(34.0, s['origin'][1], new, size=8.5, color=GREY)
    for (x, y, t) in cfg.get('texts', []):
        ov.text(x, y, t, size=7.5, color=GREY)
    stamp(page, ov, cfg['sub'])
    ov.apply(page)


# ------------------------------------------------------------------ page 2: tipo plan
def tipo_bbox(page):
    xs, ys = [], []
    for d in page.get_drawings():
        f = rnd(d.get('fill'))
        r = d['rect']
        if f in (C_UNIT, C_HALL, C_CIRC) and r.y0 > 440 and r.x0 > 640 and d.get('color'):
            xs += [r.x0, r.x1]; ys += [r.y0, r.y1]
    return min(xs), min(ys), max(xs), max(ys)


def draw_tipo(ov, bb, kind, mix):
    """kind 'A' (33,4 x 12,2; circ 1,2) ou 'C' (40,8 x 12,5; circ 1,5)."""
    x0, y0, x1, y1 = bb
    L, D, c = (33.4, 12.2, 1.2) if kind == 'A' else (40.8, 12.5, 1.5)
    s = (x1 - x0) / L
    X = lambda m: x0 + m * s
    Y = lambda m: y0 + m * s
    row = 5.5
    hall0, hall1 = 14.8, 18.6

    def box(a, b, ya, yb, fc, label=None, fs=4.6):
        ov.rect(X(a), Y(ya), X(b), Y(yb), fc=fc, ec=C_EDGE, lw=0.35)
        if label:
            ov.text((X(a) + X(b)) / 2, (Y(ya) + Y(yb)) / 2, label, size=fs, ha='center', va='center',
                    linespacing=1.25)

    rows = [(0, row), (row + c, D)]
    # ala esquerda (2 módulos): studios em todo tipo misto/studio
    if mix in ('misto', 'studio'):
        w = 14.8 / 3
        for ya, yb in rows:
            for k in range(3):
                box(k * w, (k + 1) * w, ya, yb, C_STUD, f"Studio\n{br(M.ST)}m²")
        box(0, hall0, row, row + c, C_CIRC, 'Circulação', 4.2)
    # hall
    box(hall0, hall1, 0, D, C_HALL, 'Hall', 4.6)
    # ala direita
    right = L - hall1
    if mix == 'studio' and kind == 'C':
        w = right / 4
        for ya, yb in rows:
            for k in range(4):
                box(hall1 + k * w, hall1 + (k + 1) * w, ya, yb, C_STUD, f"Studio\n{br(M.ST_C)}m²")
        box(hall1, L, row, row + c, C_CIRC, 'Circulação', 4.2)
    elif mix == 'studio':
        w = 14.8 / 3
        for ya, yb in rows:
            for k in range(3):
                box(hall1 + k * w, hall1 + (k + 1) * w, ya, yb, C_STUD, f"Studio\n{br(M.ST)}m²")
        box(hall1, L, row, row + c, C_CIRC, 'Circulação', 4.2)
    else:
        mods = [M.AP40, M.AP44] if kind == 'A' else [M.AP40, M.AP40, M.AP45]
        for ya, yb in rows:
            for k, a in enumerate(mods):
                box(hall1 + 7.4 * k, hall1 + 7.4 * (k + 1), ya, yb, C_UNIT, f"Ap.\n{br(a)}m²\n2Q")
        box(hall1, L - 6.2, row, row + c, C_CIRC, 'Circulação', 4.2)
        box(L - 6.2, L, row, row + c, C_UNIT)


def legend_tipo(ov, bb, mix, kind):
    x0, y0, x1, y1 = bb
    yy = y1 + 16
    ov.rect(x0, yy - 5, x0 + 9, yy + 1, fc=C_STUD, ec=C_EDGE)
    ov.text(x0 + 13, yy, 'Studio  ambiente único conjugado (sala/quarto/cozinha) ≤ 30 m² úteis + banho  (LC 26/2020, art. 258)',
            size=5.0, color=TXT)
    if mix != 'studio':
        ov.rect(x0, yy + 4, x0 + 9, yy + 10, fc=C_UNIT, ec=C_EDGE)
        ov.text(x0 + 13, yy + 9, 'Apartamento 2 quartos', size=5.0, color=TXT)


def occupation(page, key, cfg):
    bb = tipo_bbox(page)
    sp = spans(page)
    lab = [s for s in sp if s['text'].strip() == 'Pavimento Tipo']
    rects = [(bb[0] - 2, bb[1] - 2, bb[2] + 2, bb[3] + 2)]
    for s in lab:
        b = s['bbox']; rects.append((b[0] - 40, b[1] - 1, b[2] + 40, b[3] + 1))
    rel = []
    for sub, new in cfg.get('relabels', []):
        m = next(s for s in sp if sub in s['text'])
        grp = [s for s in sp if abs(s['origin'][1] - m['origin'][1]) < 0.6 and abs(s['origin'][0] - m['origin'][0]) < 160]
        x0 = min(s['bbox'][0] for s in grp); x1 = max(s['bbox'][2] for s in grp)
        y0 = min(s['bbox'][1] for s in grp); y1 = max(s['bbox'][3] for s in grp)
        rects.append((x0 - 1, y0 - 0.5, x1 + 1, y1 + 0.5))
        rel.append(((x0 + x1) / 2, m['origin'][1], new, m['size']))
    if cfg.get('drop_region'):
        rects.append(cfg['drop_region'])
    redact(page, rects + stamp_rects())
    ov = Overlay()
    draw_tipo(ov, bb, cfg['kind'], cfg['mix'])
    if lab:
        s = lab[0]
        ov.text((s['bbox'][0] + s['bbox'][2]) / 2, s['origin'][1], cfg['tipo_title'], size=11, color='black', ha='center')
    legend_tipo(ov, bb, cfg['mix'], cfg['kind'])
    for (x, y, t, sz) in rel:
        ov.text(x, y, t, size=sz, color='black', ha='center')
    if cfg.get('extra'):
        cfg['extra'](ov)
    stamp(page, ov, cfg['sub'])
    ov.apply(page)


def subsolo_mask(page, keep_n):
    """devolve função que mascara as vagas eliminadas do subsolo do estudo C."""
    vs = []
    for d in page.get_drawings():
        if rnd(d.get('color')) == (0.79, 0.64, 0.29) and d['rect'].x0 > 700 and d['rect'].y1 < 400:
            v, _ = draw_to_path(d)
            pts = [p for p in v]
            if len(pts) >= 3:
                vs.append(Polygon(pts).convex_hull)
    ramp = (782, 272)
    vs.sort(key=lambda p: math.dist((p.centroid.x, p.centroid.y), ramp))
    kept, gone = vs[:keep_n], vs[keep_n:]
    hull_all = unary_union(vs).convex_hull.buffer(3)
    hull_keep = unary_union(kept).convex_hull.buffer(4)
    hull_keep = hull_keep.union(Polygon([(758, 236), (806, 236), (806, 309), (758, 309)]))
    mask = hull_all.difference(hull_keep)

    def f(ov):
        geoms = getattr(mask, 'geoms', [mask])
        for g in geoms:
            ov.ax.add_patch(MPoly(list(g.exterior.coords), closed=True, fc='white', ec='none', alpha=0.88))
            ov.ax.add_patch(MPoly(list(g.exterior.coords), closed=True, fc='none', ec='#9a9a9a', lw=0.0,
                                  hatch='////'))
        ov.ax.add_patch(MPoly(list(hull_keep.convex_hull.intersection(hull_all).exterior.coords), closed=True, fc='none', ec='#222222',
                              lw=0.6, ls=(0, (3, 1.5))))
        c = mask.centroid if mask.geom_type == 'Polygon' else max(mask.geoms, key=lambda g: g.area).centroid
        ov.text(c.x, c.y, 'sem escavação', size=5.0, color=GREY, ha='center', va='center')
    return f, len(vs)


# ------------------------------------------------------------------ page 3: quadro
def quadro(page, s, cfg):
    redact(page, [(30, 35, 1165, 716)] + stamp_rects())
    ov = Overlay()
    T = ov.text
    # cabeçalho
    T(34.0, 48.2, 'PARÂMETROS URBANÍSTICOS', size=8.5, weight='bold', color='black')
    T(1020.5, 48.2, 'ZR3', size=8.5, color='black')
    T(1156.5, 48.2, '4.137,80m²', size=8.5, color='black', ha='right')
    ov.line(34, 52.4, 1156.5, 52.4, 0.6)
    T(34.0, 66.6, 'AV. NOSSA SENHORA DOS REMÉDIOS, 2027 – Araucária • Paraná • Brasil   •   Lote A-3-6   •   Matrícula 11.882'
      '   •   LC 25/2020, LC 26/2020 e LC 30/2023', size=7.5, color='black')
    ov.line(34, 72.3, 1156.5, 72.3, 0.6)

    def kv(y, a, b, v, bold=False):
        w = 'bold' if bold else 'normal'
        if a:
            T(36.9, y, a, size=7.5, color='black', weight=w)
        if b:
            T(332.8, y, b, size=7.5, color='black')
        T(513.1, y, v, size=7.5, color='black', ha='right', weight=w)

    camax = s['params'] == 'max'
    y = 95.7
    kv(y, 'Coeficiente Básico', 'índice', '2,50'); kv(y + 17.6, '', 'área (m²)', '10.344,50'); ov.line(34, y + 24.2, 515.9, y + 24.2)
    y += 35.2
    kv(y, 'Coeficiente Máximo (Compensação Paisagística)', 'índice', '3,00'); kv(y + 17.6, '', 'área (m²)', '12.413,40'); ov.line(34, y + 24.2, 515.9, y + 24.2)
    y += 35.2
    kv(y, 'Coeficiente Utilizado', 'índice', br(s['ca'])); kv(y + 17.6, '', 'área (m²)', br(s['comp'])); ov.line(34, y + 24.2, 515.9, y + 24.2)
    y += 35.2
    kv(y, 'Tx. de Ocupação', 'máx.', s['to_txt']); kv(y + 17.6, '', 'utilizada', s['to_used']); ov.line(34, y + 24.2, 515.9, y + 24.2)
    y += 35.2
    kv(y, 'Tx. de Permeabilidade', 'mín.', '25%' if camax else '20%'); kv(y + 17.6, '', 'utilizada', br(s['perm'], 1) + '%'); ov.line(34, y + 24.2, 515.9, y + 24.2)
    y += 35.2
    kv(y, 'Altura Padrão (pavimentos)', '', '14'); kv(y + 17.6, 'Altura Utilizada (pavimentos)', '', str(s['pav_util']))

    y = 328.2
    T(36.9, y, '2X Torre', size=7.5, weight='bold', color='black'); ov.line(34, y + 6.6, 515.9, y + 6.6)
    kv(y + 17.6, 'Área Privativa Total', '', br(s['priv']))
    kv(y + 35.2, 'Área Estacionamento (vagas + circulação)', '', br(s['est_area']))
    kv(y + 52.8, 'Área Lazer (solo + rooftops)', '', br(s['lazer']))
    kv(y + 70.4, 'Área Computável Total', '', br(s['comp']))
    kv(y + 88.0, 'Área Construída Total', '', br(s['constr']), bold=True); ov.line(34, y + 94.4, 515.9, y + 94.4)

    # tabela de pavimentos
    y = 465.0
    cols = [(36.9, 'left', 'pavimento'), (283.5, 'right', 'rep.'), (368.5, 'right', 'computável'),
            (453.5, 'right', 'não comp.'), (544.2, 'right', 'construída'), (629.3, 'right', 'privativa')]
    for x, ha, t in cols:
        T(x, y, t, size=7.5, weight='bold', color='black', ha=ha)
    ov.line(34, y + 8.5, 635, y + 8.5, 0.5)
    y += 24
    for (lab, rep, cp, nc, co, un) in s['rows']:
        pv = sum(a * q for a, q in un.items()) if un else 0
        vals = [lab, f'{rep}x', br(cp * rep), br(nc * rep), br(co * rep), br(pv * rep)]
        for (x, ha, _), v in zip(cols, vals):
            T(x, y, v, size=6.6, color='black', ha=ha)
        y += 17.5
    ov.line(34, y - 7.5, 635, y - 7.5, 0.5)
    y += 4
    for (x, ha, _), v in zip(cols, ['TOTAIS', '', br(s['comp']), br(s['ncomp']), br(s['constr']), br(s['priv'])]):
        T(x, y, v, size=7.5, weight='bold', color='black', ha=ha)
    T(34.0, y + 15, 'Vagas descobertas (térreo e coberturas) não somam área construída. Área computável conforme LC 26/2020, art. 151.',
      size=6.0, color=GREY)
    for i, n in enumerate(s['notes']):
        T(34.0, y + 24 + 8.5 * i, '• ' + n[0].upper() + n[1:] + '.', size=6.0, color=GREY)

    # ---- verificação legal (coluna esquerda, base)
    yb = 668
    T(34.0, yb - 14, 'Verificação legal (resumo)', size=7.0, weight='bold', color='black')
    chk = [
        ('CA (LC 25/2020)', f"{br(s['ca'])} ≤ {br(s['ca_lim'])}", s['ca'] <= s['ca_lim'] + 1e-9),
        ('Vagas (Anexo VII)', f"{s['vagas']} ≥ {s['vx']['total']}", s['vagas'] >= s['vx']['total']),
        ('Recreação 6 m²/un (art. 178)', f"{br(s['lazer'], 0)} ≥ {br(s['lazer_req'], 0)} m²", s['lazer'] >= s['lazer_req']),
        ('Pavimentos (ZR3)', f"{s['pav_util']} ≤ 14", True),
        ('Dist. torres (H/6)x2 (art. 268)', 'mantida do R00', True),
        ('EIV (Lei 4.688/2025)', s['eiv_tipo'] + (' (≥130 un.)' if s['eiv_tipo'] == 'Tipo 1' else ''), True),
    ]
    for i, (a, b, ok) in enumerate(chk):
        xx = 34 + (i % 3) * 200
        yy = yb + (i // 3) * 13
        T(xx, yy, a, size=6.2, color='black')
        T(xx + 192, yy, b + ('  ✓' if ok else '  ✗'), size=6.2, color='black' if ok else '#b00020', ha='right')
    ov.line(34, yb + 19, 635, yb + 19, 0.3, color='#999999')

    # ---- coluna direita: tipologias
    X0, X1 = 657.6, 1156.5
    xr = 1153.7
    y = 93.5
    T(X0, y, 'Resumo Tipologias', size=8.0, weight='bold', color='black')
    y += 14
    ov.line(X0, y + 3, X1, y + 3)
    y += 15
    units = sorted(s['units'].items(), key=lambda kv: (not M.is_studio(kv[0]), kv[0]))
    for a, q in units:
        if M.is_studio(a):
            lab = f"Studio {br(a)}m²  (conjugado + banho)"
        else:
            lab = f"Ap. {br(a)}m²  2Q" + ('  (pontas)' if a in (M.AP44, M.AP45) else '')
        T(660.5, y, lab, size=7.5, color='black'); T(xr, y, str(q), size=7.5, color='black', ha='right')
        y += 15
    T(660.5, y, 'TOTAL', size=7.5, weight='bold', color='black')
    T(xr, y, f"{s['nun']}", size=7.5, weight='bold', color='black', ha='right')
    T(xr - 40, y, f"({s['nst']} studios • {s['n2q']} aptos 2Q)", size=6.5, color=GREY, ha='right')

    # ---- vagas
    y += 30
    T(X0, y, 'Vagas de estacionamento', size=8.0, weight='bold', color='black')
    y += 11
    ov.line(X0, y + 3, X1, y + 3)
    y += 15
    for lab, n in s['vagas_rows']:
        T(660.5, y, lab, size=7.2, color='black'); T(xr, y, str(n), size=7.2, color='black', ha='right'); y += 13.5
    vx = s['vx']
    T(660.5, y, f"TOTAL (exigidas: {vx['total']})", size=7.5, weight='bold', color='black')
    T(xr, y, str(s['vagas']), size=7.5, weight='bold', color='black', ha='right')
    y += 12
    T(660.5, y, f"exigência: 2Q 1 vaga/un. ({s['n2q']}) + studios 1 vaga a cada 3 un. ({math.ceil(s['nst'] / 3)}) + visitantes 5% ({vx['vis']})"
      f"{'  •  excedentes: ' + str(s['exced']) if s['exced'] else ''}", size=5.8, color=GREY)
    y += 13
    T(660.5, y, 'Bicicletas (15% p/ 2Q • 30% p/ studios)', size=7.2, color='black')
    T(xr, y, str(vx['bici']), size=7.2, color='black', ha='right')

    # ---- comparativo
    y += 26
    T(X0, y, 'Comparativo (obra • VGV • resultado)', size=8.0, weight='bold', color='black')
    y += 22
    hdr = [(660.5, 'left', 'Estudo'), (800, 'right', 'Unid.'), (836, 'right', 'Studios'), (866, 'right', 'Vagas'),
           (935, 'right', 'Custo da obra'), (1005, 'right', 'VGV'), (1075, 'right', 'Resultado*'), (1156.5, 'right', 'VGV/m² constr.')]
    for x, ha, t in hdr:
        T(x, y, t, size=6.6, weight='bold', color='black', ha=ha)
    ov.line(X0, y + 4, X1, y + 4, 0.5)
    y += 15
    for r in cfg['compare']:
        cur = r['key'] == s['key']
        if cur:
            ov.rect(X0, y - 9, X1, y + 4, fc=(0.94, 0.92, 0.88))
        w = 'bold' if cur else 'normal'
        vals = [r['curto'], str(r['nun']), str(r['nst']), str(r['vagas']), mi(r['custo']), mi(r['vgv']),
                mi(r['resultado']), 'R$ ' + br(r['vgv'] / r['constr'], 0)]
        for (x, ha, _), v in zip(hdr, vals):
            T(x, y, v, size=6.4, weight=w, color='black', ha=ha)
        y += 13.2
        if r['key'] == 'D':
            ov.line(X0, y - 8.5, X1, y - 8.5, 0.3, color='#999999')
    ov.line(X0, y - 8, X1, y - 8, 0.4)
    p = M.P
    notes = [
        f"Custo: estimativa paramétrica CUB-PR ago/2026 (R8-N), ordem de grandeza ±20%; estudos R00 mantidos e versões com studios por diferença",
        f"(+ pavimento tipo R$ {br(p['custo_torre'], 0)}/m², + R$ {br(p['custo_un_extra'] / 1000, 0)} mil por unidade adicional, − garagem suprimida ao custo/m² de cada solução).",
        f"VGV: 2Q R$ {br(p['preco_2q'], 0)}/m² • studio R$ {br(p['preco_st'], 0)}/m² (+{(p['preco_st'] / p['preco_2q'] - 1) * 100:.0f}%) • vaga excedente R$ {br(p['preco_vaga'] / 1000, 0)} mil — premissas a validar com o cliente/corretor.",
        "*Resultado = VGV − custo da obra − contrapartida EIV estimada. Não inclui terreno, impostos, projetos/aprovação e comercialização.",
    ]
    for i, n in enumerate(notes):
        T(X0, y + 4 + 7.2 * i, n, size=5.4, color=GREY)
    stamp(page, ov, cfg['sub'])
    ov.apply(page)


# ------------------------------------------------------------------ build one study
def build(s, base_key, cfg, out):
    doc = pymupdf.open(SRC[base_key])
    cover(doc[0], cfg['sub'])
    diagram(doc[1], base_key, dict(cfg['diag'], sub=cfg['sub']))
    occupation(doc[2], base_key, dict(cfg['occ'], sub=cfg['sub']))
    quadro(doc[3], s, cfg)
    back(doc[4])
    doc.set_metadata(dict(title=f"151 Estudo de Viabilidade – {cfg['sub']}", author='T & L Engenharia / Marielen Ferri Arquitetura',
                          creator='T & L Engenharia', producer='T & L Engenharia'))
    doc.save(out, garbage=4, deflate=True)
    print('ok', out)
