"""Caderno comparativo (A3) — 153."""
import copy, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'estudo-151-studios', 'gerador'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import model153 as M
from render import br, mi, W, H, TXT, GREY

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['text.parse_math'] = False
LOGO = os.path.join(HERE, '..', '..', 'estudo-151-studios', 'gerador', 'assets', 'p2_img18.png')
C1, C2 = '#8a99ab', '#1e3556'          # família 2Q+3Q / família 2Q+studios
TERRENO = 3282771.82                   # valor venal (CND 61834/2026)


def page(title, n):
    fig = plt.figure(figsize=(W / 72, H / 72), dpi=72)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')
    ax.text(34, 82, title, fontsize=30, fontweight='bold', color='#6e6e6e')
    ax.imshow(plt.imread(LOGO), extent=(34, 108.2, 796.5, 746.9), zorder=5)
    ax.text(119.1, 783.5, 'T & L Engenharia', fontsize=8, fontweight='bold', color='#1e3556')
    ax.text(119.1, 793.7, 'Araucária • Paraná', fontsize=6.5, color=GREY)
    ax.plot([206, 206], [776, 797], lw=0.4, color='#9aa3ad')
    ax.text(214, 783.5, 'Marielen Ferri', fontsize=8, fontweight='bold', color='#1e3556')
    ax.text(214, 793.7, 'Arquitetura', fontsize=6.5, color=GREY)
    ax.text(977.9, 739.8, 'Comparativo', fontsize=13, color=TXT, ha='right')
    ax.text(977.9, 768.2, '153 •  Estudo de Viabilidade', fontsize=11, fontweight='bold', color=TXT, ha='right')
    ax.text(977.9, 786.6, 'R. Alexandre Wisocki, 249  .  R00     out.26', fontsize=8.5, color=TXT, ha='right')
    ax.text(1153.7, 787.5, f'{n:02d}', fontsize=30, color=TXT, ha='right')
    ax.text(1158.8, 819.2, 'a viabilidade técnico-legal do estudo deve ser confirmada através de consulta formal junto aos órgãos públicos '
            'e da confrontação com levantamento planialtimétrico a ser fornecido pelo proprietário', fontsize=4.8, color=GREY, ha='right')
    return fig, ax


def table(ax, x0, y0, cols, rows, size=6.8, rowh=15.5, hl=None):
    for x, ha, t in cols:
        ax.text(x, y0, t, fontsize=size, fontweight='bold', color='black', ha=ha)
    ax.plot([x0, cols[-1][0]], [y0 + 5, y0 + 5], lw=0.5, color='black')
    y = y0 + 5 + rowh
    for i, r in enumerate(rows):
        if r is None:
            ax.plot([x0, cols[-1][0]], [y - rowh + 6, y - rowh + 6], lw=0.3, color='#999999'); continue
        if hl and hl(r):
            ax.add_patch(plt.Rectangle((x0, y - 10.5), cols[-1][0] - x0, 14, color=(0.94, 0.92, 0.88), lw=0))
        for (x, ha, _), v in zip(cols, r):
            ax.text(x, y, v, fontsize=size, color='black', ha=ha)
        y += rowh
    ax.plot([x0, cols[-1][0]], [y - rowh + 6, y - rowh + 6], lw=0.4, color='black')
    return y


def bars(fig, rect, vals, title, labels, colors):
    ax = fig.add_axes(rect)
    x = range(len(vals))
    ax.bar(x, vals, 0.55, color=colors)
    top = max(vals)
    for i, v in enumerate(vals):
        ax.text(i, v + top * 0.015 if v >= 0 else v / 2, br(v, 1), ha='center', va='bottom' if v >= 0 else 'center', fontsize=6.8,
                color=TXT if v >= 0 else 'white', fontweight='bold')
    ax.axhline(0, color='#999999', lw=0.6)
    ax.set_xticks(list(x)); ax.set_xticklabels(labels, fontsize=7.2, color=TXT)
    ax.set_title(title, fontsize=9, loc='left', color='black', fontweight='bold', pad=10)
    for s in ('top', 'right', 'left'):
        ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(axis='y', labelsize=6.5, colors=GREY, length=0); ax.tick_params(axis='x', length=0)
    ax.yaxis.grid(True, color='#e6e6e6', lw=0.5); ax.set_axisbelow(True)
    ax.set_ylabel('R$ milhões', fontsize=6.5, color=GREY)
    lo = min(0, min(vals))
    ax.set_ylim(lo * 1.25 if lo < 0 else 0, top * 1.15)


