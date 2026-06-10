ordem: int = 0 ##Ordem é a quantidade de filhos de uma página


class Pagina:
    def __init__(self) -> None:
        self.numChaves: int = 0
        self.chaves: list = [None] * (ordem - 1)
        self.filhos: list = [None] * ordem


def buscaNaPagina(chave, pag):
    pos = 0
    while(pos < pag.numChaves and chave > pag.chaves[pos]):
        pos += 1
    if pos < pag.numChaves and chave == pag.chaves[pos]:
        return True, pos
    else:
        return False, pos


def buscaNaArvore(chave, rrn):
    if rrn == None:
        return False, None, None
    else:
        ## Aqui tem que ler a pagina para uma variavel chamada pag
        ## Para isso preciso saber como que a página vai estar armazenada em um arquivo
        achou, pos = buscaNaPagina(chave, pag)
        if achou:
            return True, rrn, pos
        else:
            return buscaNaArvore(chave, pag.filhos[pos])