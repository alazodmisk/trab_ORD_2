# TRABALHO ORGANIZAÇÃO E RECUPERAÇÃO DE DADOS - II
# RA143345 - Pedro Henrique Bertoni de Souza
# RA145092 - Guilherme Henrique Viana Pichitelli Vitor

import io
import os
import sys
import struct

ORDEM: int = 6 ##Ordem é a quantidade de filhos de uma página
NULO: int = -1

fmtCabecalho = "h" ##Indica a raíz da Árvore
TAMCABECALHO: int = sys.getsizeof(fmtCabecalho)
fmtChave = "HH"
fmtPagina = f"B{ORDEM-1}H{ORDEM-1}H{ORDEM}h"
TAMPAGINA: int = sys.getsizeof(fmtPagina)

class Chave:
    def __init__(self) -> None:
        self.id: int = NULO
        self.offset: int = NULO

class Pagina:
    def __init__(self) -> None:
        self.numChaves: int = 0
        self.chaves: list[Chave] = [Chave()] * (ORDEM - 1)
        self.filhos: list = [NULO] * ORDEM


def divide(chaveNova: Chave, filhoDpro: int, paginas: list[Pagina], pagRRN: int, posicaoLista: int):
    pagOrig = paginas[pagRRN]
    
    listaChavesTemp = pagOrig.chaves[:posicaoLista]   + [chaveNova] + pagOrig.chaves[posicaoLista:]
    listaFilhosTemp = pagOrig.filhos[:posicaoLista+1] + [filhoDpro] + pagOrig.filhos[posicaoLista+1:]

    metade = ORDEM // 2
    pagNova: Pagina = Pagina()


    for i in range(ORDEM-2):
        if i < metade - 1:
            pagNova.chaves[i] = listaChavesTemp[metade + i + 1]
            pagOrig.chaves[i] = listaChavesTemp[i]
            pagNova.filhos[i] = listaFilhosTemp[metade + i + 1]
            pagOrig.filhos[i] = listaFilhosTemp[i]

        elif i == metade - 1:
            pagOrig.chaves[i] = listaChavesTemp[i]
            pagNova.filhos[i] = listaFilhosTemp[metade + i + 1]
            pagOrig.filhos[i] = listaFilhosTemp[i]

        elif i == metade:
            pagOrig.chaves[i].id = NULO
            pagOrig.chaves[i].offset = NULO
            pagOrig.filhos[i] = listaFilhosTemp[i]

        else:
            pagOrig.chaves[i].id = NULO
            pagOrig.chaves[i].offset = NULO
            pagOrig.filhos[i] = NULO

    pagOrig.filhos[ORDEM-1] = NULO

    paginas[pagRRN] = pagOrig
    paginas.append(pagNova)

    chavePromovida = listaChavesTemp[metade]
    rrnNovaPagina = len(paginas)
    return chavePromovida, rrnNovaPagina


def insereNaArvore(chave: Chave, rrnAtual: int, paginas: list[Pagina]):

    if rrnAtual == None:                            #Identifica chegada em Folha
        return chave, None, True
    else:                                           #Caso nao ache a Chave, fala onde deve entrar
        achou, pos = buscaNaPagina(chave, paginas[rrnAtual])

    if achou:
        print("- Chave duplicada - Insercao interrompida.")
        return None, None, False
    
    chavePro, filhoDpro, promo = insereNaArvore(chave, paginas[rrnAtual].filhos[pos], paginas)

    if promo == False:
        return None, None, False
    else:
        if paginas[rrnAtual].numChaves < ORDEM - 1: #POSICAO de insercao ja achada, so colocar la
            paginas[rrnAtual].chaves = paginas[rrnAtual].chaves[:pos] + [chavePro]  + paginas[rrnAtual].chaves[pos:]
            paginas[rrnAtual].filhos = paginas[rrnAtual].filhos[:pos] + [filhoDpro] + paginas[rrnAtual].filhos[pos:]
            return None, None, False
        else:
            chavePro, filhoDpro = divide(chavePro, filhoDpro, paginas, rrnAtual, pos)
            return chavePro, filhoDpro, True


