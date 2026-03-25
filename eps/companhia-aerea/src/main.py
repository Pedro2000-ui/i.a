"""
Ponto de entrada do sistema de alocação de aeronaves via Algoritmo Genético.
Companhia Aérea Escola SENAC.

Uso:
    python main.py [opções]

Exemplos:
    python main.py
    python main.py --populacao 150 --geracoes 300 --mutacao 0.03
    python main.py --populacao 200 --geracoes 500 --crossover 0.85 --semente 42
"""

import argparse
import sys
import os

# Garante que o diretório src está no path quando executado de fora dele
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ag import executar_ag
from saida import exibir_resultado, exibir_historico_resumido
from problema import TOTAL_VOOS


def parse_args():
    parser = argparse.ArgumentParser(
        description="AG para alocação de aeronaves - Companhia Aérea Escola SENAC"
    )
    parser.add_argument(
        "--populacao", type=int, default=100,
        help="Tamanho da população (default: 100)"
    )
    parser.add_argument(
        "--geracoes", type=int, default=500,
        help="Número máximo de gerações (default: 500)"
    )
    parser.add_argument(
        "--mutacao", type=float, default=0.02,
        help="Taxa de mutação por gene (default: 0.02)"
    )
    parser.add_argument(
        "--crossover", type=float, default=0.8,
        help="Taxa de crossover (default: 0.8)"
    )
    parser.add_argument(
        "--elitismo", type=int, default=5,
        help="Número de indivíduos elite preservados (default: 5)"
    )
    parser.add_argument(
        "--torneio", type=int, default=3,
        help="Tamanho do torneio de seleção (default: 3)"
    )
    parser.add_argument(
        "--semente", type=int, default=None,
        help="Semente aleatória para reprodutibilidade (default: None)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 72)
    print("COMPANHIA AÉREA ESCOLA SENAC")
    print("Otimização de Alocação de Aeronaves por Algoritmo Genético")
    print("=" * 72)
    print(f"\nTotal de voos a cobrir: {TOTAL_VOOS}")
    print(f"Parâmetros:")
    print(f"  População  : {args.populacao}")
    print(f"  Gerações   : {args.geracoes}")
    print(f"  Crossover  : {args.crossover}")
    print(f"  Mutação    : {args.mutacao}")
    print(f"  Elitismo   : {args.elitismo}")
    print(f"  Torneio    : {args.torneio}")
    print(f"  Semente    : {args.semente}")

    melhor, fitness, violacoes, historico = executar_ag(
        tamanho_populacao=args.populacao,
        n_geracoes=args.geracoes,
        taxa_crossover=args.crossover,
        taxa_mutacao=args.mutacao,
        tamanho_elitismo=args.elitismo,
        tamanho_torneio=args.torneio,
        semente=args.semente,
    )

    exibir_historico_resumido(historico)
    exibir_resultado(melhor, fitness, violacoes)


if __name__ == "__main__":
    main()