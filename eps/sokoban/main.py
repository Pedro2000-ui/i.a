import os
import sys
import time

from src.leitura import leitura
from src.busca import busca
from src.estado import gerar_grid
from src.saida import gera_analise

def main():

    # verificar se o arquivo foi passado como argumento
    if len(sys.argv) < 2:
        print("Uso: python main.py maps/<arquivo.txt>")
        sys.exit(1)

    arquivo = sys.argv[1]

    # verificar extensão
    if not arquivo.lower().endswith(".txt"):
        print("Erro: o arquivo deve ser .txt")
        sys.exit(1)

    # verificar se existe
    if not os.path.isfile(arquivo):
        print("Erro: arquivo não encontrado")
        sys.exit(1)
    
    # verificar se o arquivo está vazio
    if os.path.getsize(arquivo) == 0:
        print("Erro: arquivo vazio")
        sys.exit(1)

    nome = os.path.basename(arquivo)
    grid,agente,caixas,alvos = leitura(arquivo)

    start = (
        agente,
        # x,y -> coordenada da caixa, p -> peso da caixa
        # Transforma em uma tupla simples (x,y,p) para usar como estado
        frozenset((x,y,p) for (x,y),p in caixas.items()),
        None
    )

    algoritmos = {
        "ganancioso":"results/ganancioso/"+nome,
        "a*":"results/a_estrela/"+nome,
        "dijkstra":"results/dijkstra/"+nome
    }

    for modo,arquivo in algoritmos.items():

        inicio = time.perf_counter()
        res = busca(grid,start,alvos,modo)
        fim = time.perf_counter()
        
        tempo = fim - inicio

        if res is None:
            print("Sem solução:",modo)
            continue
        
        print("Solução encontrada para " + modo + " e gerada em",arquivo)
        
        estado,mov,custo_total,visit = res

        # Dá tupla do caminho (movimento, custo) pega apenas os movimentos
        movimentos = [m for m,c in mov]
        # Dá tupla do caminho (movimento, custo) pega apenas os custos
        custos_por_movimento = [c for m,c in mov]

        grid_final = gerar_grid(grid,estado,alvos)

        resultado = {
            "grid": grid_final,
            "movimentos": movimentos,
            "custos": custos_por_movimento,
            "custo": custo_total,
            "tempo": tempo,
            "visitados": visit
        }
        gera_analise(arquivo,resultado)


if __name__ == "__main__":
    main()