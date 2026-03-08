def heuristica(state, alvos):

    agente, caixas, carregando = state

    heuristica = 0

    for x,y,p in caixas:

        menor = float("inf")

        for ax,ay in alvos:
            dist = abs(x-ax) + abs(y-ay)
            menor = min(menor, dist)

        heuristica += menor * p

    return heuristica
