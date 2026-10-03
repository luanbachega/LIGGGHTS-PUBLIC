"""Caderno comparativo (A3) — 151 versões com studios."""
import copy, sys, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pymupdf
import model as M
from render import br, mi, W, H, NAVY, TXT, GREY, REV, DATE

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['text.parse_math'] = False
C_ORIG = '#b8bec6'
C_NEW = '#1e3556'
LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'p2_img18.png')
OUT = sys.argv[1] if len(sys.argv) > 1 else '../out'
PAIRS = [('A', 'A2'), ('B', 'B2'), ('C', 'C2'), ('C', 'C3'), ('D', 'D2')]
BYK = {s['key']: s for s in M.ORIG + M.NEW + M.V100}


def page(title, n):
    fig = plt.figure(figsize=(W / 72, H / 72), dpi=72)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')
    ax.text(34, 82, title, fontsize=30, fontweight='bold', color='#6e6e6e')
    img = plt.imread(LOGO)
    ax.imshow(img, extent=(34, 108.2, 796.5, 746.9), zorder=5)
    ax.text(119.1, 783.5, 'T & L Engenharia', fontsize=8, fontweight='bold', color='#1e3556')
    ax.text(119.1, 793.7, 'Araucária • Paraná', fontsize=6.5, color=GREY)
    ax.plot([206, 206], [776, 797], lw=0.4, color='#9aa3ad')
    ax.text(214, 783.5, 'Marielen Ferri', fontsize=8, fontweight='bold', color='#1e3556')
    ax.text(214, 793.7, 'Arquitetura', fontsize=6.5, color=GREY)
    ax.text(977.9, 739.8, 'Comparativo', fontsize=13, color=TXT, ha='right')
    ax.text(977.9, 768.2, '151 •  Estudo de Viabilidade', fontsize=11, fontweight='bold', color=TXT, ha='right')
    ax.text(977.9, 786.6, f'Versões com studios  .  {REV}     {DATE}', fontsize=8.5, color=TXT, ha='right')
    ax.text(1153.7, 787.5, f'{n:02d}', fontsize=30, color=TXT, ha='right', fontweight='light')
    ax.text(1158.8, 819.2, 'a viabilidade técnico-legal do estudo deve ser confirmada através de consulta formal junto aos órgãos públicos '
            'e da confrontação com levantamento planialtimétrico a ser fornecido pelo proprietário', fontsize=4.8, color=GREY, ha='right')
    return fig, ax


def bars(fig, rect, metric, title, fmt):
    ax = fig.add_axes(rect)
    labels = [b for a, b in PAIRS]
    x = range(len(PAIRS))
    w = 0.36
    vo = [BYK[a][metric] / 1e6 for a, b in PAIRS]
    vn = [BYK[b][metric] / 1e6 for a, b in PAIRS]
    ax.bar([i - w / 2 - 0.01 for i in x], vo, w, color=C_ORIG, label='Estudo original (R00)')
    ax.bar([i + w / 2 + 0.01 for i in x], vn, w, color=C_NEW, label='Versão com studios')
    for i in x:
        ax.text(i - w / 2 - 0.01, vo[i] + max(vn) * 0.015, fmt(vo[i]), ha='center', fontsize=6.3, color=GREY)
        ax.text(i + w / 2 + 0.01, vn[i] + max(vn) * 0.015, fmt(vn[i]), ha='center', fontsize=6.6, color=TXT, fontweight='bold')
    ax.set_xticks(list(x))
    ax.set_xticklabels([f'{a} → {b}' for a, b in PAIRS], fontsize=7.5, color=TXT)
    ax.set_title(title, fontsize=9, loc='left', color='black', fontweight='bold', pad=10)
    for s in ('top', 'right', 'left'):
        ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color('#999999')
    ax.tick_params(axis='y', labelsize=6.5, colors=GREY, length=0)
    ax.tick_params(axis='x', length=0)
    ax.yaxis.grid(True, color='#e6e6e6', lw=0.5); ax.set_axisbelow(True)
    ax.set_ylim(0, max(vn + vo) * 1.15)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, p: f'{v:.0f}'))
    ax.set_ylabel('R$ milhões', fontsize=6.5, color=GREY)
    return ax


