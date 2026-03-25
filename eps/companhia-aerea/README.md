# Otimização de Alocação de Aeronaves — Companhia Aérea Escola SENAC

Trabalho prático de Algoritmos Genéticos. O sistema aloca automaticamente aeronaves
a 84 voos diários entre quatro aeroportos (GRU, GIG, BSB, CNF), minimizando a frota
total utilizada e respeitando todas as restrições operacionais e regulatórias.

---

## Estrutura do repositório

```
/
├── README.md
├── src/
│   ├── main.py          — ponto de entrada, argumentos de linha de comando
│   ├── ag.py            — algoritmo genetico principal
│   ├── problema.py      — definições das rotas, voos e constantes
│   ├── fitness.py       — função de aptidão e verificação de restrições
│   ├── operadores.py    — seleção, crossover, mutação e reparação
│   ├── inicializacao.py — geração da população inicial (gulosa + aleatória)
│   ├── saida.py         — formatação da saída em tabelas de texto
│   └── experimento.py   — experimento de hiperparâmetros
└── docs/
    ├── modelagem.md       — documentação técnica da modelagem
    └── hiperparametros.md — estudo experimental de hiperparâmetros
```
---

## Execução

### Execução padrão

```bash
cd eps/companhia-aerea/src
python main.py
```

### Com parâmetros configuráveis

```bash
cd eps/companhia-aerea/src
python main.py --populacao 150 --geracoes 600 --mutacao 0.03 --crossover 0.8 --semente 42
```

### Todos os parâmetros disponíveis

| Parâmetro | Descrição | Padrão |
|---|---|---|
| `--populacao` | Tamanho da população | 100 |
| `--geracoes` | Número máximo de geracões | 500 |
| `--mutacao` | Taxa de mutação por gene | 0.02 |
| `--crossover` | Taxa de crossover | 0.80 |
| `--elitismo` | Individuos elite preservados | 5 |
| `--torneio` | Tamanho do torneio de seleção | 3 |
| `--semente` | Semente aleatória (reproducibilidade) | None |

### Experimento de hiperparâmetros

```bash
python experimento.py
```

Gera automaticamente o arquivo `docs/hiperparametros.md` com tabela de resultados
e gráficos de convergência em formato Mermaid.

---

## Saída esperada

O programa exibe no terminal:

1. Parâmetros configurados
2. Evolução do fitness por geração (melhor, médio, pior, violações)
3. Escala diária de cada aeronave com todos os voos e horários
4. Resumo com total de aeronaves por tipo, voos cobertos e violações por restrição

Exemplo de saída parcial:

```
Aeronave B-01 (Tipo B) -- 9h00 de voo:
  06h00 -> GRU-BSB (chegada 08h00) | manutencao ate 09h30
  09h30 -> BSB-GIG (chegada 11h30) | manutencao ate 13h00
  ...

Resumo:
  Aeronaves Tipo A utilizadas : 12
  Aeronaves Tipo B utilizadas : 14
  Total de aeronaves          : 26
  Voos cobertos               : 84 / 84
  Total de violacoes          : 0
```

---

## Modelagem resumida

- **Cromossomo:** lista de 84 inteiros, onde cada posição representa um voo e o valor indica a aeronave alocada.
- **Seleção:** torneio de tamanho 3.
- **Crossover:** dois pontos com taxa padrao de 0,80.
- **Mutação:** reatribuição de voo a aeronave compatível com taxa padrão de 0,02 por gene.
- **Elitismo:** 5 melhores individuos preservados por geração.
- **Critério de parada:** limite de gerações ou convergência (sem melhora por 100 gerações).

Documentação técnica completa em [`docs/modelagem.md`](docs/modelagem.md).