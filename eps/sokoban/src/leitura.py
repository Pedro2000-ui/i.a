def leitura(arquivo):

    grid = []
    agente = None
    caixas = {}
    alvos = set()

    with open(arquivo) as f:

        for i, linha in enumerate(f):

            linha = linha.strip().split()
            grid.append(linha)

            for j, c in enumerate(linha):

                if c == "A":
                    agente = (i,j)
                    grid[i][j] = "."

                elif c == "G":
                    alvos.add((i,j))

                elif c.isdigit():
                    caixas[(i,j)] = int(c)
                    grid[i][j] = "."

    return grid, agente, caixas, alvos