def p1(pdf):
    fig, ax = page('COMPARATIVO', 1)
    ax.text(34, 108, 'Lote 08-A (1.524,00 m², ZR3, 24,00 m de frente): torre única de 15,00 m de largura, subsolo em faixa e '
            'rampa lateral. Duas famílias de produto, CA básico (2,5) e máximo (3,0).', fontsize=8.5, color=TXT)
    cols = [(36, 'left', 'Opção'), (290, 'right', 'Pav.'), (322, 'right', 'Unid.'), (352, 'right', '2Q'), (380, 'right', '3Q'),
            (414, 'right', 'Studios'), (466, 'right', 'Priv. (m²)'), (500, 'right', 'CA'), (540, 'right', 'Vagas'),
            (580, 'right', 'Subsolos'), (650, 'right', 'Custo obra'), (720, 'right', 'VGV'), (790, 'right', 'Resultado*'),
            (830, 'right', 'Marg.'), (905, 'right', 'Res. − terreno**'), (960, 'right', 'EIV'), (1156, 'right', 'R$ VGV / m² priv.')]
    rows = []
    for i, o in enumerate(M.OPTS):
        if i == 3:
            rows.append(None)
        rows.append([o['label'], str(o['n'] + 1), str(o['nun']), str(o['n2']), str(o['n3']), str(o['nst']), br(o['priv']),
                     br(o['ca']), str(o['vagas']), str(o['nsub']), mi(o['custo']), mi(o['vgv']), mi(o['resultado']),
                     f"{o['margem'] * 100:.0f}%", mi(o['resultado'] - TERRENO), o['eiv'], 'R$ ' + br(o['vgv_un'] / o['priv'], 0)])
    best = max(M.OPTS, key=lambda o: o['resultado'])['label']
    y = table(ax, 34, 140, cols, rows, size=6.8, hl=lambda r: r[0] == best)
    ax.text(34, y + 2, '*Resultado = VGV − custo da obra (CUB-PR ago/2026 R8-N, ±20%) − contrapartida EIV. Não inclui terreno, impostos, '
            'projetos/aprovação e comercialização.', fontsize=5.8, color=GREY)
    ax.text(34, y + 10, f"**Descontando o terreno pelo valor venal da CND (R$ {br(TERRENO / 1e6, 2)} mi) — referência, não é o valor de mercado nem o custo de aquisição.",
            fontsize=5.8, color=GREY)
    yb = y + 46
    hgt = 690 - yb
    labs = [o['key'] for o in M.OPTS]
    cols_ = [C1 if o['tipo'] == '2Q + 3Q' else C2 for o in M.OPTS]
    bars(fig, [34 / W, 1 - (yb + hgt) / H, 520 / W, (hgt - 20) / H], [o['vgv'] / 1e6 for o in M.OPTS], 'VGV (R$ milhões)', labs, cols_)
    bars(fig, [636 / W, 1 - (yb + hgt) / H, 520 / W, (hgt - 20) / H], [o['resultado'] / 1e6 for o in M.OPTS],
         'Resultado* (R$ milhões)', labs, cols_)
    ax.add_patch(plt.Rectangle((880, yb - 22), 9, 7, color=C1)); ax.text(893, yb - 16, 'Família 2Q + 3Q', fontsize=6.8, color=TXT)
    ax.add_patch(plt.Rectangle((990, yb - 22), 9, 7, color=C2)); ax.text(1003, yb - 16, 'Família 2Q + studios', fontsize=6.8, color=TXT)
    pdf.savefig(fig); plt.close(fig)


