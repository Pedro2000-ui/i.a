"""
Inicialização da população para o AG de alocação de aeronaves.

Estratégia: construção gulosa encadeada por aeroporto (conforme dica 6.1
do enunciado), garantindo continuidade de posicionamento (R4) e
compatibilidade de tipo (R3) desde o início.
"""

import random
from problema import VOOS, INTERVALO_MINIMO, DURACAO_MAX_TIPO_A, FIM_DIA
from fitness import _tipo_aeronave


def inicializar_populacao(tamanho_populacao):
    """
    Gera a população inicial. Cada indivíduo é construído pelo método
    de encadeamento guloso. Uma fração da população é gerada com
    perturbação aleatória para diversidade.
    """
    populacao = []
    for i in range(tamanho_populacao):
        if i < tamanho_populacao * 0.7:
            individuo = _construir_guloso()
        else:
            individuo = _construir_aleatorio()
        populacao.append(individuo)
    return populacao


def _construir_guloso():
    """
    Constrói um indivíduo encadeando voos por aeroporto.

    Para cada aeronave, parte de um voo inicial e encadeia voos subsequentes
    cujo aeroporto de origem coincide com o destino do voo anterior,
    respeitando o intervalo mínimo (R2) e o tipo da aeronave (R3).
    Ao final, tenta fechar o ciclo voltando ao aeroporto base (R8).
    """
    n_voos = len(VOOS)
    cromossomo = [-1] * n_voos
    voos_nao_alocados = set(range(n_voos))

    aeronave_id = 0

    while voos_nao_alocados:
        tipo = _tipo_aeronave(aeronave_id)
        candidatos_iniciais = [
            v for v in voos_nao_alocados
            if _eh_compativel_tipo(VOOS[v], tipo)
        ]
        if not candidatos_iniciais:
            aeronave_id += 1
            continue

        voo_atual_idx = random.choice(candidatos_iniciais)
        cromossomo[voo_atual_idx] = aeronave_id
        voos_nao_alocados.discard(voo_atual_idx)

        aeroporto_base = VOOS[voo_atual_idx]["origem"]
        horas_acumuladas = VOOS[voo_atual_idx]["duracao"]
        cadeia = [voo_atual_idx]

        # Encadeia voos seguintes
        while True:
            voo_atual = VOOS[voo_atual_idx]
            proximos = _candidatos_encadeamento(
                voo_atual, voos_nao_alocados, tipo, horas_acumuladas
            )
            if not proximos:
                break
            proximo_idx = proximos[0]
            cromossomo[proximo_idx] = aeronave_id
            voos_nao_alocados.discard(proximo_idx)
            horas_acumuladas += VOOS[proximo_idx]["duracao"]
            voo_atual_idx = proximo_idx
            cadeia.append(voo_atual_idx)

        # Tenta fechar o ciclo: busca voo que sai do destino atual e chega na base
        ultimo = VOOS[cadeia[-1]]
        if ultimo["destino"] != aeroporto_base:
            candidatos_retorno = [
                v for v in voos_nao_alocados
                if VOOS[v]["origem"] == ultimo["destino"]
                and VOOS[v]["destino"] == aeroporto_base
                and VOOS[v]["partida"] >= ultimo["chegada"] + INTERVALO_MINIMO
                and VOOS[v]["chegada"] <= FIM_DIA
                and _eh_compativel_tipo(VOOS[v], tipo)
                and horas_acumuladas + VOOS[v]["duracao"] <= 12 * 60
            ]
            if candidatos_retorno:
                candidatos_retorno.sort(key=lambda v: VOOS[v]["partida"])
                retorno_idx = candidatos_retorno[0]
                cromossomo[retorno_idx] = aeronave_id
                voos_nao_alocados.discard(retorno_idx)

        aeronave_id += 1

    return cromossomo


def _candidatos_encadeamento(voo_atual, voos_nao_alocados, tipo, horas_acumuladas):
    """
    Retorna lista de índices de voos que podem ser encadeados após voo_atual,
    ordenados por horário de partida.
    """
    chegada_com_manutencao = voo_atual["chegada"] + INTERVALO_MINIMO
    candidatos = []
    for v in voos_nao_alocados:
        voo = VOOS[v]
        # R4: origem deve ser o destino do voo anterior
        if voo["origem"] != voo_atual["destino"]:
            continue
        # R2: intervalo mínimo
        if voo["partida"] < chegada_com_manutencao:
            continue
        # R3: compatibilidade de tipo
        if not _eh_compativel_tipo(voo, tipo):
            continue
        # R5: chegada dentro da janela
        if voo["chegada"] > FIM_DIA:
            continue
        # R7: limite de horas
        if horas_acumuladas + voo["duracao"] > 12 * 60:
            continue
        candidatos.append(v)
    candidatos.sort(key=lambda v: VOOS[v]["partida"])
    return candidatos


def _eh_compativel_tipo(voo, tipo):
    """Verifica compatibilidade do voo com o tipo de aeronave."""
    if voo["tipo_minimo"] == "B" and tipo == "A":
        return False
    return True


def _construir_aleatorio():
    """
    Constrói um indivíduo com alocação aleatória (mantendo apenas R3).
    Usado para diversidade na população inicial.
    """
    n_voos = len(VOOS)
    # usa entre 10 e 30 aeronaves para manter pressão de minimização
    n_aeronaves = random.randint(10, 30)
    cromossomo = []
    for i in range(n_voos):
        voo = VOOS[i]
        if voo["tipo_minimo"] == "B":
            # apenas aeronaves tipo B (ids pares)
            candidatos = [a for a in range(n_aeronaves) if a % 2 == 0]
        else:
            candidatos = list(range(n_aeronaves))
        if not candidatos:
            candidatos = [0]
        cromossomo.append(random.choice(candidatos))
    return cromossomo