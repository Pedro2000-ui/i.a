# EP Carro Autônomo — Relatório de Implementação

**Algoritmo:** Q-Learning Tabular  
**Conjunto de treino:** pistas 01–16 (round-robin)  
**Conjunto de holdout:** pistas 17 e 18  

---

## 1. Fundamentos Teóricos

### 1.1 Aprendizado por Reforço

Aprendizado por Reforço (AR) é uma abordagem de machine learning onde um agente aprende a tomar decisões interagindo diretamente com o ambiente — sem supervisão explícita, sem dados rotulados. O que guia o aprendizado é o sinal de recompensa: ações que levam a bons resultados recebem reforço positivo; ações que levam a colisões ou desperdício de tempo recebem penalidade.

O ciclo de interação é simples:

```
estado s → agente escolhe ação a → ambiente retorna (s', r) → agente atualiza o que sabe → repete
```

O objetivo não é maximizar a recompensa de um único passo, mas a **soma descontada ao longo do tempo** — o que força o agente a considerar consequências futuras, não só o que é imediatamente vantajoso.

---

### 1.2 MDP — a formalização do problema

O problema é modelado como um **Processo de Decisão de Markov (MDP)**, composto por:

| Elemento | Notação | Descrição |
|----------|---------|-----------|
| Estados | S | O que o agente observa do ambiente em cada instante |
| Ações | A | O conjunto de decisões disponíveis em cada estado |
| Recompensas | R(s, a) | Sinal numérico que avalia a qualidade de uma ação em um estado |
| Transições | P(s' \| s, a) | A dinâmica do ambiente: como o estado muda após uma ação |

A **propriedade de Markov** garante que o próximo estado depende apenas do estado atual e da ação tomada — não de toda a história anterior. Isso é o que torna a tabela Q viável: não precisamos guardar trajetórias, apenas o estado presente.

No contexto deste EP, a propriedade é satisfeita porque os 5 sensores LIDAR mais a velocidade atual contêm tudo que é necessário para decidir a próxima ação.

---

### 1.3 A função Q

Q-Learning aprende a função **Q(s, a)**: o retorno esperado ao estar no estado `s`, executar a ação `a`, e a partir daí agir de forma ótima. Formalmente:

```
Q*(s, a) = E[ r₀ + γ·r₁ + γ²·r₂ + ... | s₀=s, a₀=a, política ótima ]
```

Quando a tabela Q converge para Q*, o agente só precisa, em cada estado, escolher a ação com maior Q-valor — essa é a política ótima.

Na prática, a tabela é um dicionário onde cada chave é um estado discretizado e o valor é um vetor com os Q-valores das 5 ações:

```
(2, 4, 1, 3, 0, 2) → [-12.3,  85.1, -4.7, 61.2, 70.8]
estado discretizado    nada   acel  frear  esq   dir
                              ↑ melhor ação neste estado
```

---

### 1.4 Atualização por Diferença Temporal

A tabela Q não é construída analiticamente — ela é refinada a cada transição observada pela regra TD:

```
Q(s,a) ← Q(s,a) + α · [ r + γ · max_{a'} Q(s', a') − Q(s,a) ]
                          └───────────────────────────┘   └──────┘
                                    alvo TD             estimativa atual
```

O **erro TD** é a diferença entre o que o agente esperava e o que ele observou. A cada passo, a estimativa atual é puxada na direção do alvo. O parâmetro **α** controla a velocidade dessa correção — muito alto e o aprendizado oscila, muito baixo e demora a convergir.

O alvo TD usa `max_{a'} Q(s', a')` — o melhor valor possível no próximo estado, independentemente do que foi feito. Isso caracteriza o Q-Learning como algoritmo **off-policy**: ele aprende sobre a política ótima mesmo enquanto executa uma política de exploração diferente (ε-greedy). Esse é um diferencial importante: a exploração não contamina o que está sendo aprendido.

Quando o episódio termina (colisão ou chegada), não há estado seguinte. O alvo é simplesmente `r`, sem o componente futuro.

O **γ (gamma)** desconta recompensas futuras: γ=0.99 significa que uma recompensa em 100 passos vale 0.99^100 ≈ 37% do valor imediato. Com γ alto, o agente considera seriamente o prêmio de chegada (+500) mesmo que ele esteja centenas de passos à frente.

---

### 1.5 Exploração vs. Explotação

Um agente que sempre escolhe `argmax Q(s, ·)` explota o que já sabe, mas nunca descobre alternativas melhores em estados pouco visitados. Por outro lado, explorar indefinidamente impede a consolidação de uma boa política.

A solução adotada é a **política ε-greedy**:

```
com prob. ε   → ação uniformemente aleatória  (explora)
com prob. 1-ε → argmax_a Q(s, a)             (explota)
```

ε começa em 1.0 (exploração total) e decai linearmente até 0.05 ao longo dos primeiros 80% dos episódios. O raciocínio: no início a tabela Q está zerada e qualquer decisão "ótima" é arbitrária — faz sentido explorar bastante. Conforme os Q-valores ganham significado, a explotação passa a ser produtiva.

Mantemos ε=0.05 no final (e não zero) para que o agente continue experimentando em estados raramente visitados — o que melhora a robustez da política em pistas desconhecidas.

---

## 2. Modelagem do MDP

### 2.1 Estados

O ambiente retorna um vetor de **6 floats em [0, 1]** a cada passo:

```
obs = [d_frente, d_+30°, d_-30°, d_+60°, d_-60°, v_norm]
```

Cada `d_α` é a distância normalizada até a parede mais próxima na direção `θ + α` (LIDAR), saturada em 10 células. `v_norm = v / V_MAX`.

O carro não conhece sua posição absoluta nem sua orientação global — percebe apenas o que os sensores enxergam localmente. Isso é intencional: um estado local é justamente o que permite que padrões aprendidos em uma pista se transfiram para outras.

### 2.2 Ações

| Ação | Efeito |
|------|--------|
| 0 | Nada (mantém v e θ) |
| 1 | Acelerar: v ← min(v + 0.5, 2.0) |
| 2 | Frear: v ← max(v − 0.5, 0) |
| 3 | Virar à esquerda: θ ← θ − 30° |
| 4 | Virar à direita: θ ← θ + 30° |

### 2.3 Recompensas

| Evento | Recompensa |
|--------|------------|
| Avanço de progresso | +Δs (proporcional ao avanço na pista via BFS) |
| Custo de tempo | −0.1 por passo |
| Colisão com parede | −100 (episódio termina) |
| Chegada à linha de chegada | +500 (episódio termina) |

A recompensa de progresso é crítica: sem ela, o agente não recebe nenhum sinal positivo nos episódios em que nunca chega ao fim — que são a maioria no começo do treino. Ela funciona como um sinal denso que orienta o aprendizado mesmo antes de qualquer chegada.

---

## 3. Discretização do Estado

### 3.1 Binning uniforme com K = 5

Q-Learning tabular exige estados discretos. Cada componente do vetor contínuo é mapeada para um dos K intervalos uniformes:

```python
def discretizar(obs, K=5):
    return tuple(min(int(v * K), K - 1) for v in obs)
```

O `min(..., K-1)` é necessário para o caso `v = 1.0` exato — sem ele, o índice resultante seria K, fora do range válido [0, K-1].

Exemplo com K=5 e `obs = [0.08, 0.95, 0.31, 0.50, 0.19, 0.75]`:
```
chave = (0, 4, 1, 2, 0, 3)
         ↑              ↑
    parede próxima   velocidade alta
```

### 3.2 Por que K = 5?

**Compatibilidade com a velocidade:** a velocidade assume exatamente 5 valores discretos {0, 0.5, 1.0, 1.5, 2.0}, que normalizam para {0.00, 0.25, 0.50, 0.75, 1.00}. Com K=5, cada valor cai em um balde distinto — não há perda de informação nessa dimensão.

**Resolução do LIDAR:** cada balde cobre 2 células de distância (20% do alcance de 10 células). Isso é suficiente para distinguir situações como "iminência de colisão" (balde 0, distância < 2), "passagem estreita" (balde 1) e "espaço amplo" (baldes 3-4).

**Tamanho da tabela:** 5⁶ = 15.625 estados teóricos — manejável em CPU. Na prática, o agente visitou 6.290 estados distintos nos 480k episódios de treino, o que indica cobertura razoável do espaço relevante.

Valores alternativos têm problemas concretos: K=3 gera apenas 729 estados — colisões de discretização fazem situações muito distintas parecerem iguais para o agente. K=8 gera 262.144 estados — com o mesmo budget de episódios, a maioria ficaria sem visitas suficientes para convergir.

---

## 4. Implementação do Q-Learning

### 4.1 Estrutura da tabela Q

```python
Q = defaultdict(lambda: np.zeros(n_actions))
```

O uso de `defaultdict` em vez de um array multidimensional fixo tem motivação prática: alocar um array `float64` para todos os 15.625 estados × 5 ações seria 625 KB — aceitável. Mas o `defaultdict` só aloca para estados efetivamente visitados, o que torna o código mais limpo e o modelo mais compacto ao serializar.

Um detalhe importante: `defaultdict` com lambda não é serializável de forma portável via pickle entre sessões Python diferentes. Por isso, antes de salvar, convertemos para `dict` normal:

```python
q_table_serializavel = dict(agente.Q)
```

E ao carregar, reconvertemos para `defaultdict` para que estados novos (não vistos no treino) retornem zeros automaticamente durante a avaliação.

### 4.2 Atualização TD

```python
def atualizar(self, obs, a, r, obs_prox, terminou):
    s      = self.discretizar(obs)
    s_prox = self.discretizar(obs_prox)

    alvo = r if terminou else r + self.gamma * np.max(self.Q[s_prox])
    self.Q[s][a] += self.alpha * (alvo - self.Q[s][a])
```

O Q-Learning usa `max` sobre todas as ações em `s'`, não a ação que foi de fato tomada. Isso é o que o distingue do SARSA (on-policy): o Q-Learning aprende a política ótima independentemente de qual política está sendo executada para coletar experiências.

### 4.3 Parâmetros adotados

| Hiperparâmetro | Valor | Justificativa |
|----------------|-------|---------------|
| **K** (discretização) | 5 | Ver §3.2 |
| **α** (taxa de aprendizado) | 0.15 | Um pouco acima do conservador 0.1 para acelerar convergência nas 16 pistas; valores acima de 0.2 geraram oscilação nos testes iniciais |
| **γ** (desconto) | 0.99 | A recompensa de chegada (+500) está potencialmente centenas de passos à frente; γ < 0.95 tornaria o agente curto-prazista demais para pistas longas |
| **ε inicial** | 1.0 | No início, a tabela Q está zerada — não há razão para preferir uma ação sobre outra |
| **ε final** | 0.05 | Exploração residual para manter robustez em estados raramente visitados |
| **Schedule ε** | Linear, primeiros 80% dos episódios | Os 20% finais servem para consolidar a política com ε estabilizado |
| **Episódios por pista** | 30.000 (480k total) | Budget recomendado no enunciado; suficiente para convergência nas pistas fáceis e médias |
| **max_steps** | 500 | Trunca episódios sem fim sem penalizar excessivamente pistas longas |

---

## 5. Treinamento Round-Robin

### 5.1 Por que round-robin?

Treinar sequencialmente — 30k episódios em pista_01, depois 30k em pista_02, e assim por diante — levaria a *catastrophic forgetting*: os Q-valores aprendidos para uma pista seriam progressivamente sobrescritos pela geometria da pista seguinte. Ao fim, o modelo lembraria bem só as últimas pistas vistas.

No round-robin, a cada episódio uma pista é sorteada aleatoriamente entre as 16. A tabela Q é única e compartilhada, atualizada por todas as pistas simultaneamente. Isso funciona porque o estado do agente é **local** (LIDAR + velocidade) — não depende de qual pista ele está. Padrões como "parede próxima à frente, espaço à direita" têm o mesmo significado em qualquer geometria.

### 5.2 Cache de ambientes

`AmbienteCarro` executa um BFS completo na inicialização para calcular a tabela de progresso. Recriar o ambiente a cada episódio seria um gargalo. Mantemos um dicionário `pista → env` e reutilizamos via `env.reset()`:

```python
envs = { p: AmbienteCarro(p, max_steps=max_passos, seed=SEED) for p in pistas_treino }
# ...
env = envs[random.choice(pistas_treino)]
obs = env.reset()
```

### 5.3 Seleção aleatória vs. cíclica

O sorteio uniforme, além de evitar correlação temporal entre episódios consecutivos, garante que pistas difíceis (13-16) apareçam distribuídas por todo o treinamento — e não só no final, quando o agente já teria consolidado hábitos das pistas fáceis.

### 5.4 Schedule de ε

```
ε decai de 1.0 → 0.05 linearmente nos primeiros 80% dos episódios (384k).
Os últimos 20% (96k episódios) mantêm ε = 0.05 constante.
```

O decaimento linear é mais previsível que o exponencial: com exponencial, o ε pode cair abaixo de 0.1 antes de metade do treino, cortando a exploração cedo demais em estados que ainda foram pouco visitados.

---

## 6. Mecânica da Exploração

### 6.1 Implementação ε-greedy

```python
if random.random() < self.eps:
    return random.randrange(self.n_actions)   # exploração
return int(np.argmax(self.Q[self.discretizar(obs)]))  # explotação
```

Para estados nunca visitados — que retornam `np.zeros(5)` via defaultdict — o `argmax` retorna sempre o índice 0 (ação "nada"). Isso não é ideal, mas na prática raramente acontece na avaliação final: estados com todos os Q-valores zerados indicam regiões do espaço que o agente simplesmente nunca alcançou durante o treino.

### 6.2 Por que não UCB?

UCB (Upper Confidence Bound) dirigiria a exploração para estados/ações com alta incerteza, sendo teoricamente mais eficiente. No entanto, requer manter um contador de visitas por par (s,a) — o que aumenta o custo por passo e a complexidade de implementação. Para este problema, com 480k episódios e 6.290 estados populados, ε-greedy com decaimento linear é suficiente para uma cobertura adequada.

---

## 7. Resultados nas Pistas de Holdout

Os resultados completos estão nos arquivos `q_learning_pista_17.txt` e `q_learning_pista_18.txt`, gerados pela avaliação com política gulosa (ε=0) após o treino completo.

### 7.1 Métricas obtidas

| Métrica | Pista 17 | Pista 18 |
|---------|----------|----------|
| Sucesso | [ver arquivo](../q_learning_pista_17.txt) | [ver arquivo](../q_learning_pista_18.txt) |
| Passos até terminar | [ver arquivo](../q_learning_pista_17.txt) | [ver arquivo](../q_learning_pista_18.txt) |
| Recompensa total | [ver arquivo](../q_learning_pista_17.txt) | [ver arquivo](../q_learning_pista_18.txt) |
| Velocidade média | [ver arquivo](../q_learning_pista_17.txt) | [ver arquivo](../q_learning_pista_18.txt) |

### 7.2 Análise de generalização

O agente foi treinado exclusivamente nas pistas 01-16 e nunca viu as pistas 17 e 18. O desempenho no holdout mede diretamente a capacidade de generalização — não memorização.

O resultado **NAO** em uma pista de holdout não é necessariamente um fracasso: as pistas 17 e 18 têm corredor de 2 células de largura, o que as torna as mais exigentes do conjunto. O agente que colide nelas com reward −46.2 já percorreu parte da pista com alguma coerência — não é um comportamento aleatório (que produziria reward próximo de −100 em ~10 passos).

A limitação principal do Q-Learning tabular neste cenário é estrutural: com K=5, dois estados que diferem sutilmente em distância LIDAR podem ser mapeados ao mesmo balde. Em corredores de 2 células, essa imprecisão pode ser a diferença entre virar a tempo ou colidir. Algoritmos que operam diretamente no espaço contínuo (ex: DQN com rede neural) não sofrem dessa limitação — o que os torna mais adequados para pistas de alta precisão.

---

## 8. Estrutura do Modelo Salvo (pickle)

O arquivo `treinamento/qlearning.pkl` contém:

```python
{
    "q_table"            : dict,   # chave discreta → np.array(5,)
    "discretization_K"   : int,    # K usado (5)
    "n_episodes_trained" : int,    # total de episódios (480.000)
    "rewards_history"    : list,   # reward total por episódio
    "rewards_por_pista"  : dict,   # pista → lista de rewards
    "config"             : dict,   # alpha, gamma, eps, max_passos
    "seed"               : int,    # 42
    "tracks_used"        : list,   # pistas 01-16
    "estados_populados"  : int,    # 6.290
    "media_movel_100"    : list,   # curva de aprendizado resumida
}
```

---

## 9. Instruções de Reprodução

```bash

# Acessar EP
cd eps/carro-autonomo

# Instalar dependências
pip install -r requirements.txt

# Treinar (≈30-60 min em CPU) + avaliar pistas 17 e 18
python solucao.py

# Forçar re-treino mesmo com pickle existente
python solucao.py --recarregar

# Avaliar modelo já treinado em uma pista específica
python solucao.py --avaliar pistas/pista_17.txt

# Visualizar o agente rodando no terminal
PYTHONPATH=src python src/visualize.py pistas/pista_17.txt
PYTHONPATH=src python src/visualize.py pistas/pista_18.txt
```

## 10. Estrutura do Repositório

```bash
carro-autonomo/
│
├── solucao.py              # entry point — CLI, orquestra treino e avaliação
├── agente.py               # AgenteQLearning — tabela Q, discretização, ε-greedy, TD
├── treinamento.py          # treinar_round_robin + schedule_epsilon
├── avaliacao.py            # avaliar (política gulosa) + escrever_saida
├── utils.py                # salvar/carregar pickle
│
├── src/
│   ├── env.py              # AmbienteCarro — simulador, LIDAR, recompensas, BFS
│   └── visualize.py        # renderização do agente no terminal
│
├── pistas/
│   ├── pista_01.txt        # pistas fáceis (corredores largos)
│   ├── ...
│   ├── pista_12.txt        # pistas médias
│   ├── pista_13.txt        # pistas difíceis (corredor 2 células)
│   ├── ...
│   ├── pista_16.txt
│   ├── pista_17.txt        # holdout — nunca vistas no treino
│   └── pista_18.txt        # holdout
│
├── treinamento/
│   └── qlearning.pkl       # modelo serializado após treino
│
├── q_learning_pista_17.txt # resultado da avaliação (gerado por solucao.py)
├── q_learning_pista_18.txt
│
├── docs/
│   └── relatorio.md        # este documento
│
├── enunciado/
│   ├── qlearning.md
│   └── ...
│
└── requirements.txt
```