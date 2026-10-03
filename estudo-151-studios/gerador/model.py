"""Modelo numérico — 151 Estudo de Viabilidade, versões com studios.

Base legal (Araucária):
  LC 25/2020 (zoneamento) — ZR3: CA básico 2,5 / máx 3,0 (compensação paisagística),
      TO base 65% (60% no máx), TO torre 50% no máx, perm. 20% (25% no máx), 14 pav.
  LC 26/2020 c/ redação LC 30/2023 (código de obras):
      art. 151  áreas não computáveis
      art. 178  recreação >= 6,00 m² por unidade (50% contínua, 25% permeável)
      art. 258  studio = 1 compartimento conjugado <= 30,00 m² úteis + instalação sanitária
      art. 259 / Anexo VII  studios: 1 vaga a cada 1 a 3 unidades; demais: 1 vaga/unidade;
                visitantes 5% (art. 268, V); bicicletas +15% (2Q) / +30% (studios);
                frações desprezadas (Obs. gerais do Anexo VII)
      art. 268, II  distância entre torres (H/6)x2 >= 5,00 m
  Lei 4.688/2025 (EIV): Tipo 1 p/ condomínio vertical >= 130 unidades;
      Tipo 2 p/ habitação com >= 200 vagas. VC = GI x (VI x 0,25).
"""
import math

LOT = 4137.80
CA_BAS, CA_MAX = 2.50, 3.00

# ---------------- premissas de mercado / custo (editáveis) -----------------
P = dict(
    preco_2q=7000.0,        # R$/m² privativo, 2 quartos (vaga inclusa)
    preco_st=8400.0,        # R$/m² privativo, studio (+20%)
    preco_vaga=35000.0,     # R$ por vaga excedente comercializada
    custo_torre=3470.0,     # R$/m² construído (torres/térreo/ático) — calibrado nos estudos R00
    custo_un_extra=15000.0, # R$ por unidade adicional (cozinha+banho+porta+medição)
    custo_garagem_emb=2122.0,   # R$/m² garagem em embasamento (B) — calibrado
    custo_subsolo=3514.0,       # R$/m² subsolo (C) — calibrado
    custo_edgar=1666.0,         # R$/m² edifício garagem (D) — calibrado
    cub_pr=2730.31,         # CUB-PR ago/2026 (referência VI do EIV)
    gi_eiv=0.05,            # grau de impacto estimado (depende da matriz do EIV)
)

# ---------------- tipologias ----------------
# módulo: unidade 7,40 m (fachada) x 5,50 m (prof.)
AP40, AP44, AP45 = 40.70, 44.42, 45.35
ST = round(14.80 * 5.50 / 3, 2)        # 3 studios no lugar de 2 aptos -> 27,13 m²
ST_C = round(22.20 * 5.50 / 4, 2)      # 4 studios no lugar de 3 aptos (só variante 100%) -> 30,53

# pavimentos tipo (por torre): (comp, nao_comp, construida, {tipologia: qtd})
TIPO_A_2Q = (385.82, 21.66, 407.48, {AP44: 4, AP40: 4})
TIPO_A_MX = (385.82, 21.66, 407.48, {ST: 6, AP44: 2, AP40: 2})
TIPO_A_ST = (385.82, 21.66, 407.48, {ST: 12})
TIPO_C_2Q = (488.34, 21.66, 510.00, {AP45: 4, AP40: 6})
TIPO_C_MX = (488.34, 21.66, 510.00, {ST: 6, AP45: 2, AP40: 4})
TIPO_C_ST = (488.34, 21.66, 510.00, {ST: 6, ST_C: 8})


def is_studio(area):
    return area < 32


def priv(t):
    return sum(a * q for a, q in t[3].items())


def vagas_exigidas(n2q, nst):
    v2 = n2q
    vs = math.ceil(nst / 3)                     # 1 vaga a cada intervalo de 1 a 3 studios
    vis = math.floor(0.05 * (v2 + vs))          # visitantes 5%
    tot = v2 + vs + vis
    # bicicletário: 15% (2Q) / 30% (studios) sobre as vagas, rateando visitantes
    k2 = v2 / (v2 + vs) if (v2 + vs) else 0
    bik = math.floor(0.15 * tot * k2 + 0.30 * tot * (1 - k2))
    return dict(unid=v2 + vs, vis=vis, total=tot, bici=bik)


