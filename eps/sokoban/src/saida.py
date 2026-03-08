
# -------------------------
# relatório
# -------------------------

def gera_analise(arquivo,resultado):

    with open(arquivo,"w") as f:

        f.write("Tempo total: {:.4f} segundos\n".format(resultado["tempo"]))
        f.write("Custo total: {}\n".format(resultado["custo"]))
        f.write("Estados visitados: {}\n".format(len(resultado["visitados"])))
        f.write("Quantidade de movimentos: {}\n\n".format(len(resultado["movimentos"])))
        
        f.write("Estado final\n")

        for l in resultado["grid"]:
            f.write(" ".join(l)+"\n")

        f.write("\n")
        
        f.write("Movimentos\n")
        f.write(" ".join(resultado["movimentos"])+"\n")

        f.write("\n")
        f.write("Custo por movimento\n")
        f.write(" ".join("+"+str(c) for c in resultado["custos"])+"\n")
        
        f.write("\n")
        f.write("Legenda")
        f.write("\nP: Pegar caixa")
        f.write("\nS: Soltar caixa")
        f.write("\nD: Direita")
        f.write("\nE: Esquerda")
        f.write("\nC: Cima")
        f.write("\nB: Baixo")
