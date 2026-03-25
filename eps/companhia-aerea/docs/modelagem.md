# Modelagem do Problema — Alocação de Aeronaves

## 1. Cromossomo

O cromossomo é uma lista de inteiros de tamanho fixo igual ao número total de voos diários (84).

Cada posição `i` do cromossomo representa o voo de índice `i` na lista global de voos, e o valor armazenado nessa posição é o identificador inteiro da aeronave responsável por operar aquele voo.

```
cromossomo = [aeronave_id_do_voo_0, aeronave_id_do_voo_1, ..., aeronave_id_do_voo_83]
```

**Domínio dos valores:** inteiros não negativos. O número de aeronaves distintas presentes no cromossomo determina a frota total utilizada, que o AG busca minimizar.

**Tipo de aeronave por id:** o tipo é derivado diretamente do identificador numérico da aeronave. Ids pares correspondem ao Tipo B (médio porte, todas as rotas); ids ímpares correspondem ao Tipo A (regional, rotas com duração máxima de 1h30). Essa codificação garante que a restrição R3 possa ser verificada e reparada de forma eficiente sem informação adicional no cromossomo.

**Tamanho do cromossomo:** 84 genes, um por voo.

---

## 2. Função de Aptidão

A função de aptidão segue a formulação do enunciado:

```
f = V - sum(p_i * n_i) - beta * N_aeronaves
```

Onde:
- `V = 1.000.000` — valor base alto, garantindo que soluções sem violações apresentem fitness positivo.
- `p_i` — peso da penalidade da restrição `i`.
- `n_i` — número de violações da restrição `i` na solução avaliada.
- `beta = 1500` — peso para pressionar a minimização da frota.
- `N_aeronaves` — número de aeronaves distintas no cromossomo.

### Pesos das restrições

| Restrição | Descrição | Peso (p_i) | Justificativa |
|---|---|---|---|
| R1 | Exclusividade de uso | 5000 | Segurança operacional crítica |
| R2 | Intervalo mínimo de manutenção | 3000 | Segurança — risco de falha mecânica |
| R3 | Compatibilidade de tipo | 8000 | O maior peso: aeronave inadequada é risco imediato |
| R4 | Continuidade de posicionamento | 4000 | Impossibilidade operacional |
| R5 | Janela operacional 06h-24h | 6000 | Restrição regulatória rígida |
| R6 | Distribuição de horários | 500 | Qualidade de serviço, não segurança |
| R7 | Limite de 12h de voo/dia | 2000 | Regulamentação de segurança |
| R8 | Reposicionamento ao aeroporto base | 3500 | Impacta operação do dia seguinte |

As restrições de segurança e operacionais (R1, R3, R4, R5) recebem penalidades mais altas do que as restrições de qualidade de serviço (R6, R8), conforme exigido pelo enunciado.

---

## 3. Operadores

### Seleção — Torneio

Utiliza-se seleção por torneio de tamanho `k=3` (configurável). A cada passo, três indivíduos são selecionados aleatoriamente da população e o de maior fitness é escolhido como pai. Esse operador mantém pressão seletiva moderada e não exige normalização do fitness, tornando-o robusto em cenários com valores negativos ou com grande variância.

### Crossover — Dois pontos

Dois pontos de corte são sorteados aleatoriamente na extensão do cromossomo. O segmento entre os dois pontos é trocado entre os pais, gerando dois filhos. A taxa de crossover padrão é de 0,80.

O crossover de dois pontos foi escolhido por permitir que blocos coesos de alocação (grupos de voos já bem encadeados) sejam preservados nos extremos do cromossomo, ao mesmo tempo em que introduz variação no segmento central.

**Tratamento de restrições:** o crossover em si não garante validade. Após a aplicação do operador, o operador de reparação corrige as violações de R3 e tenta reduzir as de R8.

### Mutação — Reatribuição compatível

Para cada gene do cromossomo, com probabilidade `taxa_mutacao` (padrão 0,02), o voo correspondente é reatribuído a uma aeronave diferente escolhida aleatoriamente entre as candidatas compatíveis com o tipo exigido pela rota (R3). O conjunto candidato inclui aeronaves já existentes no cromossomo e até duas novas (para permitir expansão controlada da frota quando necessário).

**Tratamento de restrições R2 e R4:** a mutação reatribui o voo e o operador de reparação, executado imediatamente após, verifica a continuidade de posicionamento e tenta corrigir o reposicionamento final (R8).

### Reparação pós-operador

Após crossover e mutação, cada filho passa por um operador de reparação com duas etapas:

1. **R3 — Compatibilidade de tipo:** voos em aeronaves incompatíveis são reatribuídos a aeronaves do Tipo B disponíveis.
2. **R8 — Reposicionamento ao aeroporto base:** para cada aeronave cujo último voo não retorna ao aeroporto base, busca-se um voo ainda alocado em outra aeronave que faça a rota de retorno necessária e que seja compatível com os intervalos de tempo. Se encontrado, esse voo é reatribuído à aeronave em questão.

---

## 4. Inicialização

A população inicial utiliza uma estratégia híbrida:

- **70% dos indivíduos** são construídos pelo método guloso encadeado por aeroporto (conforme sugerido no enunciado, seção 6.1): para cada aeronave, um voo inicial é escolhido aleatoriamente e os voos seguintes são encadeados garantindo que o aeroporto de origem do próximo voo seja o destino do atual. O encadeamento respeita R2 (intervalo mínimo), R3 (tipo), R5 (janela operacional) e R7 (limite de horas). Ao final da cadeia, o método tenta inserir um voo de retorno ao aeroporto base (R8).

- **30% dos indivíduos** são gerados aleatoriamente (respeitando apenas R3), para garantir diversidade genética e evitar convergência prematura.

Essa inicialização reduz drasticamente as violações de R4 nos indivíduos da primeira geração, acelerando a convergência.

---

## 5. Critério de Parada

O AG utiliza um critério combinado:

1. **Número máximo de gerações** (configurável via `--geracoes`, padrão 500).
2. **Convergência antecipada:** se o melhor fitness global não melhorar por 100 gerações consecutivas, o algoritmo encerra antes de atingir o limite. Isso evita processamento desnecessário após a estabilização da população.

O elitismo (padrão: 5 melhores indivíduos preservados por geração) garante que a melhor solução encontrada nunca seja perdida entre gerações.