def study(key, nome, curto, pav_rows, vagas_rows, est_area, lazer_area, perm, to_txt, to_used,
          pav_util, base_cost=None, ref=None, notes=(), params='bas'):
    """pav_rows: list of (label, rep, comp, ncomp, constr, units_dict or None)."""
    comp = sum(r[1] * r[2] for r in pav_rows)
    ncomp = sum(r[1] * r[3] for r in pav_rows)
    constr = sum(r[1] * r[4] for r in pav_rows)
    units = {}
    for r in pav_rows:
        if r[5]:
            for a, q in r[5].items():
                units[a] = units.get(a, 0) + q * r[1]
    privat = sum(a * q for a, q in units.items())
    n2q = sum(q for a, q in units.items() if not is_studio(a))
    nst = sum(q for a, q in units.items() if is_studio(a))
    vx = vagas_exigidas(n2q, nst)
    vagas = sum(v for _, v in vagas_rows)
    return dict(key=key, nome=nome, curto=curto, rows=pav_rows, vagas_rows=vagas_rows,
                comp=comp, ncomp=ncomp, constr=constr, priv=privat, units=units,
                n2q=n2q, nst=nst, nun=n2q + nst, vx=vx, vagas=vagas,
                est_area=est_area, lazer=lazer_area, perm=perm, to_txt=to_txt, to_used=to_used,
                pav_util=pav_util, ca=comp / LOT, params=params, notes=list(notes))


def U(t, n=2):
    """unidades de n torres de um pavimento tipo"""
    return {a: q * n for a, q in t[3].items()}


def row_tipo(label, rep, t, n=2):
    return (label, rep, t[0] * n, t[1] * n, t[2] * n, U(t, n))


# ------------------------------------------------------------------ originais R00
A = study('A', 'Estudo A  Somente vagas no térreo', 'A  só térreo', [
    ('Térreo  pilotis (2 torres)', 1, 771.64, 43.32, 814.96, None),
    row_tipo('Pav. tipo (2 torres)', 7, TIPO_A_2Q),
    row_tipo('Pav. tipo (só T1)', 1, TIPO_A_2Q, 1),
    ('Ático  salão gourmet (2 torres)', 1, 0, 264.08, 264.08, None),
    ('Guarita, lixo e gás', 1, 0, 18.10, 18.10, None)],
    [('Térreo', 127)], 2789.86, 1079.41, 34.4, '65%', '19,7%', 9)
A['custo'] = 25.0e6

B = study('B', 'Estudo B  Vagas no térreo e 2 pavimentos', 'B  térreo + 2 pav.', [
    ('Térreo garagem', 1, 2272.23, 43.32, 2315.55, None),
    ('1º pav. garagem', 1, 2272.23, 43.32, 2315.55, None),
    row_tipo('Pav. tipo (2 torres)', 10, TIPO_A_2Q),
    ('Ático  salão gourmet (2 torres)', 1, 0, 264.08, 264.08, None),
    ('Guarita, lixo e gás', 1, 0, 21.84, 21.84, None)],
    [('Térreo', 73), ('1º pavimento', 85), ('Cobertura (deck)', 24)],
    4296.88, 1314.72, 37.2, 'base 60% / torre 50%', 'base 56,0% / torre 19,7%', 12, params='max')
B['custo'] = 41.3e6

C = study('C', 'Estudo C  Vagas com 1 subsolo', 'C  1 subsolo', [
    ('Subsolo', 1, 0, 3001.60, 3001.60, None),
    ('Térreo  pilotis (2 torres)', 1, 976.68, 43.32, 1020.00, None),
    row_tipo('Pav. tipo (2 torres)', 9, TIPO_C_2Q),
    ('Ático  salão gourmet (2 torres)', 1, 0, 270.68, 270.68, None),
    ('Guarita, lixo e gás', 1, 0, 21.84, 21.84, None)],
    [('Térreo', 91), ('Subsolo s1', 108)], 4743.08, 1517.50, 23.9, '65%', '24,7%', 10)
