"""
Definições do problema de alocação de aeronaves.
Contém as constantes, rotas, voos e funções auxiliares de tempo.
"""

# Janela operacional: 06h00 até 24h00 (em minutos a partir de meia-noite)
INICIO_DIA = 6 * 60    # 360 minutos
FIM_DIA = 24 * 60      # 1440 minutos

# Tempos de manutenção em minutos
MANUTENCAO_POS_VOO = 30   # após desembarque
PREPARACAO_PRE_VOO = 60   # antes do embarque
INTERVALO_MINIMO = MANUTENCAO_POS_VOO + PREPARACAO_PRE_VOO  # 90 minutos

LIMITE_HORAS_VOO = 12 * 60  # 720 minutos por aeronave por dia

AEROPORTOS = ["GRU", "GIG", "BSB", "CNF"]

# Cada rota: (origem, destino, duração_em_minutos, voos_diários)
ROTAS = [
    ("GRU", "GIG", 60,  10),
    ("GRU", "BSB", 120,  6),
    ("GRU", "CNF", 90,   8),
    ("GIG", "GRU", 60,  10),
    ("GIG", "BSB", 120,  5),
    ("GIG", "CNF", 90,   6),
    ("BSB", "GRU", 120,  6),
    ("BSB", "GIG", 120,  5),
    ("BSB", "CNF", 90,   7),
    ("CNF", "GRU", 90,   8),
    ("CNF", "GIG", 90,   6),
    ("CNF", "BSB", 90,   7),
]

TOTAL_VOOS = sum(r[3] for r in ROTAS)  # 84

# Tipo A: apenas rotas com duração <= 90 min
# Tipo B: todas as rotas
DURACAO_MAX_TIPO_A = 90


def gerar_voos():
    """
    Gera a lista completa de voos do dia com horários de partida distribuídos
    uniformemente conforme R6 (intervalo aprox. 18h / n_voos, com tolerância +-30 min).
    Retorna lista de dicts com id, origem, destino, duração, partida, chegada, tipo_minimo.
    """
    voos = []
    vid = 0
    for origem, destino, duracao, n_voos in ROTAS:
        intervalo = (18 * 60) / n_voos  # minutos entre partidas
        for i in range(n_voos):
            partida = INICIO_DIA + int(i * intervalo)
            # garante que a chegada não ultrapasse 24h00 (R5)
            if partida + duracao > FIM_DIA:
                partida = FIM_DIA - duracao
            chegada = partida + duracao
            tipo_minimo = "A" if duracao <= DURACAO_MAX_TIPO_A else "B"
            voos.append({
                "id": vid,
                "origem": origem,
                "destino": destino,
                "duracao": duracao,
                "partida": partida,
                "chegada": chegada,
                "tipo_minimo": tipo_minimo,
            })
            vid += 1
    return voos


def minutos_para_hhmm(minutos):
    """Converte minutos desde meia-noite para string HH:MM."""
    h = minutos // 60
    m = minutos % 60
    return f"{h:02d}h{m:02d}"


VOOS = gerar_voos()