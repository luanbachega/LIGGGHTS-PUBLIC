"""DXF (metros) — base do lote 08-A e implantação de cada opção do estudo 153.

Origem (0,0) = canto da frente com a divisa do lote 10; eixo X ao longo da testada da
R. Alexandre Wisocki; eixo Y para dentro do lote. Norte indicado no desenho.
"""
import os, sys, math
import ezdxf
from ezdxf.enums import TextEntityAlignment
import model153 as M

LAYERS = {
    'LOTE': 7, 'LOTE-COTAS': 3, 'CONFRONTANTES': 8, 'VIAS': 9, 'RECUOS': 5, 'AFASTAMENTOS': 1,
    'TORRE-PROJECAO': 6, 'TORRE-TIPO': 2, 'UNIDADES': 30, 'NUCLEO': 252, 'SUBSOLO': 4, 'VAGAS': 40,
    'RAMPA': 32, 'LAZER': 170, 'JARDIM': 94, 'TEXTO': 7, 'NORTE': 7,
}


def new_doc():
    doc = ezdxf.new('R2010', setup=True)
    doc.units = ezdxf.units.M
    for n, c in LAYERS.items():
        doc.layers.add(n, color=c)
    doc.layers.get('RECUOS').dxf.linetype = 'DASHED'
    doc.layers.get('AFASTAMENTOS').dxf.linetype = 'DOT'
    doc.layers.get('TORRE-PROJECAO').dxf.linetype = 'DASHED'
    return doc


def T(msp, x, y, s, h=0.6, layer='TEXTO', rot=0, align=TextEntityAlignment.MIDDLE_CENTER):
    msp.add_text(s, height=h, rotation=rot, dxfattribs={'layer': layer}).set_placement((x, y), align=align)


def pl(msp, pts, layer, closed=True):
    msp.add_lwpolyline(pts, close=closed, dxfattribs={'layer': layer})


def rect(msp, x0, y0, x1, y1, layer, dx=0, dy=0):
    pl(msp, [(x0 + dx, y0 + dy), (x1 + dx, y0 + dy), (x1 + dx, y1 + dy), (x0 + dx, y1 + dy)], layer)


def base(msp, dx=0, dy=0, cotas=True):
    P = lambda p: (p[0] + dx, p[1] + dy)
    pl(msp, [P(p) for p in M.LOT], 'LOTE')
    # vias e confrontantes
    pl(msp, [P((-12, -1)), P((36, -1)), P((36, -17)), P((-12, -17))], 'VIAS')
    T(msp, 12 + dx, -9 + dy, 'RUA ALEXANDRE WISOCKI (16,00 m)', 0.8, 'VIAS')
    n = (8.5 / 25.46, 24 / 25.46)
    b1, b2 = M.B1, M.B2
    pl(msp, [P(b1), P(b2), P((b2[0] + n[0] * 12, b2[1] + n[1] * 12)), P((b1[0] + n[0] * 12, b1[1] + n[1] * 12))], 'VIAS')
    T(msp, (b1[0] + b2[0]) / 2 + n[0] * 7 + dx, (b1[1] + b2[1]) / 2 + n[1] * 7 + dy, 'RUA ZDENKO GAYER', 0.7, 'VIAS', rot=-19.5)
    T(msp, -5 + dx, 34 + dy, 'LOTE 10', 0.7, 'CONFRONTANTES', rot=90)
    T(msp, 29 + dx, 30 + dy, 'LOTE 07', 0.7, 'CONFRONTANTES', rot=90)
    T(msp, 1.5 + dx, 70.5 + dy, 'LOTE 03 QD. H', 0.45, 'CONFRONTANTES')
    T(msp, 26.5 + dx, 61.8 + dy, 'LOTE 01 QD. C', 0.45, 'CONFRONTANTES')
    for p in (M.B1, M.B2):
        msp.add_circle(P(p), 0.15, dxfattribs={'layer': 'LOTE'})
    # recuos 5,00 (frente e testada dos fundos)
    msp.add_line(P((0, 5)), P((24, 5)), dxfattribs={'layer': 'RECUOS'})
    m = (-8.5 / 25.46, -24 / 25.46)
    msp.add_line(P((b1[0] + 5 * m[0], b1[1] + 5 * m[1])), P((b2[0] + 5 * m[0], b2[1] + 5 * m[1])), dxfattribs={'layer': 'RECUOS'})
    T(msp, 12 + dx, 5.7 + dy, 'recuo frontal 5,00', 0.45, 'RECUOS')
    if cotas:
        dims = [((0, 0), (24, 0), -2.5), ((24, 0), (24, M.L_NE), 2.5), ((0, 0), (0, M.L_SW), -2.5),
                ((24, M.L_NE), M.B1, 2.0), (M.B1, M.B2, 2.0), (M.B2, (0, M.L_SW), 2.0)]
        for a, b, off in dims:
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            txt = br(math.dist(a, b)) if (a, b) != (M.B1, M.B2) else '19,26 (matr. 19,18)'
            d = msp.add_aligned_dim(p1=P(a), p2=P(b), distance=off, dimstyle='EZDXF', text=txt, override={
                'dimtxt': 0.6, 'dimasz': 0.4, 'dimdec': 2, 'dimdsep': ord(','), 'dimexe': 0.3, 'dimexo': 0.3},
                dxfattribs={'layer': 'LOTE-COTAS'})
            d.render()
    if cotas:
        T(msp, 12 + dx, 30 + dy, 'LOTE 08-A – 1.524,00 m²', 0.9, 'TEXTO')
        T(msp, 12 + dx, 28.6 + dy, 'Matrícula 39.537 • Insc. 01.01.00.099.0257 • ZR3', 0.55, 'TEXTO')
    # norte
    cx, cy = -8 + dx, -24 + dy
    msp.add_circle((cx, cy), 2.0, dxfattribs={'layer': 'NORTE'})
    nx, ny = M.NORTH
    msp.add_line((cx - nx * 2, cy - ny * 2), (cx + nx * 2, cy + ny * 2), dxfattribs={'layer': 'NORTE'})
    T(msp, cx + nx * 3, cy + ny * 3, 'N', 0.9, 'NORTE')