def scen(**kw):
    keep = dict(M.P); M.P.update(kw)
    out = {}
    for o in M.OPTS:
        n = M.option(o['key'], o['tipo'], o['ca_mode'], o['n'], o['fk'],
                     o['nsub'], o['label'])
        out[o['key']] = n
    M.P.clear(); M.P.update(keep)
    return out


def p2(pdf):
    fig, ax = page('SENSIBILIDADE', 2)
    ax.text(34, 108, 'Resultado* de cada opção variando o preço de venda (as demais premissas fixas).', fontsize=8.5, color=TXT)
    base2q = M.P['preco_2q']
    cases = [('2Q/3Q −10%', dict(preco_2q=base2q * 0.9, preco_3q=M.P['preco_3q'] * 0.9)),
             ('base', {}),
             ('2Q/3Q +10%', dict(preco_2q=base2q * 1.1, preco_3q=M.P['preco_3q'] * 1.1)),
             ('studio = 2Q', dict(preco_st=base2q)),
             ('studio +30%', dict(preco_st=base2q * 1.3)),
             ('custo +10%', dict(custo_torre=M.P['custo_torre'] * 1.1, custo_subsolo=M.P['custo_subsolo'] * 1.1))]
    sc = [(n, scen(**k)) for n, k in cases]
    cols = [(36, 'left', 'Opção')] + [(330 + 100 * i, 'right', n) for i, (n, _) in enumerate(sc)]
    rows = [[o['label']] + [mi(s[o['key']]['resultado']) for _, s in sc] for o in M.OPTS]
    y = table(ax, 34, 140, cols, rows, size=7.0, rowh=16)
    # preço de equilíbrio do 2Q/3Q para pagar o terreno com 15% de margem
    ax.text(34, y + 8, 'Preço mínimo do m² (2Q/3Q, mantida a proporção) para resultado ≥ terreno (valor venal) + 15% do VGV:', fontsize=7.5,
            color='black', fontweight='bold')
    yy = y + 24
    for o in M.OPTS:
        lo, hi = 3000, 15000
        for _ in range(40):
            mid = (lo + hi) / 2
            r = scen(preco_2q=mid, preco_3q=mid * M.P['preco_3q'] / M.P['preco_2q'],
                     preco_st=mid * M.P['preco_st'] / M.P['preco_2q'])[o['key']]
            if r['resultado'] - TERRENO >= 0.15 * r['vgv']:
                hi = mid
            else:
                lo = mid
        ax.text(46, yy, f"• {o['label']}: 2Q a R$ {br(hi, 0)}/m²"
                + (f" (studio R$ {br(hi * 1.2, 0)}/m²)" if o['nst'] else ''), fontsize=7.0, color=TXT)
        yy += 12
    y0 = yy + 20
    ax.text(34, y0, 'Base legal aplicada (Araucária – ZR3)', fontsize=9, fontweight='bold', color='black')
    leg = [('LC 25/2020 (ZR3)', 'CA 2,5 / 3,0 (Compensação Paisagística); TO base 65% (60% no máx.) e torre 65% (50% no máx.); perm. 20% (25% no máx.); '
                                '14 pav.; recuo frontal 5,00 m; afastamento da torre H/8 (mín. 2,00 m); base 0 m / 1,5 m c/ abertura.'),
           ('LC 26/2020, art. 151', 'Não computáveis: subsolo de estacionamento, ático ≤ 1/3, escada enclausurada, poço de elevador, guarita (≤ 6 m²), lixo e gás.'),
           ('LC 26/2020, art. 157/158', 'Vaga 2,40 × 5,00 m; corredor 5,00 m a 90°; vão de entrada 5,00 m (> 50 vagas); vagas fora do recuo frontal (as duas testadas).'),
           ('LC 26/2020, art. 258/259 + Anexo VII', 'Studio ≤ 30 m² úteis conjugado + banho; 1 vaga a cada 3 studios; aptos 1 vaga/un.; visitantes 5%; bicicletas 15% / 30%.'),
           ('LC 26/2020, art. 167 / 178', 'Pista de acumulação acima de 50 vagas; recreação ≥ 6 m²/unidade (50% contínua, 25% permeável).'),
           ('Lei 4.688/2025 (EIV)', 'EIV Tipo 1 a partir de 130 unidades; Tipo 2 a partir de 200 vagas — nenhuma opção atinge.')]
    yy = y0 + 18
    for a, b in leg:
        ax.text(34, yy, a, fontsize=6.8, fontweight='bold', color='black'); ax.text(220, yy, b, fontsize=6.6, color=TXT); yy += 14
    pdf.savefig(fig); plt.close(fig)