def table(ax, x0, y0, cols, rows, size=6.8, rowh=15.5, hl=None, bold_rows=()):
    for x, ha, t in cols:
        ax.text(x, y0, t, fontsize=size, fontweight='bold', color='black', ha=ha)
    ax.plot([x0, cols[-1][0]], [y0 + 5, y0 + 5], lw=0.5, color='black')
    y = y0 + 5 + rowh
    for i, r in enumerate(rows):
        if r is None:
            ax.plot([x0, cols[-1][0]], [y - rowh + 6, y - rowh + 6], lw=0.3, color='#999999'); continue
        if hl and hl(i, r):
            ax.add_patch(plt.Rectangle((x0, y - 10.5), cols[-1][0] - x0, 14, color=(0.94, 0.92, 0.88), lw=0))
        for (x, ha, _), v in zip(cols, r):
            ax.text(x, y, v, fontsize=size, color='black', ha=ha, fontweight='bold' if i in bold_rows else 'normal')
        y += rowh
    ax.plot([x0, cols[-1][0]], [y - rowh + 6, y - rowh + 6], lw=0.4, color='black')
    return y


def p1(pdf):
    fig, ax = page('COMPARATIVO', 1)
    ax.text(34, 108, 'Versões com studios (kitnet) dos estudos A, B, C e D — mesma implantação, mesmas torres; '
            'muda o pavimento tipo, o nº de pavimentos onde a lei permite e a estrutura de garagem.', fontsize=8.5, color=TXT)
    cols = [(36, 'left', 'Estudo'), (250, 'right', 'Unid.'), (292, 'right', '2Q'), (334, 'right', 'Studios'),
            (392, 'right', 'Priv. (m²)'), (430, 'right', 'CA'), (474, 'right', 'Vagas'), (514, 'right', 'Exig.'),
            (582, 'right', 'Custo obra'), (650, 'right', 'VGV'), (705, 'right', 'EIV est.'), (775, 'right', 'Resultado*'),
            (820, 'right', 'Marg.'), (880, 'right', 'Δ result.'), (1156, 'right', 'O que muda')]
    what = {
        'A': 'térreo pilotis, 127 vagas no térreo', 'B': 'embasamento c/ 2 pav. de garagem + deck', 'C': '1 subsolo (108 vagas)',
        'D': 'edifício garagem térreo + 3 pav. + cobertura',
        'A2': 'tipo misto; T2 +1 pav.; 27 vagas excedentes', 'B2': 'tipo misto; mesmo volume; 56 vagas excedentes',
        'C2': 'tipo misto; subsolo reduzido a 60 vagas', 'C3': '100% studios; SEM subsolo',
        'D2': 'tipo misto; T2 +1 pav.; ed. garagem −1 pav.',
        'A2-100': '100% studios (lazer +73 m²)', 'B2-100': '100% studios; deck → lazer', 'D2-100': '100% studios; ed. garagem só térreo + cob.'}
    base = {'A2': 'A', 'B2': 'B', 'C2': 'C', 'C3': 'C', 'D2': 'D', 'A2-100': 'A', 'B2-100': 'B', 'D2-100': 'D'}
    seq = ['A', 'B', 'C', 'D', None, 'A2', 'B2', 'C2', 'C3', 'D2', None, 'A2-100', 'B2-100', 'D2-100']
    rows = []
    for k in seq:
        if k is None:
            rows.append(None); continue
        s = BYK[k]
        d = s['resultado'] - BYK[base[k]]['resultado'] if k in base else None
        rows.append([s['curto'] if k not in ('A2-100', 'B2-100', 'D2-100') else f"{k} (indicativo)", str(s['nun']), str(s['n2q']),
                     str(s['nst']), br(s['priv']), br(s['ca']), str(s['vagas']), str(s['vx']['total']), mi(s['custo']),
                     mi(s['vgv']), mi(s['eiv_vc']) if s['eiv_vc'] else '—', mi(s['resultado']), f"{s['margem'] * 100:.0f}%",
                     ('+' if d >= 0 else '') + br(d / 1e6, 1) + ' mi' if d is not None else '', what[k]])
    best = max(M.NEW, key=lambda s: s['resultado'])['key']
    y = table(ax, 34, 140, cols, rows, size=6.8, hl=lambda i, r: r[0].startswith(best + ' '))
    ax.text(34, y + 2, '*Resultado = VGV − custo da obra − contrapartida estimada do EIV (Lei 4.688/2025). Não inclui terreno, impostos, '
            'projetos/aprovação e comercialização. Custos dos R00 mantidos; versões com studios calculadas por diferença.', fontsize=5.8, color=GREY)
    ax.text(34, y + 10, f"VGV: 2Q R$ {br(M.P['preco_2q'], 0)}/m² • studio R$ {br(M.P['preco_st'], 0)}/m² • vaga excedente "
            f"R$ {br(M.P['preco_vaga'] / 1000, 0)} mil.  Linhas “indicativo”: só números, sem prancha; dependem de pequenos ajustes de lazer.",
            fontsize=5.8, color=GREY)
    yb = (y + 40)
    hgt = 690 - yb
    bars(fig, [34 / W, 1 - (yb + hgt) / H, 520 / W, (hgt - 20) / H], 'vgv', 'VGV (R$ milhões)', lambda v: br(v, 1))
    bars(fig, [636 / W, 1 - (yb + hgt) / H, 520 / W, (hgt - 20) / H], 'resultado', 'Resultado* (R$ milhões)', lambda v: br(v, 1))
    ax.add_patch(plt.Rectangle((900, yb - 22), 9, 7, color=C_ORIG)); ax.text(913, yb - 16, 'Estudo original (R00)', fontsize=6.8, color=TXT)
    ax.add_patch(plt.Rectangle((1010, yb - 22), 9, 7, color=C_NEW)); ax.text(1023, yb - 16, 'Versão com studios', fontsize=6.8, color=TXT)
    pdf.savefig(fig); plt.close(fig)


