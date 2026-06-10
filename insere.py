ordem: int = 0 ##Ordem é a quantidade de filhos de uma página


class Pagina:
    def __init__(self) -> None:
        self.numChaves: int = 0
        self.chaves: list = [None] * (ordem - 1)
        self.filhos: list = [None] * ordem


def insereNaArvore(chave, rrnAtual):
    if rrnAtual == None:
        chavePro = chave
        filhoDpro = None
        return chavePro, filhoDpro, True
    else:
        ##ler a página que tem que carregar na memória e chamar de pag
        achou, pos = buscaNaPagina(chave, pag)

    if achou:
        print("Chave fuplicada")
    
    chavePro, filhoDpro, promo = insereNaArvore(chave, pag.filhos[pos])

    if promo == False:
        return None, None, False
    else:
        if pag.numChaves <= ordem:
            pag.chaves.append(chavePro)
            pag.filhos.append(filhoDpro)
            ##escrever pagina no arquivo na posição rrnAtual
            return None, None, False
        else:
            