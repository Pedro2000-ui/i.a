"""
agente.py — Q-Learning tabular com discretização binning uniforme (K=5).
"""

import random
import numpy as np
from collections import defaultdict


class AgenteQLearning:
    """
    Tabela Q indexada por estados discretizados via binning uniforme.

    obs_dim=6: [d_frente, d_±30°, d_±60°, v_norm], todos em [0,1].
    K=5: 5^6 = 15.625 estados teóricos; só aloca os visitados (defaultdict).
    K=5 casa com os 5 níveis de velocidade {0, 0.5, 1.0, 1.5, 2.0} → sem perda
    de informação nessa dimensão, e cobre 2 células por balde no LIDAR.
    """

    def __init__(self, obs_dim=6, n_actions=5, K=5,
                 alpha=0.15, gamma=0.99, eps=1.0, eps_final=0.05):
        self.K         = K
        self.n_actions = n_actions
        self.alpha     = alpha
        self.gamma     = gamma
        self.eps       = eps
        self.eps_final = eps_final
        self.Q         = defaultdict(lambda: np.zeros(n_actions))

    def discretizar(self, obs):
        """Float[6] → tuple[6] com índices em [0, K-1]."""
        return tuple(min(int(v * self.K), self.K - 1) for v in obs)

    def escolher_acao(self, obs):
        """ε-greedy: explora com prob. ε, explota com prob. 1-ε."""
        if random.random() < self.eps:
            return random.randrange(self.n_actions)
        return int(np.argmax(self.Q[self.discretizar(obs)]))

    def atualizar(self, obs, a, r, obs_prox, terminou):
        """
        Atualização TD off-policy (Q-Learning, Watkins 1989):
            Q(s,a) += α * [r + γ * max Q(s') - Q(s,a)]
        Se terminal, o alvo é apenas r (sem componente futuro).
        Off-policy: usa max sobre s', não a ação que foi tomada — permite
        explorar livremente sem contaminar o aprendizado da política ótima.
        """
        s = self.discretizar(obs)
        alvo = r if terminou else r + self.gamma * np.max(self.Q[self.discretizar(obs_prox)])
        self.Q[s][a] += self.alpha * (alvo - self.Q[s][a])

    def n_estados(self):
        return len(self.Q)

    @classmethod
    def from_modelo(cls, modelo):
        """Reconstrói o agente a partir do dict salvo no pickle."""
        cfg    = modelo.get("config", {})
        agente = cls(
            K=modelo["discretization_K"],
            alpha=cfg.get("alpha", 0.15),
            gamma=cfg.get("gamma", 0.99),
            eps=0.0,
            eps_final=0.0,
        )
        agente.Q = defaultdict(lambda: np.zeros(agente.n_actions), modelo["q_table"])
        return agente
