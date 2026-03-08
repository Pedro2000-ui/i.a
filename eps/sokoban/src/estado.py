from config import MOVIMENTOS

def objetivo(state, alvos):

    agente, caixas, carregando = state

    # Restrição 1:
    # se o agente estiver carregando uma caixa, não atingiu o objetivo
    if carregando is not None:
        return False
    
    # Restrição 2:
    # se as caixas não estiverem nos alvos (gols), não atingiu o objetivo
    for x,y,p in caixas:
        if (x,y) not in alvos:
            return False
    
    # Restrição 3:
    # se todas as caixas estão nos alvos (gols), mas o agente está em uma posição de alvo, não atingiu o objetivo
    if agente in alvos:
        return False

    return True

def sucessores(grid, state):

    agente, caixas, carregando = state
    caixas_dict = {(x,y):p for x,y,p in caixas}

    suc = []

    x,y = agente

    # movimentos
    for mov,(dx,dy) in MOVIMENTOS.items():

        nx = x + dx
        ny = y + dy

        if nx < 0 or ny < 0 or nx >= len(grid) or ny >= len(grid[0]):
            continue
            
        if grid[nx][ny] == "#":
            continue

        # se carregando caixa
        if carregando is not None:

            if (nx,ny) in caixas_dict:
                continue

            novo = ((nx,ny), caixas, carregando)
            custo = 1 + carregando

            suc.append((novo,mov,custo))

        else:

            custo = 1
            novo = ((nx,ny), caixas, None)
            suc.append((novo,mov,custo))


    # pegar caixa
    if carregando is None:

        if agente in caixas_dict:

            peso = caixas_dict[agente]

            novas = caixas_dict.copy()
            del novas[agente]

            novo = (
                agente,
                frozenset((x,y,p) for (x,y),p in novas.items()),
                peso
            )

            suc.append((novo,"P",1)) # pegar caixa


    # soltar caixa
    else:

        if agente not in caixas_dict:

            novas = caixas_dict.copy()
            novas[agente] = carregando

            novo = (
                agente,
                frozenset((x,y,p) for (x,y),p in novas.items()),
                None
            )

            suc.append((novo,"S",1)) # soltar caixa


    return suc

def gerar_grid(grid,state,alvos):

    agente,caixas,carregando = state
    caixas = {(x,y):p for x,y,p in caixas}

    g = [l[:] for l in grid]

    for x,y in alvos:
        g[x][y] = "G"

    for (x,y),p in caixas.items():
        g[x][y] = str(p)

    ax,ay = agente
    g[ax][ay] = "A"

    # mostrar caixa carregada
    if carregando is not None:
        g[ax][ay] = "A"+str(carregando)

    return g
