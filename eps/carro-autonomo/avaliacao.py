"""
avaliacao.py — avaliação gulosa (ε=0) e geração dos arquivos de entrega.
"""

import numpy as np
from pathlib import Path


def avaliar(env, agente):
    """
    Roda um episódio com política gulosa (ε=0).
    ε=0 garante resultados determinísticos — mede o que o agente aprendeu,
    sem ruído de exploração.
    """
    agente.eps = 0.0
    obs        = env.reset()
    reward_total, velocidades, n_passos, sucesso = 0.0, [], 0, False

    for _ in range(env.max_steps):
        a                        = agente.escolher_acao(obs)
        obs, r, fim, trunc, info = env.step(a)
        reward_total += r
        velocidades.append(obs[5] * 2.0)   # desnormaliza: v_norm * V_MAX (2.0)
        n_passos += 1
        if fim or trunc:
            sucesso = bool(info.get("chegada", False))
            break

    return {
        "n_passos"         : n_passos,
        "recompensa_total" : reward_total,
        "sucesso"          : sucesso,
        "vel_media"        : float(np.mean(velocidades)) if velocidades else 0.0,
        "vel_maxima"       : float(np.max(velocidades))  if velocidades else 0.0,
    }


def escrever_saida(caminho, pista, resultado, n_ep_treino, n_estados):
    """Gera arquivo de resultado no formato exigido pelo README §4.3."""
    sucesso_str = "SIM" if resultado["sucesso"] else "NAO"
    linhas = [
        f"=== Pista: {Path(pista).name} ===",
        f"Algoritmo: Q-Learning (round-robin em pistas 01-16)",
        f"Episódios totais de treinamento: {n_ep_treino}",
        f"Estados populados: {n_estados}",
        f"Tempo de chegada (passos): {resultado['n_passos']}",
        f"Velocidade média: {resultado['vel_media']:.4f}",
        f"Velocidade máxima atingida: {resultado['vel_maxima']:.4f}",
        f"Recompensa total: {resultado['recompensa_total']:.2f}",
        f"Sucesso: {sucesso_str}",
        "",
    ]
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    print(f"  → {caminho}  |  Sucesso: {sucesso_str}  |  "
          f"Passos: {resultado['n_passos']}  |  Reward: {resultado['recompensa_total']:.1f}")
