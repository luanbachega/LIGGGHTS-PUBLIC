# 153 Estudo de Viabilidade — R. Alexandre Wisocki, 249 (lote 08-A)

Fazenda Velha, Araucária/PR — matrícula 39.537 — inscrição 01.01.00.099.0257 — ZR3 — 1.524,00 m².

Este estudo usa as mesmas premissas de preço, custo e legislação do estudo 151.

## Opções (`entregaveis/`)

| Opção | Família | CA | Subsolos | Unidades |
|---|---|---|---|---|
| Estudo 1 | 2Q + 3Q | 2,5 | 1 | 48 |
| Estudo 2 | 2Q + 3Q | 3,0 | 1 | 56 |
| Estudo 3 | 2Q + 3Q | 3,0 | 2 | 56 (mostra que o 2º subsolo não compensa) |
| Estudo 4 | 2Q + studios | 2,5 | 1 | 70 |
| Estudo 5 | 2Q + studios | 3,0 | 1 | 96 |
| Estudo 6 | studios + 2Q | 3,0 | 1 | 112 |

Também estão em `entregaveis/`:

- `153 BASE LOTE 08-A ….dxf`: lote desenhado a partir da matrícula, com cotas, confrontantes, vias, recuos e norte.
- `153 IMPLANTACAO E#.dxf`: térreo, subsolo(s) e pavimentos tipo de cada opção, um ao lado do outro, com layers separadas.
- `153 COMPARATIVO - OPCOES.pdf`: tabela comparativa, sensibilidade, base legal, recomendação e ressalvas.
- `153 MODELO NUMERICO - OPCOES.xlsx`: premissas editáveis.

Os DXF estão em metros. A origem fica no canto da frente com a divisa do lote 10; o eixo X segue a testada e o eixo Y entra no lote.

## Ressalvas principais

- O lote não foi levantado em campo; foi desenhado pela matrícula, com as laterais perpendiculares à frente.
- A ordem dos segmentos dos fundos e a largura da R. Zdenko Gayer precisam ser confirmadas.
- O cadastro registra 498,22 m² construídos, mas a matrícula diz "sem benfeitorias".
- O CA máximo depende da regulamentação da Compensação Paisagística.

## Regerar

```
cd gerador
python3 render153.py ../entregaveis   # pranchas (usa o gerador do 151 como base)
python3 dxf153.py ../entregaveis
python3 compare153.py ../entregaveis
python3 sheet153.py ../entregaveis
python3 model153.py                   # resumo no terminal
```
