"""153 Estudo de Viabilidade — R. Alexandre Wisocki, 249 (lote 08-A, matr. 39.537) — Araucária/PR, ZR3.

Coordenadas locais (m): origem no canto frente/lado esquerdo-SW (divisa com o lote 10);
x ao longo da frente (24,00 m) até a divisa com o lote 07; y para dentro do lote.
Laterais perpendiculares à frente (área resultante = 1.524,00 m², igual à matrícula).
"""
import math

LOT_AREA = 1524.00
FRONT = 24.00
L_SW, L_NE = 67.75, 59.25            # lote 10 / lote 07
CA_BAS, CA_MAX = 2.50, 3.00
NORTH = (0.656, -0.755)          # norte em coord. locais (frente a 41° NE; lote avança para SE)
COS_B = math.cos(math.atan(8.5 / 24))  # inclinação dos fundos (19,5°)

P = dict(preco_2q=7000.0, preco_3q=6800.0, preco_st=8400.0, preco_vaga=35000.0,
         custo_torre=3470.0, custo_subsolo=3514.0, custo_st_extra=5000.0, demolicao=40000.0,
         cub_pr=2730.31, gi_eiv=0.05)

TERREO, TIPO_H, ATICO = 3.00, 2.88, 3.00
X_T0, W_T = 4.00, 15.00          # torre: x 4,00 a 19,00
CORR, CORE = 1.40, 3.80          # circulação (corredor) e faixa do hall/núcleo
NC_CORE = 21.66                  # escada enclausurada + poço de elevador (art. 151, VI)
Y_T0 = 12.0                      # início da torre (5 m recuo + 7 m de acesso/praça)
VW, VL, AISLE = 2.40, 5.00, 5.00


def y_back(x):
    return L_SW - (L_SW - L_NE) * x / FRONT


LOT = [(0, 0), (FRONT, 0), (FRONT, L_NE), (0, L_SW)]
_u = ((0 - FRONT) / 25.46, (L_SW - L_NE) / 25.46)
B1 = (FRONT + 1.20 * _u[0], L_NE + 1.20 * _u[1])
B2 = (B1[0] + 19.26 * _u[0], B1[1] + 19.26 * _u[1])


def vagas_exigidas(n_full, nst):
    v = n_full + math.ceil(nst / 3)
    vis = math.floor(0.05 * v)
    tot = v + vis
    k = n_full / v if v else 0
    bici = math.floor(0.15 * tot * k + 0.30 * tot * (1 - k))
    return dict(total=tot, vis=vis, bici=bici, unid=v)


def rows_rects(x0, x1, y0, y1, excl=()):
    out, y = [], y0
    while y + VW <= y1 + 1e-6:
        if not any(not (y + VW <= a or y >= b) for a, b in excl):
            out.append((x0, y, x1, y + VW))
        y += VW
    return out


