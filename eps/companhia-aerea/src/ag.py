import random
import time

from problema import TOTAL_VOOS, VOOS
from fitness import avaliar, total_violacoes
from operadores import selecao_torneio, crossover_dois_pontos, mutacao, reparar
from inicializacao import inicializar_populacao


def executar_ag(
    tamanho_populacao=100,
    n_geracoes=500,
    taxa_crossover=0.8,
    taxa_mutacao=0.02,
    tamanho_elitismo=5,
    tamanho_torneio=3,
    semente=None,
):
    """
        Executa o Algoritmo Genético e retorna o melhor cromossomo encontrado,
        seu fitness e o histórico de evolução por geração.
    """
    if semente is not None:
        random.seed(semente)

    print(f"\nIniciando AG com {tamanho_populacao} indivíduos, {n_geracoes} gerações")
    print(f"Crossover={taxa_crossover:.2f}, Mutação={taxa_mutacao:.4f}, Elitismo={tamanho_elitismo}\n")
    print(f"{'Geracao':>8} | {'Melhor':>12} | {'Medio':>12} | {'Pior':>12} | {'Violacoes':>10}")
    print("-" * 65)

    populacao = inicializar_populacao(tamanho_populacao)

    historico = []  # (geração, melhor_fitness, médio, pior)
    melhor_global = None
    melhor_fitness_global = float("-inf")

    inicio = time.time()

    for geracao in range(n_geracoes):
        # Avaliação
        resultados = [avaliar(ind) for ind in populacao]
        fitnesses = [r[0] for r in resultados]
        violacoes_lista = [r[1] for r in resultados]

        melhor_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
        melhor_fitness = fitnesses[melhor_idx]
        medio = sum(fitnesses) / len(fitnesses)
        pior_fitness = min(fitnesses)

        historico.append((geracao, melhor_fitness, medio, pior_fitness))

        if melhor_fitness > melhor_fitness_global:
            melhor_fitness_global = melhor_fitness
            melhor_global = populacao[melhor_idx][:]
            melhor_violacoes = violacoes_lista[melhor_idx]

        # Exibe evolução a cada 50 gerações e na primeira e última
        if geracao % 50 == 0 or geracao == n_geracoes - 1:
            viol = total_violacoes(violacoes_lista[melhor_idx])
            print(
                f"{geracao:>8} | {melhor_fitness:>12,.0f} | {medio:>12,.0f} | "
                f"{pior_fitness:>12,.0f} | {viol:>10}"
            )

        # Critério de parada antecipada: sem melhora por 100 gerações
        if geracao > 100:
            fitness_100_geracoes_atras = historico[geracao - 100][1]
            if melhor_fitness_global <= fitness_100_geracoes_atras:
                print(f"\nConvergência detectada na geração {geracao}. Encerrando.")
                break

        # Elitismo: preserva os melhores indivíduos
        indices_ordenados = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)
        elite = [populacao[i][:] for i in indices_ordenados[:tamanho_elitismo]]

        # Geração da nova população
        nova_populacao = elite[:]

        while len(nova_populacao) < tamanho_populacao:
            pai1 = selecao_torneio(populacao, fitnesses, k=tamanho_torneio)
            pai2 = selecao_torneio(populacao, fitnesses, k=tamanho_torneio)

            filho1, filho2 = crossover_dois_pontos(pai1, pai2, taxa_crossover)

            filho1 = mutacao(filho1, taxa_mutacao)
            filho2 = mutacao(filho2, taxa_mutacao)

            filho1 = reparar(filho1)
            filho2 = reparar(filho2)

            nova_populacao.append(filho1)
            if len(nova_populacao) < tamanho_populacao:
                nova_populacao.append(filho2)

        populacao = nova_populacao

    tempo_total = time.time() - inicio
    print(f"\nTempo de execução: {tempo_total:.1f}s")

    return melhor_global, melhor_fitness_global, melhor_violacoes, historico