def buscaNaPagina(chave: Chave, pag: Pagina):
    pos = 0
    while(pos < pag.numChaves and chave.id > pag.chaves[pos].id):
        pos += 1
    if pos < pag.numChaves and chave == pag.chaves[pos]:
        return True, pos
    else:
        return False, pos


def buscaNaArvore(chave: Chave, rrnAtual: int, paginas: list[Pagina]):
    if rrnAtual == None:
        return False, None, None
    else:
        achou, pos = buscaNaPagina(chave, paginas[rrnAtual])
        if achou:
            return achou, rrnAtual, pos
        else:
            return buscaNaArvore(chave, paginas[rrnAtual].filhos[pos], paginas)



def construir_indices():
    raiz = -1
    paginas: list[Pagina] = [Pagina()]
    offset = 0

    with open('games.dat', 'rb') as games:
        buffer = games.read(2)

        while buffer != b'':
            tam = int.from_bytes(buffer, "little")
            buffer = games.read(tam).decode()
            
            registro:list[str] = buffer.split("|", 1)
            indice = int(registro[0])

            insereNaArvore(paginas, Chave(indice, offset))
            offset += tam + 2

            buffer = games.read(2)

    with open("btree.dat", "wb") as arvoreB:
        for i in paginas:
            linha = struct.pack("B", i.numChaves)

            for j in i.chaves:
                linha += struct.pack(fmtChave, j.id, j.offset)
            
            for k in i.filhos:
                linha += struct.pack("H", k)


            arvoreB.write(linha)
    return None



def insercao(arvore: io.BufferedRandom, novoRegistro: Chave, games: io.BufferedReader):
    return None

def busca(arvore: io.BufferedRandom, buscaID: int, games: io.BufferedReader):
    return None


def executar_operacoes(nome_arquivo):

    print(f"\n-------> Executando operações do arquivo: {nome_arquivo} <-------\n")

    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f, open("games.dat", 'rb') as games, open("btree.dat", 'r+b') as arvoreB:
            
            for linha in f:
                linha = linha.strip()

                if not linha:
                    continue  # pula linha vazia
                
                partes = linha.split(" ", 1)

                operacao = partes[0]
                argumento = partes[1]

                if operacao == 'b':
                    busca(arvoreB, int(argumento), games)
                elif operacao == 'i':
                    insercao(arvoreB, argumento, games)

                else:
                    print("Comando não identificado. Por favor, verifique o arquivo de operações.")   
                print("")

            return None
        


        print(f"As operações do arquivo {nome_arquivo} foram executadas com sucesso!")

    except FileNotFoundError:
        print("Erro: arquivo de operações/jogos/arvore não encontrado.")






def imprime_arvore():
    try:
        with open("btree.dat", "rb") as arvoreB:
            raiz: int  = arvoreB.read(TAMCABECALHO)
            numPaginas = (arvoreB.seek(0, 2).tell() - TAMCABECALHO)/fmtPagina #vai pro final e conta onde é o final
            for i in range(numPaginas):
                if i == raiz:
                    print("---------------- RAIZ ------------------")

                arvoreB.read(TAMPAGINA)
                arvoreB.seek(i * fmtPagina + TAMCABECALHO, 0)

                if i == raiz:
                    print("----------------------------------------")


    except FileNotFoundError:
        print("Erro: arquivo de arvore não encontrado")






def main():
    if len(sys.argv) < 2:
        print("Erro: Use as flags -b, -e ou -p.")
        return

    flag = sys.argv[1]

    if flag == '-b':
        construir_indices()
        
    elif flag == '-e':
        if len(sys.argv) < 3:
            print("Erro: Para usar -e, você deve informar o arquivo de operações.")
        else:
            arquivo_ops = sys.argv[2]
            executar_operacoes(arquivo_ops)

    elif flag == '-c':
        imprime_arvore()
        
    else:
        print(f"Flag '{flag}' não reconhecida.")

if __name__ == "__main__":
    main()     