def option(key, tipo, ca, n, floor_kind, nsub, label, notes=()):
    ca_lim = CA_MAX if ca == 'max' else CA_BAS
    af = ca_lim * LOT_AREA / (n + 1) + NC_CORE       # térreo pilotis + n tipos, mesmo pavimento
    L = round(af / W_T - 0.005, 2)
    af = L * W_T
    S = (L - CORE) / 2                                  # comprimento de cada ala
    du = (W_T - CORR) / 2                               # profundidade das unidades
    wing = S * du
    nst_w = 4 if wing >= 106 else 3
    # catálogo de alas: (tipologia, área)
    AL = {
        '2q3q': [('2Q', wing * 0.43), ('3Q', wing * 0.57)],
        '2q2q': [('2Q', wing / 2), ('2Q', wing / 2)],
        'st': [('ST', wing / nst_w)] * nst_w,
    }
    FLOORS = {   # 4 alas por pavimento
        'A': ['2q3q'] * 4,                       # 4×2Q + 4×3Q
        'B': ['2q2q'] * 4,                       # 8×2Q (c/ suíte)
        'M': ['2q2q', '2q2q', 'st', 'st'],       # 4×2Q + studios
        'S': ['2q2q', 'st', 'st', 'st'],         # 2×2Q + studios
    }
    seq = [floor_kind[i % len(floor_kind)] for i in range(n)]
    units = {}
    for f in seq:
        for w in FLOORS[f]:
            for t, a in AL[w]:
                k = (t, round(a, 2))
                units[k] = units.get(k, 0) + 1
    n2 = sum(q for (t, a), q in units.items() if t == '2Q')
    n3 = sum(q for (t, a), q in units.items() if t == '3Q')
    nst = sum(q for (t, a), q in units.items() if t == 'ST')
    nun = n2 + n3 + nst
    priv = sum(a * q for (t, a), q in units.items())
    vx = vagas_exigidas(n2 + n3, nst)
    H = TERREO + n * TIPO_H + ATICO
    afast = max(2.0, H / 8)

    # ---------------- estacionamento (geometria) ----------------
    y_core = Y_T0 + S
    back_off = 5.0
    yl = lambda x: y_back(x) - back_off
    aisle_end = yl(14.0)
    core_ex = [(y_core - 0.2, y_core + CORE + 0.2)]
    sub = []
    for lvl in range(nsub):
        rw = rows_rects(4.0, 9.0, 5.0, aisle_end, core_ex)
        if lvl == 0:
            re = rows_rects(14.0, 19.0, 5.0, 28.0) + rows_rects(14.0, 19.0, 33.0, yl(19.0))
        else:
            re = rows_rects(14.0, 19.0, 5.0, 51.0) + rows_rects(14.0, 19.0, 56.0, yl(19.0))
        sub.append(rw + re)
    lobby = [(y_core - 3.0, y_core + CORE + 3.0)]
    g_e = rows_rects(14.0, 19.0, 10.0, yl(19.0) + back_off - 1.5)
    g_w = rows_rects(4.0, 9.0, 10.0, aisle_end + back_off - 1.5, lobby)
    nsub_v = sum(len(s) for s in sub)
    need_g = max(0, vx['total'] - nsub_v)
    g_all = g_e + g_w
    ground = g_all[:need_g]
    vagas = nsub_v + len(ground)
    sub_area = 0.0
    if nsub:
        sub_poly_area = 20.0 * ((y_back(4) + y_back(24)) / 2 - back_off - 5.0)
        sub_area = sub_poly_area * nsub

    # ---------------- áreas ----------------
    comp_tipo = af - NC_CORE
    atico = round(af / 3, 2)
    gua = 18.0
    rows = []
    if nsub:
        rows.append(('Subsolo' + (f's (S1 e S2)' if nsub > 1 else ''), nsub, 0.0, sub_area / nsub, sub_area / nsub, None))
    rows.append(('Térreo – pilotis, hall e estacionamento', 1, comp_tipo, NC_CORE, af, None))
    for f in sorted(set(seq)):
        c = seq.count(f)
        u = {}
        for w in FLOORS[f]:
            for t, a in AL[w]:
                u[(t, round(a, 2))] = u.get((t, round(a, 2)), 0) + 1
        nm = {'A': 'Pav. tipo 2Q + 3Q', 'B': 'Pav. tipo 2Q (c/ suíte)', 'M': 'Pav. tipo misto 2Q + studios',
              'S': 'Pav. tipo studios + 2Q'}[f]
        rows.append((nm, c, comp_tipo, NC_CORE, af, u))
    rows.append(('Ático – salão de festas/gourmet (≤ 1/3)', 1, 0.0, atico, atico, None))
    rows.append(('Guarita, lixo e gás (recuo frontal)', 1, 0.0, gua, gua, None))
    comp = sum(r[1] * r[2] for r in rows)
    constr = sum(r[1] * r[4] for r in rows)
    ncomp = constr - comp

    # lazer: rooftop (salão + terraço) + jardim lateral SW + fundos + faixas de vaga não usadas
    roof = 0.85 * af                      # desconta caixa d'água, casa de máquinas, circulações
    y_end_t = Y_T0 + L
    fundos = sum(max(0.0, y_back(x + 0.5) - max(y_end_t + 2.0, aisle_end + back_off - 1.5)) for x in range(24))
    jardim = 2.5 * (y_back(2) - 5.0)
    unused = (len(g_all) - len(ground)) * VW * VL
    lazer_terreo = fundos + jardim + unused
    lazer = roof + lazer_terreo
    # permeabilidade: fora do subsolo, descontando pisos (acesso veículos no recuo, guarita/lixo, passeio 1,5 m)
    paved = 5 * 5 + gua + 1.5 * (y_core - 5)
    perm_area = (LOT_AREA - (sub_area / nsub if nsub else 0) - paved) if nsub else LOT_AREA - (
        sum(1 for _ in g_all) * VW * VL + 5 * 10 + af * 0 + paved + 5 * 23)
    perm = perm_area / LOT_AREA

    # ---------------- custos e VGV ----------------
    custo = ((constr - sub_area) * P['custo_torre'] + sub_area * P['custo_subsolo']
             + nst * P['custo_st_extra'] + P['demolicao'])
    vgv_un = sum(a * q * P[{'2Q': 'preco_2q', '3Q': 'preco_3q', 'ST': 'preco_st'}[t]] for (t, a), q in units.items())
    exced = max(0, vagas - vx['total'])
    vgv = vgv_un + exced * P['preco_vaga']
    eiv = 'Tipo 2' if vagas >= 200 else ('Tipo 1' if nun >= 130 else 'não')
    eiv_vc = 0 if eiv == 'não' else P['gi_eiv'] * (1.25 if nun > 200 else 1) * 0.25 * constr * P['cub_pr']
    res = vgv - custo - eiv_vc

    # studio: área útil do conjugado (paredes 0,15 m; banho 3,5 m²)
    st_conj = None
    if nst:
        fr = S / nst_w
        st_conj = (fr - 0.15) * (du - 0.15) - 3.5

    return dict(fk=list(floor_kind), key=key, tipo=tipo, label=label, ca_mode=ca, ca_lim=ca_lim, n=n, seq=seq, nsub=nsub,
                L=L, af=af, S=S, du=du, wing=wing, nst_w=nst_w, AL=AL, FLOORS=FLOORS, units=units,
                n2=n2, n3=n3, nst=nst, nun=nun, priv=priv, vx=vx, H=H, afast=afast, y_core=y_core,
                sub=sub, ground=ground, g_all=g_all, vagas=vagas, nsub_v=nsub_v, sub_area=sub_area,
                rows=rows, comp=comp, constr=constr, ncomp=ncomp, ca=comp / LOT_AREA, atico=atico,
                lazer=lazer, lazer_req=6.0 * nun, roof=roof, lazer_terreo=lazer_terreo,
                perm=perm, perm_req=0.25 if ca == 'max' else 0.20,
                to_torre=af / LOT_AREA, custo=custo, vgv=vgv, vgv_un=vgv_un, exced=exced,
                eiv=eiv, eiv_vc=eiv_vc, resultado=res, margem=res / vgv, st_conj=st_conj,
                aisle_end=aisle_end, back_off=back_off, notes=list(notes))


