# 151 Estudo de Viabilidade — versões com studios

Av. Nossa Senhora dos Remédios, 2027 — Araucária/PR — ZR3 (LC 25/2020, LC 26/2020, LC 30/2023).

## Entregáveis (`entregaveis/`)

| Arquivo | Conteúdo |
|---|---|
| `151 ESTUDO A2 …` | A com tipo misto (6 studios + 4 aptos 2Q por torre); a T2 passa a ter 8 pav. tipo, como a T1 |
| `151 ESTUDO B2 …` | B com tipo misto, mesmo volume (CA 2,96) |
| `151 ESTUDO C2 …` | C com tipo misto e subsolo reduzido de 108 para 60 vagas |
| `151 ESTUDO C3 …` | Torres do C com 100% studios (252) e sem subsolo |
| `151 ESTUDO D2 …` | D com tipo misto, T2 com +1 pav. e edifício garagem com 1 pav. a menos |
| `151 COMPARATIVO …` | Tabela geral, gráficos, sensibilidade ao preço do studio, base legal e recomendação |
| `151 MODELO NUMERICO ….xlsx` | Premissas editáveis (preços e custos) e resultado por estudo |

## Regras que definem o estudo

- **Studio** (LC 26/2020, art. 258): 1 ambiente conjugado de até 30 m² úteis, sem divisórias, mais o banheiro. O módulo adotado troca 2 aptos 2Q por 3 studios de 27,13 m².
- **Vagas** (art. 259 e Anexo VII): 1 vaga a cada 3 studios; 1 vaga por apto 2Q; mais 5% para visitantes.
- **Lazer** (art. 178): 6 m² por unidade.
- **Distância entre torres** (art. 268, II): (H/6)×2. As alturas dos R00 já estão no limite.
- **EIV** (Lei 4.688/2025): Tipo 1 a partir de 130 unidades; Tipo 2 a partir de 200 vagas.

## Regerar

```
cd gerador
python3 build.py ../entregaveis      # pranchas A2, B2, C2, C3, D2 (a partir de originais-R00/)
python3 compare.py ../entregaveis    # caderno comparativo
python3 sheet.py ../entregaveis      # planilha
python3 model.py                     # tabela-resumo no terminal
```

As premissas de preço e custo ficam em `gerador/model.py` (dicionário `P`).
Requisitos: `pymupdf`, `matplotlib` e `shapely`, além de `openpyxl` para a planilha.
