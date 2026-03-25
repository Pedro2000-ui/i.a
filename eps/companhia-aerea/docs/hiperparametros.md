# Estudo de Hiperparâmetros

Experimento variando o **tamanho da população** e a **taxa de mutação**.
Número de gerações fixado em 300. Semente aleatória: 42.

## Tabela de Resultados

| Populacao | Mutacao | Melhor Fitness | Geracao de Convergencia | Violacoes | Tempo (s) |
|---|---|---|---|---|---|
| 50 | 0.01 | 933,000 | 224 | 5 | 6.3 |
| 50 | 0.03 | 940,500 | 139 | 3 | 4.6 |
| 100 | 0.01 | 937,000 | 81 | 3 | 4.7 |
| 100 | 0.03 | 934,500 | 69 | 2 | 6.3 |
| 150 | 0.01 | 931,500 | 76 | 4 | 8.2 |
| 150 | 0.03 | 937,500 | 226 | 3 | 17.2 |

## Análise

A melhor combinação encontrada foi **populacao=50, mutacao=0.03**, com fitness de **940,500** e 3 violacao(oes).

Populações maiores tendem a explorar melhor o espaço de busca, mas aumentam o custo computacional por geração. Taxas de mutação mais altas introduzem mais diversidade, o que ajuda a escapar de ótimos locais, porém pode desestabilizar indivíduos já bons se excessivamente alta.

## Gráficos de Convergência

### pop=50, mut=0.01

```mermaid
xychart-beta
    title "Evolucao do Fitness — pop=50, mut=0.01"
    x-axis "Geracao" [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 299]
    y-axis "Fitness" 860000 --> 950000
    line [876500, 925000, 928500, 929000, 929000, 929500, 929500, 929500, 933000, 933000, 933000]
```

### pop=50, mut=0.03

```mermaid
xychart-beta
    title "Evolucao do Fitness — pop=50, mut=0.03"
    x-axis "Geracao" [0, 24, 48, 72, 96, 120, 144, 168, 192, 216, 239]
    y-axis "Fitness" 860000 --> 960000
    line [876500, 912000, 923000, 937000, 937000, 940000, 940500, 940500, 940500, 940500, 940500]
```

### pop=100, mut=0.01

```mermaid
xychart-beta
    title "Evolucao do Fitness — pop=100, mut=0.01"
    x-axis "Geracao" [0, 18, 36, 54, 72, 90, 108, 126, 144, 162, 180, 181]
    y-axis "Fitness" 860000 --> 950000
    line [876500, 915500, 930000, 934500, 935500, 937000, 937000, 937000, 937000, 937000, 937000, 937000]
```

### pop=100, mut=0.03

```mermaid
xychart-beta
    title "Evolucao do Fitness — pop=100, mut=0.03"
    x-axis "Geracao" [0, 17, 34, 51, 68, 85, 102, 119, 136, 153, 169]
    y-axis "Fitness" 860000 --> 950000
    line [876500, 914000, 921000, 927500, 930500, 934500, 934500, 934500, 934500, 934500, 934500]
```

### pop=150, mut=0.01

```mermaid
xychart-beta
    title "Evolucao do Fitness — pop=150, mut=0.01"
    x-axis "Geracao" [0, 17, 34, 51, 68, 85, 102, 119, 136, 153, 170, 176]
    y-axis "Fitness" 860000 --> 950000
    line [876500, 924000, 928000, 928000, 928000, 931500, 931500, 931500, 931500, 931500, 931500, 931500]
```

### pop=150, mut=0.03

```mermaid
xychart-beta
    title "Evolucao do Fitness — pop=150, mut=0.03"
    x-axis "Geracao" [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 299]
    y-axis "Fitness" 860000 --> 950000
    line [876500, 924500, 928500, 928500, 932500, 936000, 936000, 936500, 937500, 937500, 937500]
```