def scenario(prem):
    """resultado de cada estudo com o studio a (1+prem) x preço do 2Q."""
    keep = M.P['preco_st']
    M.P['preco_st'] = M.P['preco_2q'] * (1 + prem)
    out = {}
    for s in M.ORIG + M.NEW + M.V100:
        t = copy.deepcopy(s); M.finance(t); out[s['key']] = t
    M.P['preco_st'] = keep
    return out


def p2(pdf):
    fig, ax = page('SENSIBILIDADE', 2)
    ax.text(34, 108, 'O preço do m² do studio é a premissa que mais pesa. Abaixo, o resultado* de cada versão com o studio vendido '
            'a 0% / +10% / +20% / +30% sobre o m² do 2Q.', fontsize=8.5, color=TXT)
    prems = [0.0, 0.10, 0.20, 0.30]
    sc = {p: scenario(p) for p in prems}
    cols = [(36, 'left', 'Estudo'), (300, 'right', 'Original R00')] + \
           [(380 + 80 * i, 'right', f'+{int(p * 100)}%' if p else 'mesmo R$/m²') for i, p in enumerate(prems)] + \
           [(720, 'right', 'empata c/ R00 em')]
    rows = []
    for a, b in PAIRS:
        o = sc[0.2][a]['resultado']
        r = [BYK[b]['curto'], mi(o)] + [mi(sc[p][b]['resultado']) for p in prems]
        # prêmio de empate
        lo, hi = -0.5, 0.5
        for _ in range(40):
            mid = (lo + hi) / 2
            if scenario(mid)[b]['resultado'] >= o:
                hi = mid
            else:
                lo = mid
        r.append(f"{hi * 100:+.0f}%")
        rows.append(r)
    y = table(ax, 34, 140, cols, rows, size=7.2, rowh=17)
    ax.text(34, y + 2, '“empata c/ R00 em”: prêmio (ou desconto) do m² do studio sobre o m² do 2Q a partir do qual a versão com studios supera o estudo original. '
            'Valores negativos = a versão com studios já ganha mesmo vendendo o studio mais barato por m².', fontsize=5.8, color=GREY)

    # premissas e base legal
    y0 = y + 40
    ax.text(34, y0, 'Base legal aplicada (Araucária – ZR3)', fontsize=9, fontweight='bold', color='black')
    leg = [
        ('LC 26/2020, art. 258', 'Studio = 1 compartimento conjugado (sala/quarto/cozinha, sem divisórias) de até 30,00 m² úteis + instalação sanitária. '
                                 'Adotado: 27,13 m² privativos (~22 m² conjugado + banho ~3,5 m²) e 30,53 m² no C3.'),
        ('LC 26/2020, art. 259 + Anexo VII', '1 vaga a cada 1 a 3 studios; 2Q: 1 vaga/unidade; visitantes 5% (art. 268, V); bicicletas +15% (2Q) e +30% (studios); frações desprezadas.'),
        ('LC 26/2020, art. 178', 'Recreação ≥ 6,00 m² por unidade (50% contínua, 25% permeável) — é o limite que trava “100% studio” no A, B e D sem ajuste de lazer.'),
        ('LC 26/2020, art. 268, II', 'Distância entre torres (H/6)×2 ≥ 5 m: as alturas dos R00 já estão no limite; só a T2 do A e do D sobe até igualar a T1.'),
        ('LC 25/2020 (ZR3)', 'CA 2,5 básico / 3,0 máx. (compensação paisagística — B/B2); TO e permeabilidade inalteradas; ≤ 14 pavimentos.'),
        ('Lei 4.688/2025 (EIV)', 'EIV Tipo 1 obrigatório a partir de 130 unidades (todas as versões com studios; o A original, com 120, não exigia). '
                                 'Tipo 2 a partir de 200 vagas — todas as versões ficam abaixo. Contrapartida estimada com GI 0,05 (AP 1,25 acima de 200 un.).'),
        ('LC 26/2020, art. 165 §2º', 'Vagas privativas de condomínio vertical dispensadas da reserva PcD/idoso; as de visitantes seguem a regra (2% + 3%).'),
        ('Federal', 'Lei 13.146/2015 e Dec. 9.451/2018: unidades adaptáveis — banho do studio dimensionado para adaptação (≈1,60 × 2,20 m). '
                    'CSCIP/CBMPR: altura e circulações iguais aos R00; população por andar do tipo misto é menor que a do tipo 2Q.'),
    ]
    yy = y0 + 18
    for a, b in leg:
        ax.text(34, yy, a, fontsize=6.8, fontweight='bold', color='black')
        ax.text(200, yy, b, fontsize=6.6, color=TXT, wrap=True)
        yy += 15
    # premissas
    ax.text(34, yy + 18, 'Premissas (editáveis na planilha)', fontsize=9, fontweight='bold', color='black')
    pr = [f"Preço 2Q R$ {br(M.P['preco_2q'], 0)}/m² privativo (vaga inclusa) • studio R$ {br(M.P['preco_st'], 0)}/m² (+20%) • vaga excedente R$ {br(M.P['preco_vaga'], 0)}.",
          f"Custo: R00 mantidos (CUB-PR ago/2026, R8-N); pavimento tipo adicional R$ {br(M.P['custo_torre'], 0)}/m²; unidade adicional R$ {br(M.P['custo_un_extra'], 0)} "
          f"(cozinha, banho, porta, medição); garagem suprimida: embasamento R$ {br(M.P['custo_garagem_emb'], 0)}/m², subsolo R$ {br(M.P['custo_subsolo'], 0)}/m², "
          f"ed. garagem R$ {br(M.P['custo_edgar'], 0)}/m² (custos/vaga implícitos nos R00).",
          'Preços de venda NÃO foram validados em pesquisa de mercado local (portais bloqueados neste ambiente) — confirmar com corretor/cliente antes de decidir.',
          'Consulta prévia do lote (23/09/2026) ainda exibe parâmetros da lei anterior (“ZR”, 3 pav.); estudo segue ZR3 (LC 25/2020) — confirmar na SMUR.']
    for i, t in enumerate(pr):
        ax.text(34, yy + 34 + 12 * i, '• ' + t, fontsize=6.6, color=TXT)
    pdf.savefig(fig); plt.close(fig)


