import heapq
from src.estado import objetivo, sucessores
from src.heuristica import heuristica

def busca(grid,start,alvos,modo):

    fila = []
    mov_custo = {}
    visit = set()

    heapq.heappush(fila,(0,start,[],0))

    while fila:

        prioridade,state,path,custo = heapq.heappop(fila)
        mov_custo[state] = custo

        if state in visit:
            continue

        visit.add(state)

        if objetivo(state,alvos):
            return state,path,custo,visit

        for novo,mov,c in sucessores(grid,state):
            novo_custo = custo + c
            
            if modo == "dijkstra":
                prioridade = novo_custo

            elif modo == "ganancioso":
                prioridade = heuristica(novo,alvos)

            else:
                prioridade = novo_custo + heuristica(novo,alvos)

            heapq.heappush(
                fila,
                (prioridade,novo,path+[(mov,c)],novo_custo)
            )

    return None
