import os, sys, pymupdf
import model as M
import render as R

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
os.makedirs(OUT, exist_ok=True)

COMPARE = M.ORIG + M.NEW
MX_A = 'misto: 6 studios + 4 aptos 2Q por torre'
MX_C = 'misto: 6 studios + 6 aptos 2Q por torre'

CFG = {
    'A2': ('A', '151 ESTUDO A2 - VAGAS TERREO + STUDIOS.pdf', dict(
        sub='Estudo A2 – Vagas no térreo + studios',
        diag=dict(raise_T2=1, relabel={'Pav. tipo': f'Pav. tipo 8x (T1 e T2) – {MX_A}'}),
        occ=dict(kind='A', mix='misto', tipo_title='Pavimento Tipo misto (cada torre)'))),
    'B2': ('B', '151 ESTUDO B2 - VAGAS TERREO E 2 PAVIMENTOS + STUDIOS.pdf', dict(
        sub='Estudo B2 – Vagas no térreo e 2 pavimentos + studios',
        diag=dict(relabel={'Pav. tipo': f'Pav. tipo 10x – {MX_A}'}),
        occ=dict(kind='A', mix='misto', tipo_title='Pavimento Tipo misto (cada torre)'))),
    'C2': ('C', '151 ESTUDO C2 - SUBSOLO REDUZIDO + STUDIOS.pdf', dict(
        sub='Estudo C2 – Subsolo reduzido + studios',
        diag=dict(relabel={'Pav. tipo': f'Pav. tipo 9x – {MX_C}',
                           'Subsolo': 'Subsolo reduzido (60 vagas) – estacionamento'}),
        occ=dict(kind='C', mix='misto', tipo_title='Pavimento Tipo misto (cada torre)',
                 relabels=[('108 vagas', 'Subsolo reduzido – 60 vagas')]))),
    'C3': ('C', '151 ESTUDO C3 - SEM SUBSOLO 100% STUDIOS.pdf', dict(
        sub='Estudo C3 – Sem subsolo, 100% studios',
        diag=dict(relabel={'Pav. tipo': 'Pav. tipo 9x – 100% studios: 14 por torre'}, drop_label='Subsolo'),
        occ=dict(kind='C', mix='studio', tipo_title='Pavimento Tipo 100% studios (cada torre)',
                 drop_region=(600, 100, 1080, 445)))),
    'D2': ('D', '151 ESTUDO D2 - EDIFICIO GARAGEM + STUDIOS.pdf', dict(
        sub='Estudo D2 – Edifício garagem + studios',
        diag=dict(raise_T2=1, lower_garage=1,
                  relabel={'Pav. tipo': f'Pav. tipo 9x (T1 e T2) – {MX_A}'},
                  texts=[(482.5, 151.4, 'Edifício garagem'), (482.5, 160.7, '(térreo + 2 pav. + cobertura)')]),
        occ=dict(kind='A', mix='misto', tipo_title='Pavimento Tipo misto (cada torre)',
                 relabels=[('(4x)', 'Ed. garagem – pav. tipo (3x) – 23 vagas')]))),
}


def c3_note(ov):
    ov.text(830, 270, 'Sem subsolo', size=11, color='black', ha='center')
    ov.text(830, 286, '252 studios exigem 88 vagas (84 + 4 visitantes) — LC 26/2020, art. 259 e Anexo VII', size=6.5,
            color=R.GREY, ha='center')
    ov.text(830, 296, 'as 91 vagas do térreo (sem alteração) atendem a exigência', size=6.5, color=R.GREY, ha='center')


if __name__ == '__main__':
    only = sys.argv[2:] or list(CFG)
    for key in only:
        base, fn, cfg = CFG[key]
        s = next(x for x in M.NEW if x['key'] == key)
        cfg = dict(cfg, compare=COMPARE)
        if key == 'C2':
            doc = pymupdf.open(R.SRC['C'])
            f, n = R.subsolo_mask(doc[2], M.C2_SUB)
            assert n == 108, n
            cfg['occ']['extra'] = f
        if key == 'C3':
            cfg['occ']['extra'] = c3_note
        R.build(s, base, cfg, os.path.join(OUT, fn))