def p3(pdf):
    fig, ax = page('LEITURA', 3)
    best = max(M.NEW, key=lambda s: s['resultado'])
    A2, B2, C2, C3, D2 = (BYK[k] for k in ('A2', 'B2', 'C2', 'C3', 'D2'))
    txt = [
        ('1. Por que studio rende tanto aqui', [
            'O gargalo dos 4 estudos é a vaga: cada apto 2Q exige 1 vaga (+5%), e a vaga cara (embasamento, subsolo, ed. garagem) consome o resultado.',
            'Pelo art. 259, 3 studios exigem 1 vaga. Trocando 2 aptos 2Q por 3 studios na mesma área, a exigência cai à metade e o nº de unidades sobe 50%.',
            'O ganho vem de 3 frentes: m² de studio vende mais caro, sobra vaga para vender/cortar, e dá para subir pavimento onde a vaga travava (T2 do A e do D).']),
        ('2. Ranking (premissas base)', [
            f"Maior VGV e maior resultado: {best['curto']} — VGV {mi(best['vgv'])}, resultado {mi(best['resultado'])}, "
            f"sem subsolo (economia de ~R$ {br(3001.6 * M.P['custo_subsolo'] / 1e6, 1)} mi em escavação/estrutura).",
            f"Melhor custo-benefício com produto misto: {A2['curto']} — menor investimento ({mi(A2['custo'])}), margem {A2['margem'] * 100:.0f}%, "
            f"resultado {mi(A2['resultado'])}; mantém 64 aptos 2Q.",
            f"C2 ({mi(C2['resultado'])}) e D2 ({mi(D2['resultado'])}) melhoram muito o C e o D, mas ainda carregam garagem estruturada; "
            f"B2 ({mi(B2['resultado'])}) é o que menos ganha: o volume já está no CA máximo e as 56 vagas excedentes são de embasamento."]),
        ('3. Riscos e pontos de atenção', [
            'Absorção: 252 studios (C3) é muito para Araucária se o produto for só “compra para morar”. A tese depende de demanda de locação '
            '(REPAR/polo industrial, prestadores em paradas de manutenção, estudantes) — validar com pesquisa/corretor.',
            'A2 e D2 mantêm ~40% de 2Q: diversificam o produto e diluem o risco de liquidez. C3 pode ser faseado (torre 1 → torre 2).',
            'EIV Tipo 1 passa a ser exigido em todas as versões (≥130 un.): prazo de aprovação maior e contrapartida (estimada na tabela).',
            'Lazer: C3 usa 1.518 m² para 1.512 exigidos — sem folga; qualquer perda de área de lazer no projeto exige compensação (rooftop/terraço).',
            'Studio é unidade de 1 ambiente “livre de paredes” (art. 258, parágrafo único): o projeto não pode prever divisória de quarto.']),
        ('4. Recomendação', [
            'Levar ao cliente duas leituras: (i) C3 como “máximo VGV” se a pesquisa de mercado sustentar o volume de studios; '
            '(ii) A2 como “custo-benefício seguro” (menor capital, maior margem, produto misto).',
            'Próximos passos: pesquisa de preço/absorção de studio em Araucária; confirmar ZR3 na SMUR (consulta prévia com parâmetros antigos); '
            'levantamento planialtimétrico; pré-consulta do EIV.']),
    ]
    y = 120
    for h, items in txt:
        ax.text(34, y, h, fontsize=10, fontweight='bold', color='black'); y += 18
        for t in items:
            ax.text(46, y, '• ' + t, fontsize=7.6, color=TXT); y += 14
        y += 12
    pdf.savefig(fig); plt.close(fig)


if __name__ == '__main__':
    fn = os.path.join(OUT, '151 COMPARATIVO - VERSOES COM STUDIOS.pdf')
    with PdfPages(fn) as pdf:
        p1(pdf); p2(pdf); p3(pdf)
        d = pdf.infodict(); d['Title'] = '151 Estudo de Viabilidade – Comparativo versões com studios'
        d['Author'] = 'T & L Engenharia / Marielen Ferri Arquitetura'
    print('ok', fn)