def p3(pdf):
    import render153 as RR
    fig, ax = page('LEITURA', 3)
    o = {k['key']: k for k in M.OPTS}
    txt = [
        ('1. O que limita este lote', [
            'Frente de 24 m: cabe uma torre de 15 m de largura com afastamentos ≥ H/8, e o estacionamento só se organiza em faixa (corredor central + 2 fileiras).',
            'Um subsolo comporta 36 vagas; o térreo, sob pilotis, até 36 — mas cada vaga no térreo é lazer a menos. O 2º subsolo (E3) custa mais do que rende.',
            'O teto de VGV é o CA: 3.810 m² (básico) ou 4.572 m² (máximo, condicionado à Compensação Paisagística).']),
        ('2. Família 2Q + 3Q', [
            f"Melhor: {o['E2']['label']} — {o['E2']['nun']} unidades, VGV {mi(o['E2']['vgv'])}, resultado {mi(o['E2']['resultado'])} "
            f"(margem {o['E2']['margem'] * 100:.0f}%). No CA básico (E1) a margem cai a {o['E1']['margem'] * 100:.0f}%.",
            'Com as premissas atuais, nenhuma opção 2Q+3Q paga o terreno pelo valor venal: só se viabiliza com preço de venda maior (ver sensibilidade) ou custo menor.']),
        ('3. Família 2Q + studios', [
            f"Melhor: {o['E6']['label']} — {o['E6']['nun']} unidades ({o['E6']['nst']} studios), VGV {mi(o['E6']['vgv'])}, resultado {mi(o['E6']['resultado'])} "
            f"(margem {o['E6']['margem'] * 100:.0f}%), sem EIV (< 130 un.).",
            f"Alternativa mais equilibrada: {o['E5']['label']} — {o['E5']['nun']} un. ({o['E5']['n2']} aptos 2Q), resultado {mi(o['E5']['resultado'])}.",
            'O studio rende mais aqui pelos mesmos motivos do 151: m² mais caro e 1 vaga a cada 3 unidades (o subsolo único basta).']),
        ('4. Recomendação', [
            'Se o CA máximo for confirmado: E6 (máximo resultado) ou E5 (mix mais vendável). Sem CA máximo: E4 (2Q + studios, CA básico).',
            'Família 2Q + 3Q só faz sentido com preço de venda acima de ~R$ 8 mil/m² — validar com corretor antes de seguir.',
            'Antes do anteprojeto: levantamento planialtimétrico, sondagem, consulta à SMUR sobre Compensação Paisagística e recuo na R. Zdenko Gayer.']),
        ('Ressalvas', [f'{i + 1}. {t}' for i, t in enumerate(RR.RESSALVAS)]),
    ]
    y = 120
    for h, items in txt:
        ax.text(34, y, h, fontsize=10, fontweight='bold', color='black' if h != 'Ressalvas' else '#9a1b1b'); y += 18
        for t in items:
            ax.text(46, y, ('• ' if h != 'Ressalvas' else '') + t, fontsize=7.4, color=TXT); y += 14
        y += 10
    pdf.savefig(fig); plt.close(fig)


if __name__ == '__main__':
    fn = os.path.join(sys.argv[1], '153 COMPARATIVO - OPCOES.pdf')
    with PdfPages(fn) as pdf:
        p1(pdf); p2(pdf); p3(pdf)
        d = pdf.infodict(); d['Title'] = '153 Estudo de Viabilidade – Comparativo'; d['Author'] = 'T & L Engenharia / Marielen Ferri Arquitetura'
    print('ok', fn)
