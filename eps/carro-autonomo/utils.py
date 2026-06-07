"""
utils.py — persistência do modelo via pickle.
"""

import pickle
from pathlib import Path

DIR = Path("treinamento")
DIR.mkdir(exist_ok=True)


def salvar(nome, dados):
    path = DIR / f"{nome}.pkl"
    with open(path, "wb") as f:
        pickle.dump(dados, f)
    print(f"[pickle] Salvo em {path}")


def carregar(nome):
    path = DIR / f"{nome}.pkl"
    if not path.exists():
        return None
    print(f"[pickle] Carregando {path} ...")
    with open(path, "rb") as f:
        return pickle.load(f)
