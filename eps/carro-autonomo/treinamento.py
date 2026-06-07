"""
treinamento.py — loop round-robin nas pistas de treino.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from env import AmbienteCarro  # noqa: E402

from agente import AgenteQLearning

SEED = 42


def schedule_epsilon(ep, total, eps_ini=1.0, eps_fim=0.05, pct_decaimento=0.80):
    """
    Decaimento linear de ε nos primeiros `pct_decaimento` do treino.
    Linear é mais previsível que exponencial — evita cortar exploração cedo demais.
    """
    limite = int(total * pct_decaimento)
    if ep >= limite:
        return eps_fim
    return eps_ini + (ep / limite) * (eps_fim - eps_ini)


def treinar_round_robin(pistas, agente, ep_por_pista, max_passos, verbose=True):
    """
    A cada episódio, sorteia uma pista aleatoriamente e roda um episódio completo.

    Por que round-robin e não sequencial?
    Treino sequencial causa catastrophic forgetting: aprender pista_02 sobrescreve
    o que foi aprendido em pista_01. O sorteio uniforme intercala todas as pistas,
    mantendo a tabela Q coerente com o conjunto completo.
    O estado é local (LIDAR), então os Q-valores são compartilháveis entre pistas.

    Cache de ambientes: AmbienteCarro roda BFS na init — reutilizamos via reset().
    """
    n_total = ep_por_pista * len(pistas)
    envs    = {p: AmbienteCarro(p, max_steps=max_passos, seed=SEED) for p in pistas}

    print(f"Ambientes prontos. Iniciando {n_total:,} episódios.\n")

    historico, sucessos = [], []
    janela = []
    JANELA = 500

    for ep in range(n_total):
        agente.eps = schedule_epsilon(ep, n_total)

        env          = envs[random.choice(pistas)]
        obs          = env.reset()
        reward_total = 0.0
        sucesso      = False

        for _ in range(max_passos):
            a                        = agente.escolher_acao(obs)
            obs_prox, r, fim, trunc, info = env.step(a)
            agente.atualizar(obs, a, r, obs_prox, fim)
            obs           = obs_prox
            reward_total += r
            if fim or trunc:
                sucesso = bool(info.get("chegada", False))
                break

        historico.append(reward_total)
        sucessos.append(sucesso)
        janela.append(reward_total)
        if len(janela) > JANELA:
            janela.pop(0)

        if verbose and (ep + 1) % 5_000 == 0:
            media    = sum(janela) / len(janela)
            pct_suc  = 100 * sum(sucessos[-JANELA:]) / min(JANELA, ep + 1)
            print(f"  Ep {ep+1:>7,}/{n_total:,} | ε={agente.eps:.3f} | "
                  f"Reward={media:>8.1f} | Sucesso={pct_suc:5.1f}% | "
                  f"Estados={agente.n_estados():,}")

    print(f"\nTreinamento concluído. Estados populados: {agente.n_estados():,}")
    return historico, sucessos
