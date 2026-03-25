"""
Formatação e exibição dos resultados do AG.
Toda saída é apresentada em tabelas de texto, conforme exigido pelo enunciado.
"""

from problema import VOOS, INTERVALO_MINIMO
from fitness import _tipo_aeronave, PESOS
from problema import minutos_para_hhmm


def exibir_resultado(cromossomo, fitness, violacoes):
    """Exibe a escala completa de aeronaves e o resumo da solução."""
    agenda = _montar_agenda(cromossomo)

    print("\n" + "=" * 72)
    print("ESCALA DIÁRIA DE AERONAVES")
    print("=" * 72)

    total_tipo_a = 0
    total_tipo_b = 0
    total_horas_voo = 0

    for aeronave_id in sorted(agenda.keys()):
        lista_voos = agenda[aeronave_id]
        tipo = _tipo_aeronave(aeronave_id)
        letra = f"{'A' if tipo == 'A' else 'B'}"
        num = aeronave_id // 2 + 1 if tipo == 'B' else (aeronave_id - 1) // 2 + 1
        nome = f"{letra}-{num:02d}"

        horas_voo = sum(VOOS[v]["duracao"] for v in lista_voos)
        total_horas_voo += horas_voo

        hh = horas_voo // 60
        mm = horas_voo % 60
        print(f"\nAeronave {nome} (Tipo {tipo}) -- {hh}h{mm:02d} de voo:")

        for idx, voo_idx in enumerate(lista_voos):
            voo = VOOS[voo_idx]
            partida_str = minutos_para_hhmm(voo["partida"])
            chegada_str = minutos_para_hhmm(voo["chegada"])
            manut_str = minutos_para_hhmm(voo["chegada"] + INTERVALO_MINIMO)
            print(
                f"  {partida_str} -> {voo['origem']}-{voo['destino']} "
                f"(chegada {chegada_str}) | manutenção até {manut_str}"
            )

        if tipo == "A":
            total_tipo_a += 1
        else:
            total_tipo_b += 1

    # Resumo geral
    n_aeronaves = total_tipo_a + total_tipo_b
    voos_cobertos = len(cromossomo)

    print("\n" + "=" * 72)
    print("RESUMO")
    print("=" * 72)
    print(f"  Aeronaves Tipo A utilizadas : {total_tipo_a}")
    print(f"  Aeronaves Tipo B utilizadas : {total_tipo_b}")
    print(f"  Total de aeronaves          : {n_aeronaves}")
    print(f"  Voos cobertos               : {voos_cobertos} / {len(VOOS)}")

    print("\n" + "-" * 72)
    print("VIOLAÇÕES POR RESTRIÇÃO")
    print("-" * 72)
    print(f"  {'Restrição':<12} | {'Descrição':<42} | {'Violações':>9}")
    print(f"  {'-'*12}-+-{'-'*42}-+-{'-'*9}")
    descricoes = {
        "R1": "Exclusividade de uso (sobreposição)",
        "R2": "Intervalo mínimo entre voos",
        "R3": "Compatibilidade tipo de aeronave",
        "R4": "Continuidade de posicionamento",
        "R5": "Janela operacional (06h-24h)",
        "R6": "Distribuição uniforme de horários",
        "R7": "Limite de 12h de voo por aeronave",
        "R8": "Reposicionamento ao aeroporto base",
    }
    for r, desc in descricoes.items():
        v = violacoes.get(r, 0)
        print(f"  {r:<12} | {desc:<42} | {v:>9}")

    total_v = sum(violacoes.values())
    print(f"\n  Total de violações          : {total_v}")
    print(f"  Fitness da melhor solução   : {fitness:,.0f}")
    print("=" * 72)


def _montar_agenda(cromossomo):
    """
    Monta dicionário aeronave_id -> lista de índices de voo ordenados por partida.
    """
    agenda = {}
    for voo_idx, aeronave_id in enumerate(cromossomo):
        agenda.setdefault(aeronave_id, []).append(voo_idx)
    for aeronave_id in agenda:
        agenda[aeronave_id].sort(key=lambda v: VOOS[v]["partida"])
    return agenda


def exibir_historico_resumido(historico):
    """Exibe tabela resumida da evolução do fitness."""
    print("\n" + "-" * 65)
    print("EVOLUÇÃO DO FITNESS (amostras)")
    print("-" * 65)
    print(f"  {'Geracao':>8} | {'Melhor':>12} | {'Medio':>12} | {'Pior':>12}")
    print(f"  {'-'*8}-+-{'-'*12}-+-{'-'*12}-+-{'-'*12}")
    passo = max(1, len(historico) // 10)
    for i, (ger, melhor, medio, pior) in enumerate(historico):
        if i % passo == 0 or i == len(historico) - 1:
            print(f"  {ger:>8} | {melhor:>12,.0f} | {medio:>12,.0f} | {pior:>12,.0f}")
    print("-" * 65)