def option(msp, o):
    base(msp)
    L = o['L']
    rect(msp, o['x_t0'], M.Y_T0, 19.0, M.Y_T0 + L, 'TORRE-PROJECAO')
    T(msp, 11.5, M.Y_T0 + L - 1.2, f"projeção da torre {br(o['wt'])} x {br(L)} m", 0.5, 'TORRE-PROJECAO')
    for x in (o['afast'], 24 - o['afast']):
        msp.add_line((x, 5), (x, M.y_back(x) - 1), dxfattribs={'layer': 'AFASTAMENTOS'})
    T(msp, o['afast'] + 0.3, 40, f"H/8 = {br(o['afast'])}", 0.45, 'AFASTAMENTOS', rot=90)
    rect(msp, 19.0, 10.0, 24.0, 28.0, 'RAMPA'); T(msp, 21.5, 19, 'RAMPA', 0.5, 'RAMPA', rot=90)
    rect(msp, 9.5, 0.6, 17.5, 3.6, 'TEXTO'); T(msp, 13.5, 2.1, 'guarita / lixo / gás', 0.45)
    yc = o['y_core']
    rect(msp, 4.0, yc - 3.0, 9.0, yc + M.CORE + 3.0, 'NUCLEO'); T(msp, 6.5, yc + 1.9, 'HALL', 0.5, 'NUCLEO')
    for i, r in enumerate(o['ground']):
        rect(msp, *r, 'VAGAS'); T(msp, (r[0] + r[2]) / 2, (r[1] + r[3]) / 2, f"T{i + 1:02d}", 0.4, 'VAGAS')
    yb0 = max(M.Y_T0 + L + 1.0, o['aisle_end'] + o['back_off'] - 1.5)
    pl(msp, [(4.0, yb0), (24.0, yb0), (24.0, M.y_back(24)), (4.0, M.y_back(4))], 'LAZER')
    T(msp, 13, (yb0 + M.y_back(13)) / 2, 'LAZER', 0.6, 'LAZER')
    T(msp, 12, -21, f"{o['label']} – TÉRREO", 0.9)
    # subsolos ao lado (+40 m em X por nível)
    for lvl, vs in enumerate(o['sub']):
        dx = 40 * (lvl + 1)
        base(msp, dx=dx, cotas=False)
        bo = o['back_off']
        pl(msp, [(4 + dx, 5), (24 + dx, 5), (24 + dx, M.y_back(24) - bo), (4 + dx, M.y_back(4) - bo)], 'SUBSOLO')
        for i, r in enumerate(vs):
            rect(msp, *r, 'VAGAS', dx=dx); T(msp, (r[0] + r[2]) / 2 + dx, (r[1] + r[3]) / 2, f"S{lvl + 1}-{i + 1:02d}", 0.35, 'VAGAS')
        rect(msp, 4.0, yc, 9.0, yc + M.CORE, 'NUCLEO', dx=dx)
        T(msp, 12 + dx, -21, f"SUBSOLO S{lvl + 1} – {len(vs)} vagas", 0.9)
    # pavimentos tipo (posição real sobre o lote, deslocados +40·(nsub+1))
    for j, k in enumerate(sorted(set(o['seq']))):
        dx = 40 * (len(o['sub']) + 1 + j)
        base(msp, dx=dx, cotas=False)
        du, c, xt = o['du'], M.CORR, o['x_t0']
        y0 = M.Y_T0
        pl_ = o['plans'][k]
        split = pl_['split']
        for ri, row in enumerate(pl_['rows']):
            x0, x1 = (xt, xt + du) if ri == 0 else (xt + du + c, 19.0)
            u = 0.0
            for j, (t, a, fr) in enumerate(row):
                if j == split:
                    u += M.CORE
                rect(msp, x0, y0 + u, x1, y0 + u + fr, 'UNIDADES', dx=dx)
                T(msp, (x0 + x1) / 2 + dx, y0 + u + fr / 2, f"{t} {br(a)}", 0.4, 'UNIDADES', rot=90)
                u += fr
        us = sum(fr for _, _, fr in pl_['rows'][0][:split])
        rect(msp, xt + du, y0, xt + du + c, y0 + L, 'TORRE-TIPO', dx=dx)
        rect(msp, xt, y0 + us, 19.0, y0 + us + M.CORE, 'NUCLEO', dx=dx)
        rect(msp, xt, y0, 19.0, y0 + L, 'TORRE-TIPO', dx=dx)
        T(msp, 12 + dx, -21, M.kind_name(o["plans"][k]["comp"]).upper() + f" ({o['seq'].count(k)}x)", 0.9)


def br(x, d=2):
    return f"{x:,.{d}f}".replace(',', 'X').replace('.', ',').replace('X', '.')


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    d = new_doc(); base(d.modelspace())
    d.saveas(os.path.join(out, '153 BASE LOTE 08-A - R ALEXANDRE WISOCKI.dxf'))
    for o in M.OPTS:
        d = new_doc(); option(d.modelspace(), o)
        d.saveas(os.path.join(out, f"153 IMPLANTACAO {o['key']}.dxf"))
    print('ok')
