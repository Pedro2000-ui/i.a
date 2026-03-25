"""
Operadores genéticos para o AG de alocação de aeronaves.

Seleção: torneio
Crossover: dois pontos com reparação de restrições
Mutação: reatribuição de voo com verificação de compatibilidade
"""

import random
from problema import VOOS, INTERVALO_MINIMO, DURACAO_MAX_TIPO_A, FIM_DIA
from fitness import _tipo_aeronave, avaliar


# ---------------------------------------------------------------------------
# Seleção por torneio
# ---------------------------------------------------------------------------

def selecao_torneio(populacao, fitnesses, k=3):
    """
    Seleciona um indivíduo via torneio de tamanho k.
    Retorna uma cópia do cromossomo vencedor.
    """
    candidatos = random.sample(range(len(populacao)), k)
    vencedor = max(candidatos, key=lambda i: fitnesses[i])
    return populacao[vencedor][:]


# ---------------------------------------------------------------------------
# Crossover de dois pontos
# ---------------------------------------------------------------------------

def crossover_dois_pontos(pai1, pai2, taxa_crossover=0.8):
    """
    Crossover de dois pontos. Troca o segmento entre dois cortes aleatórios.
    Retorna dois filhos. Se o sorteio não ativar o crossover, retorna cópias dos pais.
    """
    if random.random() > taxa_crossover:
        return pai1[:], pai2[:]

    n = len(pai1)
    p1, p2 = sorted(random.sample(range(n), 2))

    filho1 = pai1[:p1] + pai2[p1:p2] + pai1[p2:]
    filho2 = pai2[:p1] + pai1[p1:p2] + pai2[p2:]

    return filho1, filho2


# ---------------------------------------------------------------------------
# Mutação: reatribuição de voo a aeronave compatível
# ---------------------------------------------------------------------------

def mutacao(cromossomo, taxa_mutacao=0.02, n_aeronaves_max=None):
    """
    Para cada gene com probabilidade taxa_mutacao, reatribui o voo
    a uma aeronave diferente. Respeita a compatibilidade de tipo (R3).

    Se n_aeronaves_max não for informado, usa o número atual de aeronaves + 2
    para permitir alguma expansão controlada.
    """
    cromossomo = cromossomo[:]
    n_atual = max(cromossomo) + 1
    if n_aeronaves_max is None:
        n_aeronaves_max = n_atual + 2

    for i in range(len(cromossomo)):
        if random.random() < taxa_mutacao:
            voo = VOOS[i]
            aeronave_atual = cromossomo[i]

            # gera candidatos de aeronaves compatíveis com o tipo do voo
            candidatos = [
                a for a in range(n_aeronaves_max)
                if a != aeronave_atual and _compativel(voo, a)
            ]
            if candidatos:
                cromossomo[i] = random.choice(candidatos)

    return cromossomo


def _compativel(voo, aeronave_id):
    """Verifica se a aeronave é compatível com o tipo mínimo exigido pelo voo."""
    tipo = _tipo_aeronave(int(aeronave_id))
    if voo["tipo_minimo"] == "B" and tipo == "A":
        return False
    return True


# ---------------------------------------------------------------------------
# Reparação pós-operador
# ---------------------------------------------------------------------------

def reparar(cromossomo):
    """
    Reparação pós-operador:
    1. Corrige violações de R3 (tipo incompatível com a rota).
    2. Tenta corrigir R8 (reposicionamento ao aeroporto base) adicionando
       um voo de retorno ou redistribuindo o último voo da aeronave.
    """
    cromossomo = cromossomo[:]
    n_aeronaves = max(cromossomo) + 1

    # --- R3: compatibilidade de tipo ---
    for i, aeronave_id in enumerate(cromossomo):
        voo = VOOS[i]
        if not _compativel(voo, aeronave_id):
            tipo_b_ids = [a for a in range(n_aeronaves) if _tipo_aeronave(a) == "B"]
            if tipo_b_ids:
                cromossomo[i] = random.choice(tipo_b_ids)
            else:
                novo_id = n_aeronaves if n_aeronaves % 2 == 0 else n_aeronaves + 1
                cromossomo[i] = novo_id
                n_aeronaves = max(cromossomo) + 1

    # --- R8: reposicionamento ao aeroporto base ---
    # Monta agenda por aeronave
    agenda = {}
    for voo_idx, aeronave_id in enumerate(cromossomo):
        agenda.setdefault(aeronave_id, []).append(voo_idx)
    for aid in agenda:
        agenda[aid].sort(key=lambda v: VOOS[v]["partida"])

    for aeronave_id, lista_voos in agenda.items():
        if not lista_voos:
            continue
        base = VOOS[lista_voos[0]]["origem"]
        ultimo_destino = VOOS[lista_voos[-1]]["destino"]

        if ultimo_destino != base:
            # Tenta encontrar um voo não alocado que parta do destino atual
            # e chegue ao aeroporto base, e que possa ser inserido no final
            # sem violar R2 e R5. Se não encontrar, apenas aceita a violação
            # (será penalizada pelo fitness e corrigida nas próximas gerações).
            ultimo = VOOS[lista_voos[-1]]
            minimo_partida = ultimo["chegada"] + INTERVALO_MINIMO
            tipo = _tipo_aeronave(aeronave_id)

            # Busca voo candidato com mesmo aeroporto de saída e destino == base
            candidatos = [
                v for v, aid in enumerate(cromossomo)
                if int(aid) != int(aeronave_id)
                and VOOS[v]["origem"] == ultimo_destino
                and VOOS[v]["destino"] == base
                and VOOS[v]["partida"] >= minimo_partida
                and VOOS[v]["chegada"] <= FIM_DIA
                and _compativel(VOOS[v], aeronave_id)
            ]
            if candidatos:
                # escolhe o mais cedo
                candidatos.sort(key=lambda v: VOOS[v]["partida"])
                cromossomo[candidatos[0]] = aeronave_id

    return cromossomo