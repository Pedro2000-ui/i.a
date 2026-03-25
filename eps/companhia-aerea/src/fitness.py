"""
Função de aptidão e verificação de restrições para o problema de alocação
de aeronaves da Companhia Aérea Escola SENAC.
"""

from problema import (
    VOOS, INTERVALO_MINIMO, LIMITE_HORAS_VOO, FIM_DIA, INICIO_DIA
)

# Valor base alto para o fitness
V_BASE = 1_000_000

# Pesos das penalidades por violação de cada restrição
# Restrições de segurança e operacionais recebem peso mais alto
PESOS = {
    "R1": 5000,   # exclusividade de uso (sobreposição)
    "R2": 3000,   # intervalo mínimo entre voos
    "R3": 8000,   # compatibilidade tipo de aeronave
    "R4": 4000,   # continuidade de posicionamento
    "R5": 6000,   # janela operacional (chegada após 24h)
    "R6": 500,    # distribuição de horários (qualidade)
    "R7": 2000,   # limite de horas de voo por aeronave
    "R8": 3500,   # reposicionamento ao aeroporto base
}

# Peso para minimização de aeronaves
BETA = 1500


def avaliar(cromossomo):
    """
    Avalia um cromossomo e retorna (fitness, dict_violacoes).

    O cromossomo é uma lista de inteiros de tamanho TOTAL_VOOS,
    onde cromossomo[i] indica o índice da aeronave responsável pelo voo i.
    """
    n_aeronaves = max(cromossomo) + 1 if cromossomo else 0

    # Agrupa voos por aeronave e ordena por horário de partida
    agenda = {}  # aeronave_id -> lista de índices de voo ordenados por partida
    for voo_idx, aeronave_id in enumerate(cromossomo):
        agenda.setdefault(aeronave_id, []).append(voo_idx)

    for aeronave_id in agenda:
        agenda[aeronave_id].sort(key=lambda v: VOOS[v]["partida"])

    violacoes = {k: 0 for k in PESOS}

    for aeronave_id, lista_voos in agenda.items():
        tipo_aeronave = _tipo_aeronave(aeronave_id)
        horas_acumuladas = 0
        aeroporto_base = VOOS[lista_voos[0]]["origem"]

        for i, voo_idx in enumerate(lista_voos):
            voo = VOOS[voo_idx]

            # R3: compatibilidade de tipo
            if tipo_aeronave == "A" and voo["tipo_minimo"] == "B":
                violacoes["R3"] += 1

            # R5: janela operacional
            if voo["chegada"] > FIM_DIA:
                violacoes["R5"] += 1
            if voo["partida"] < INICIO_DIA:
                violacoes["R5"] += 1

            # R1 e R2: sobreposição e intervalo entre voos consecutivos
            if i > 0:
                voo_ant = VOOS[lista_voos[i - 1]]
                # sobreposição direta (R1)
                if voo["partida"] < voo_ant["chegada"]:
                    violacoes["R1"] += 1
                # intervalo mínimo insuficiente (R2)
                elif voo["partida"] < voo_ant["chegada"] + INTERVALO_MINIMO:
                    violacoes["R2"] += 1

                # R4: continuidade de posicionamento
                if voo["origem"] != voo_ant["destino"]:
                    violacoes["R4"] += 1

            horas_acumuladas += voo["duracao"]

        # R7: limite de horas de voo
        if horas_acumuladas > LIMITE_HORAS_VOO:
            violacoes["R7"] += 1

        # R8: reposicionamento ao aeroporto base
        ultimo_voo = VOOS[lista_voos[-1]]
        if ultimo_voo["destino"] != aeroporto_base:
            violacoes["R8"] += 1

    # R6: distribuição uniforme dos horários de partida por rota
    _verificar_r6(violacoes)

    penalidade = sum(PESOS[r] * violacoes[r] for r in violacoes)
    fitness = V_BASE - penalidade - BETA * n_aeronaves

    return fitness, violacoes


def _tipo_aeronave(aeronave_id):
    """
    Determina o tipo da aeronave com base no id.
    Aeronaves com id par são Tipo B, ímpares são Tipo A.
    A designação é fixa por id para manter consistência entre gerações.
    """
    return "B" if aeronave_id % 2 == 0 else "A"


def _verificar_r6(violacoes):
    """
    Verifica se os horários de partida de cada rota estão distribuídos
    uniformemente (tolerância de +-30 minutos entre partidas consecutivas).
    """
    from problema import ROTAS
    idx = 0
    for origem, destino, duracao, n_voos in ROTAS:
        intervalo_esperado = (18 * 60) / n_voos
        partidas = sorted(
            VOOS[v]["partida"]
            for v in range(idx, idx + n_voos)
        )
        for i in range(1, len(partidas)):
            intervalo_real = partidas[i] - partidas[i - 1]
            if abs(intervalo_real - intervalo_esperado) > 30:
                violacoes["R6"] += 1
        idx += n_voos


def total_violacoes(violacoes):
    return sum(violacoes.values())