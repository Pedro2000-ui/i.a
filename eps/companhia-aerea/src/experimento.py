"""
Experimento de hiperparâmetros para o AG de alocação de aeronaves.
Varia tamanho da população e taxa de mutação, registrando resultados
e gerando gráficos de convergência no formato Mermaid XY Chart.

Uso:
    python experimento.py
    python experimento.py --saida ../docs/hiperparametros.md
"""

import argparse
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ag import executar_ag
from fitness import total_violacoes

# Combinações de hiperparâmetros a testar
POPULACOES = [50, 100, 150]
MUTACOES = [0.01, 0.03]
N_GERACOES = 300
SEMENTE = 42  # fixada para reprodutibilidade


def executar_experimento():
    resultados = []

    print("Iniciando experimento de hiperparâmetros...")
    print(f"Populações testadas : {POPULACOES}")
    print(f"Taxas de mutação    : {MUTACOES}")
    print(f"Gerações            : {N_GERACOES}")
    print(f"Semente             : {SEMENTE}")
    print()

    total_combinacoes = len(POPULACOES) * len(MUTACOES)
    idx = 0

    for pop in POPULACOES:
        for mut in MUTACOES:
            idx += 1
            print(f"[{idx}/{total_combinacoes}] pop={pop}, mut={mut:.2f} ...", flush=True)

            inicio = time.time()
            melhor, fitness, violacoes, historico = executar_ag(
                tamanho_populacao=pop,
                n_geracoes=N_GERACOES,
                taxa_crossover=0.8,
                taxa_mutacao=mut,
                tamanho_elitismo=5,
                tamanho_torneio=3,
                semente=SEMENTE,
            )
            tempo = time.time() - inicio

            geracao_convergencia = len(historico) - 1
            # detecta geração de convergência real (última melhora)
            melhor_ate_agora = historico[0][1]
            ultima_melhora = 0
            for g, (ger, f_mel, _, _) in enumerate(historico):
                if f_mel > melhor_ate_agora:
                    melhor_ate_agora = f_mel
                    ultima_melhora = ger

            resultados.append({
                "pop": pop,
                "mut": mut,
                "fitness": fitness,
                "violacoes": total_violacoes(violacoes),
                "geracao_convergencia": ultima_melhora,
                "geracoes_executadas": len(historico),
                "tempo": tempo,
                "historico": historico,
            })
            print(f"   Fitness={fitness:,.0f} | Violacoes={total_violacoes(violacoes)} | Convergencia={ultima_melhora}g | Tempo={tempo:.1f}s\n")

    return resultados


def gerar_markdown(resultados):
    linhas = []
    linhas.append("# Estudo de Hiperparâmetros")
    linhas.append("")
    linhas.append("Experimento variando o **tamanho da população** e a **taxa de mutação**.")
    linhas.append(f"Número de gerações fixado em {N_GERACOES}. Semente aleatória: {SEMENTE}.")
    linhas.append("")

    # Tabela resumo
    linhas.append("## Tabela de Resultados")
    linhas.append("")
    linhas.append("| Populacao | Mutacao | Melhor Fitness | Geracao de Convergencia | Violacoes | Tempo (s) |")
    linhas.append("|---|---|---|---|---|---|")
    for r in resultados:
        linhas.append(
            f"| {r['pop']} | {r['mut']:.2f} | {r['fitness']:,.0f} | "
            f"{r['geracao_convergencia']} | {r['violacoes']} | {r['tempo']:.1f} |"
        )
    linhas.append("")

    # Análise
    melhor = max(resultados, key=lambda r: r["fitness"])
    linhas.append("## Análise")
    linhas.append("")
    linhas.append(
        f"A melhor combinação encontrada foi **populacao={melhor['pop']}, "
        f"mutacao={melhor['mut']:.2f}**, com fitness de **{melhor['fitness']:,.0f}** "
        f"e {melhor['violacoes']} violacao(oes)."
    )
    linhas.append("")
    linhas.append(
        "Populações maiores tendem a explorar melhor o espaço de busca, mas aumentam o custo "
        "computacional por geração. Taxas de mutação mais altas introduzem mais diversidade, "
        "o que ajuda a escapar de ótimos locais, porém pode desestabilizar indivíduos já bons "
        "se excessivamente alta."
    )
    linhas.append("")

    # Gráficos Mermaid por combinação
    linhas.append("## Gráficos de Convergência")
    linhas.append("")

    for r in resultados:
        pop = r["pop"]
        mut = r["mut"]
        historico = r["historico"]

        # Amostra de até 10 pontos do histórico para o gráfico
        n = len(historico)
        passo = max(1, n // 10)
        amostras = [historico[i] for i in range(0, n, passo)]
        if historico[-1] not in amostras:
            amostras.append(historico[-1])

        eixo_x = [str(a[0]) for a in amostras]
        eixo_y = [str(int(a[1])) for a in amostras]

        fitness_min = min(int(a[1]) for a in amostras)
        fitness_max = max(int(a[1]) for a in amostras)
        
        y_min = max(0, (fitness_min // 10000) * 10000 - 10000)
        y_max = (fitness_max // 10000) * 10000 + 20000

        linhas.append(f"### pop={pop}, mut={mut:.2f}")
        linhas.append("")
        linhas.append("```mermaid")
        linhas.append("xychart-beta")
        linhas.append(f'    title "Evolucao do Fitness — pop={pop}, mut={mut:.2f}"')
        linhas.append(f'    x-axis "Geracao" [{", ".join(eixo_x)}]')
        linhas.append(f'    y-axis "Fitness" {y_min} --> {y_max}')
        linhas.append(f'    line [{", ".join(eixo_y)}]')
        linhas.append("```")
        linhas.append("")

    return "\n".join(linhas)


def main():
    parser = argparse.ArgumentParser(
        description="Experimento de hiperparâmetros do AG de alocação de aeronaves"
    )
    parser.add_argument(
        "--saida", type=str, default="../docs/hiperparametros.md",
        help="Caminho do arquivo Markdown de saída (default: ../docs/hiperparametros.md)"
    )
    args = parser.parse_args()

    resultados = executar_experimento()
    markdown = gerar_markdown(resultados)

    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.saida)
    caminho = os.path.normpath(caminho)

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"\nDocumento de hiperparâmetros gerado em: {caminho}")

    # Exibe tabela resumo no terminal
    print("\n" + "=" * 72)
    print("RESUMO DO EXPERIMENTO")
    print("=" * 72)
    print(f"  {'Pop':>6} | {'Mutacao':>8} | {'Fitness':>14} | {'Conv.(g)':>9} | {'Viol.':>6} | {'Tempo':>7}")
    print("  " + "-" * 68)
    for r in resultados:
        print(
            f"  {r['pop']:>6} | {r['mut']:>8.2f} | {r['fitness']:>14,.0f} | "
            f"{r['geracao_convergencia']:>9} | {r['violacoes']:>6} | {r['tempo']:>6.1f}s"
        )
    print("=" * 72)


if __name__ == "__main__":
    main()