C['custo'] = 46.8e6

EDG = (751.33, 15.68, 767.01)  # edifício garagem, por pavimento coberto
D = study('D', 'Estudo D  Vagas em edifício garagem', 'D  edif. garagem', [
    ('Térreo  pilotis (2 torres)', 1, 771.64, 43.32, 814.96, None),
    ('Ed. garagem térreo a 3º pav.', 4, *EDG, None),
    row_tipo('Pav. tipo (2 torres)', 8, TIPO_A_2Q),
    row_tipo('Pav. tipo (só T1)', 1, TIPO_A_2Q, 1),
    ('Ático  salão gourmet (2 torres)', 1, 0, 264.08, 264.08, None),
    ('Guarita, lixo e gás', 1, 0, 20.34, 20.34, None)],
    [('Térreo (pilotis + descoberto)', 33), ('Ed. garagem térreo', 23), ('Ed. garagem 1º pav.', 23),
     ('Ed. garagem 2º pav.', 23), ('Ed. garagem 3º pav.', 23), ('Ed. garagem cobertura (descoberta)', 21)],
    3375.16, 1236.92, 40.0, '65%', '38,2%', 10)
D['custo'] = 33.2e6

# ------------------------------------------------------------------ versões com studios
TOW = P['custo_torre']

A2 = study('A2', 'Estudo A2  Vagas no térreo + studios', 'A2  só térreo + studios', [
    ('Térreo  pilotis (2 torres)', 1, 771.64, 43.32, 814.96, None),
    row_tipo('Pav. tipo misto (2 torres)', 8, TIPO_A_MX),
    ('Ático  salão gourmet (2 torres)', 1, 0, 264.08, 264.08, None),
    ('Guarita, lixo e gás', 1, 0, 18.10, 18.10, None)],
    [('Térreo', 127)], 2789.86, 1079.41, 34.4, '65%', '19,7%', 9,
    notes=['T2 passa de 7 para 8 pav. tipo (mesma altura da T1: distância entre torres mantida)'])
A2['custo'] = A['custo'] + 407.48 * TOW + (A2['nun'] - A['nun']) * P['custo_un_extra']

B2 = study('B2', 'Estudo B2  Vagas no térreo e 2 pav. + studios', 'B2  térreo + 2 pav. + studios', [
    ('Térreo garagem', 1, 2272.23, 43.32, 2315.55, None),
    ('1º pav. garagem', 1, 2272.23, 43.32, 2315.55, None),
    row_tipo('Pav. tipo misto (2 torres)', 10, TIPO_A_MX),
    ('Ático  salão gourmet (2 torres)', 1, 0, 264.08, 264.08, None),
    ('Guarita, lixo e gás', 1, 0, 21.84, 21.84, None)],
    [('Térreo', 73), ('1º pavimento', 85), ('Cobertura (deck)', 24)],
    4296.88, 1314.72, 37.2, 'base 60% / torre 50%', 'base 56,0% / torre 19,7%', 12, params='max',
    notes=['volume idêntico ao B (CA já em 2,96); ganho via unidades e vagas excedentes'])
B2['custo'] = B['custo'] + (B2['nun'] - B['nun']) * P['custo_un_extra']

C2_SUB = 60
C2_SUB_AREA = round(3001.60 * 0.60, 2)   # subsolo reduzido (~60% da projeção; rampa e circulação mantidas)
C2 = study('C2', 'Estudo C2  Subsolo reduzido + studios', 'C2  subsolo reduzido + studios', [
    ('Subsolo (reduzido)', 1, 0, C2_SUB_AREA, C2_SUB_AREA, None),
    ('Térreo  pilotis (2 torres)', 1, 976.68, 43.32, 1020.00, None),
    row_tipo('Pav. tipo misto (2 torres)', 9, TIPO_C_MX),
    ('Ático  salão gourmet (2 torres)', 1, 0, 270.68, 270.68, None),
    ('Guarita, lixo e gás', 1, 0, 21.84, 21.84, None)],
    [('Térreo', 91), ('Subsolo s1 (reduzido)', C2_SUB)], round(4743.08 * 151 / 199, 2), 1517.50, 23.9, '65%', '24,7%', 10,
    notes=['subsolo reduzido de 108 para 60 vagas (~60% da escavação)'])
