"""
solucao.py — entry point do EP Carro Autônomo (Q-Learning Tabular).

Uso:
    python solucao.py                         # treina + avalia pistas 17 e 18
    python solucao.py --recarregar            # força re-treino ignorando pickle
    python solucao.py --avaliar pistas/X.txt  # avalia modelo salvo em pista X
"""

import sys
import random
import argparse
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from env import AmbienteCarro  # noqa: E402

from agente      import AgenteQLearning
from treinamento import treinar_round_robin
from avaliacao   import avaliar, escrever_saida
from utils       import salvar, carregar

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

PISTAS_TREINO  = [f"pistas/pista_{i:02d}.txt" for i in range(1, 17)]
PISTAS_HOLDOUT = [f"pistas/pista_{i:02d}.txt" for i in range(17, 19)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ep-por-pista", type=int,   default=30_000)
    parser.add_argument("--max-passos",   type=int,   default=500)
    parser.add_argument("--K",            type=int,   default=5)
    parser.add_argument("--alpha",        type=float, default=0.15)
    parser.add_argument("--gamma",        type=float, default=0.99)
    parser.add_argument("--recarregar",   action="store_true")
    parser.add_argument("--avaliar",      type=str,   default=None)
    args = parser.parse_args()

    # ── Treino ───────────────────────────────────────────────────────────────
    if args.avaliar:
        modelo = carregar("qlearning")
        if modelo is None:
            print("ERRO: pickle não encontrado. Rode sem --avaliar primeiro.")
            sys.exit(1)
    else:
        modelo = None if args.recarregar else carregar("qlearning")

        if modelo is None:
            agente = AgenteQLearning(K=args.K, alpha=args.alpha, gamma=args.gamma)

            print("=" * 60)
            print("TREINAMENTO Q-LEARNING — ROUND-ROBIN")
            print("=" * 60)
            print(f"  Pistas    : 16 (01-16)    Ep/pista : {args.ep_por_pista:,}")
            print(f"  Total ep. : {args.ep_por_pista * 16:,}         Max passos: {args.max_passos}")
            print(f"  K={args.K}  α={args.alpha}  γ={args.gamma}  ε: 1.0→0.05 (80% do treino)")
            print("=" * 60)

            historico, sucessos = treinar_round_robin(
                PISTAS_TREINO, agente, args.ep_por_pista, args.max_passos
            )

            n_total = args.ep_por_pista * len(PISTAS_TREINO)
            modelo  = {
                "q_table"            : dict(agente.Q),
                "discretization_K"   : args.K,
                "n_episodes_trained" : n_total,
                "estados_populados"  : agente.n_estados(),
                "config"             : {
                    "alpha": args.alpha, "gamma": args.gamma,
                    "max_passos": args.max_passos,
                },
                "seed"               : SEED,
                "tracks_used"        : PISTAS_TREINO,
                "rewards_history"    : historico,
            }
            salvar("qlearning", modelo)

    # ── Avaliação ─────────────────────────────────────────────────────────────
    agente_eval = AgenteQLearning.from_modelo(modelo)
    n_ep        = modelo["n_episodes_trained"]
    n_est       = modelo["estados_populados"]

    print(f"\n{'='*60}")
    print("AVALIAÇÃO — POLÍTICA GULOSA (ε = 0)")
    print(f"  Episódios de treino: {n_ep:,}  |  Estados: {n_est:,}")
    print("=" * 60)

    pistas_eval = [args.avaliar] if args.avaliar else PISTAS_HOLDOUT

    for pista in pistas_eval:
        print(f"\n  {pista} ...")
        env       = AmbienteCarro(pista, max_steps=args.max_passos, seed=SEED)
        resultado = avaliar(env, agente_eval)
        nome      = Path(pista).stem
        escrever_saida(f"q_learning_{nome}.txt", pista, resultado, n_ep, n_est)

    print("\nArquivos gerados:")
    for p in pistas_eval:
        print(f"  - q_learning_{Path(p).stem}.txt")


if __name__ == "__main__":
    main()