OPTS = [
    option('E1', '2Q + 3Q', 'bas', 6, ['A', 'B'], 1, 'Estudo 1 – 2Q e 3Q, CA básico (2,5)',
           ['tipos alternados: 2Q + 3Q / 2Q c/ suíte', '1 subsolo + vagas sob pilotis']),
    option('E2', '2Q + 3Q', 'max', 7, ['A', 'A', 'B'], 1, 'Estudo 2 – 2Q e 3Q, CA máximo (3,0)',
           ['CA máximo depende da Compensação Paisagística (perm. 25%, TO base 60% / torre 50%)']),
    option('E3', '2Q + 3Q', 'max', 7, ['A', 'A', 'B'], 2, 'Estudo 3 – 2Q e 3Q, CA máx., 2 subsolos',
           ['2 subsolos liberam o térreo inteiro para lazer']),
    option('E4', '2Q + studios', 'bas', 7, ['M'], 1, 'Estudo 4 – 2Q e studios, CA básico (2,5)'),
    option('E5', '2Q + studios', 'max', 8, ['M'], 1, 'Estudo 5 – 2Q e studios, CA máximo (3,0)',
           ['CA máximo depende da Compensação Paisagística']),
    option('E6', '2Q + studios', 'max', 8, ['S'], 1, 'Estudo 6 – studios + 2Q, CA máximo (3,0)',
           ['predominância de studios; abaixo de 130 unidades (sem EIV)']),
]