C2['custo'] = C['custo'] - (3001.60 - C2_SUB_AREA) * P['custo_subsolo'] + (C2['nun'] - C['nun']) * P['custo_un_extra']

D2 = study('D2', 'Estudo D2  Edifício garagem + studios', 'D2  edif. garagem + studios', [
    ('Térreo  pilotis (2 torres)', 1, 771.64, 43.32, 814.96, None),
    ('Ed. garagem térreo a 2º pav.', 3, *EDG, None),
    row_tipo('Pav. tipo misto (2 torres)', 9, TIPO_A_MX),
    ('Ático  salão gourmet (2 torres)', 1, 0, 264.08, 264.08, None),
    ('Guarita, lixo e gás', 1, 0, 20.34, 20.34, None)],
    [('Térreo (pilotis + descoberto)', 33), ('Ed. garagem térreo', 23), ('Ed. garagem 1º pav.', 23),
     ('Ed. garagem 2º pav.', 23), ('Ed. garagem cobertura (descoberta)', 21)],
    round(3375.16 * 123 / 146, 2), 1236.92, 40.0, '65%', '38,2%', 10,
    notes=['T2 passa de 8 para 9 pav. tipo', 'edifício garagem perde 1 pavimento (térreo + 2 pav. + cobertura)'])
D2['custo'] = (D['custo'] + 407.48 * TOW - EDG[2] * P['custo_edgar']
               + (D2['nun'] - D['nun']) * P['custo_un_extra'])

ORIG = [A, B, C, D]
NEW = [A2, B2, C2, D2]


# ------------------------------------------------------------------ variantes 100% studio (indicativas)
def variant100(base, tipo_rows, vagas_rows, custo, nota):
    s = study(base['key'] + '-100', base['nome'] + ' (100% studio)', base['curto'] + ' 100%',
              tipo_rows, vagas_rows, base['est_area'], base['lazer'], base['perm'], base['to_txt'],
              base['to_used'], base['pav_util'], params=base['params'], notes=[nota])
    s['custo'] = custo
    return s


V100 = [
    variant100(A2, [r if 'tipo' not in r[0] else row_tipo('Pav. tipo studio (2 torres)', 8, TIPO_A_ST)
                    for r in A2['rows']], A2['vagas_rows'],
               A['custo'] + 407.48 * TOW + (192 - 120) * P['custo_un_extra'],
               'lazer exige +73 m² (converter 4 vagas excedentes)'),
    variant100(B2, [r if 'tipo' not in r[0] else row_tipo('Pav. tipo studio (2 torres)', 10, TIPO_A_ST)
                    for r in B2['rows']], [('Térreo', 73), ('1º pavimento', 85)],
               B['custo'] + (240 - 160) * P['custo_un_extra'], 'deck vira lazer (lazer exigido 1.440 m²)'),
    variant100(C2, [r for r in C2['rows'] if 'Subsolo' not in r[0] and 'tipo' not in r[0]][:1]
               + [row_tipo('Pav. tipo studio (2 torres)', 9, TIPO_C_ST)]
               + [r for r in C2['rows'] if 'Ático' in r[0] or 'Guarita' in r[0]],
               [('Térreo', 91)],
               C['custo'] - 3001.60 * P['custo_subsolo'] + (252 - 180) * P['custo_un_extra'],
               'SEM subsolo (91 vagas no térreo atendem 88 exigidas)'),
    variant100(D2, [r if 'tipo' not in r[0] and 'garagem' not in r[0] else
                    (row_tipo('Pav. tipo studio (2 torres)', 9, TIPO_A_ST) if 'tipo' in r[0]
                     else ('Ed. garagem térreo', 1, *EDG, None)) for r in D2['rows']],
               [('Térreo (pilotis + descoberto)', 33), ('Ed. garagem térreo', 23), ('Ed. garagem cobertura', 21)],
               D['custo'] + 407.48 * TOW - 3 * EDG[2] * P['custo_edgar'] + (216 - 136) * P['custo_un_extra'],
               'edifício garagem só térreo + cobertura; lazer exige +60 m²'),
]


def finance(s):
    v2 = sum(a * q for a, q in s['units'].items() if not is_studio(a)) * P['preco_2q']
    vs = sum(a * q for a, q in s['units'].items() if is_studio(a)) * P['preco_st']
    exc = max(0, s['vagas'] - s['vx']['total'])
    vv = exc * P['preco_vaga']
    s['vgv_un'] = v2 + vs
    s['vgv_vagas'] = vv
    s['vgv'] = v2 + vs + vv
    s['exced'] = exc
    ap = 1.25 if s['nun'] > 200 else 1.0
    s['eiv_tipo'] = ('Tipo 2' if s['vagas'] >= 200 else ('Tipo 1' if s['nun'] >= 130 else 'não'))
    s['eiv_vc'] = 0 if s['eiv_tipo'] == 'não' else P['gi_eiv'] * ap * 0.25 * s['constr'] * P['cub_pr']
    s['resultado'] = s['vgv'] - s['custo'] - s['eiv_vc']
    s['margem'] = s['resultado'] / s['vgv']
    s['lazer_req'] = 6.0 * s['nun']
    s['ca_lim'] = CA_MAX if s['params'] == 'max' else CA_BAS
    return s


C3 = V100[2]
C3.update(key='C3', nome='Estudo C3  Sem subsolo + 100% studios', curto='C3  sem subsolo, 100% studios',
          est_area=round(4743.08 * 91 / 199, 2),
          notes=['subsolo eliminado: 91 vagas no térreo atendem as 88 exigidas (252 studios)',
                 'pavimento tipo 100% studios: 14 por torre (6 de 27,13 m² + 8 de 30,53 m²)'])
NEW.append(C3)
V100 = [v for v in V100 if v is not C3]

for s in ORIG + NEW + V100:
    finance(s)


def checks(s):
    out = []
    out.append(('CA', f"{s['ca']:.2f} ≤ {s['ca_lim']:.2f}", s['ca'] <= s['ca_lim'] + 1e-9))
    out.append(('Vagas', f"{s['vagas']} ≥ {s['vx']['total']}", s['vagas'] >= s['vx']['total']))
    out.append(('Lazer 6 m²/un', f"{s['lazer']:.0f} ≥ {s['lazer_req']:.0f}", s['lazer'] >= s['lazer_req']))
    out.append(('Pavimentos', f"{s['pav_util']} ≤ 14", s['pav_util'] <= 14))
    return out


if __name__ == '__main__':
    def mi(x):
        return f"{x/1e6:6.1f}"
    print(f"{'est':7s} {'un':>4s} {'2Q':>4s} {'st':>4s} {'priv':>8s} {'comp':>9s} {'CA':>5s} {'constr':>9s} "
          f"{'vag':>4s} {'exig':>4s} {'bic':>4s} {'lazR':>5s} {'laz':>6s} {'custo':>6s} {'VGV':>6s} {'EIV':>5s} {'res':>6s} {'marg':>5s}")
    for s in ORIG + NEW + V100:
        print(f"{s['key']:7s} {s['nun']:4d} {s['n2q']:4d} {s['nst']:4d} {s['priv']:8.2f} {s['comp']:9.2f} {s['ca']:5.2f} "
              f"{s['constr']:9.2f} {s['vagas']:4d} {s['vx']['total']:4d} {s['vx']['bici']:4d} {s['lazer_req']:5.0f} "
              f"{s['lazer']:6.0f} {mi(s['custo'])} {mi(s['vgv'])} {s['eiv_vc']/1e6:5.2f} {mi(s['resultado'])} {s['margem']*100:4.0f}% "
              f"{s['eiv_tipo']} {[c[0] for c in checks(s) if not c[2]]}")


# travessões (no PDF original eram glifos desenhados, perdidos na extração do texto)
for _s in ORIG + NEW + V100:
    _s['rows'] = [(r[0].replace('  ', ' – '),) + tuple(r[1:]) for r in _s['rows']]
    _s['curto'] = _s['curto'].replace('  ', ' – ')
    _s['nome'] = _s['nome'].replace('  ', ' – ')