def checks(o):
    st_ok = o['st_conj'] is None or (21.0 <= o['st_conj'] <= 30.0)
    return [
        ('CA (LC 25/2020)', f"{o['ca']:.2f} ≤ {o['ca_lim']:.2f}".replace('.', ','), o['ca'] <= o['ca_lim'] + 1e-6),
        ('Pavimentos', f"{o['n'] + 1} ≤ 14", o['n'] + 1 <= 14),
        ('Afast. torre H/8', f"{X_T0:.2f} ≥ {o['afast']:.2f} m".replace('.', ','), X_T0 >= o['afast'] - 1e-6),
        ('TO torre', f"{o['to_torre'] * 100:.1f}% ≤ {50 if o['ca_mode'] == 'max' else 65}%".replace('.', ','),
         o['to_torre'] <= (0.50 if o['ca_mode'] == 'max' else 0.65)),
        ('Vagas (Anexo VII)', f"{o['vagas']} ≥ {o['vx']['total']}", o['vagas'] >= o['vx']['total']),
        ('Recreação 6 m²/un', f"{o['lazer']:.0f} ≥ {o['lazer_req']:.0f} m²", o['lazer'] >= o['lazer_req']),
        ('Permeabilidade', f"{o['perm'] * 100:.1f}% ≥ {o['perm_req'] * 100:.0f}%".replace('.', ','), o['perm'] >= o['perm_req']),
        ('Studio ≤ 30 m² úteis (art. 258)', '—' if o['st_conj'] is None else f"conj. {o['st_conj']:.1f} m²".replace('.', ','), st_ok),
        ('EIV (Lei 4.688/2025)', o['eiv'] + (' (≥130 un.)' if o['eiv'] == 'Tipo 1' else ''), True),
    ]


if __name__ == '__main__':
    for o in OPTS:
        bad = [c[0] for c in checks(o) if not c[2]]
        print(f"{o['key']} n={o['n']} L={o['L']:.2f} af={o['af']:.1f} wing={o['wing']:.1f} un={o['nun']:3d} "
              f"(2Q {o['n2']} 3Q {o['n3']} st {o['nst']}) priv={o['priv']:.0f} CA={o['ca']:.2f} constr={o['constr']:.0f} "
              f"vag={o['vagas']}({o['nsub_v']}+{len(o['ground'])}/{len(o['g_all'])}) exig={o['vx']['total']} "
              f"laz={o['lazer']:.0f}/{o['lazer_req']:.0f} perm={o['perm'] * 100:.1f}% H={o['H']:.1f} "
              f"custo={o['custo'] / 1e6:.1f} VGV={o['vgv'] / 1e6:.1f} res={o['resultado'] / 1e6:.1f} "
              f"marg={o['margem'] * 100:.0f}% conj={o['st_conj']} FAIL={bad}")
        for (t, a), q in sorted(o['units'].items()):
            print('     ', t, a, q)
