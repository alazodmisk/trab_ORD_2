# TRABALHO ORGANIZAÇÃO E RECUPERAÇÃO DE DADOS - II
# RA143345 - Pedro Henrique Bertoni de Souza
# RA145092 - Guilherme Henrique Viana Pichitelli Vitor

import io
import os
import sys
import struct

ORDEM: int = 0 ##Ordem é a quantidade de filhos de uma página
NULO: int = -1

fmtChave = "HH"
fmtPagina = f"HB{ORDEM-1}H{ORDEM-1}H{ORDEM}h"

class Chave:
    def __init__(self) -> None:
        self.id: int = NULO
        self.offset: int = NULO

class Pagina:
    def __init__(self, rrn: int) -> None:
        self.rrn: int = rrn
        self.numChaves: int = 0
        self.chaves: list[Chave] = [Chave()] * (ORDEM - 1)
        self.filhos: list = [-1] * ORDEM


def divide(chaveNova: Chave, filhoNovo: int, paginaCheia: Pagina, maiorRRN: int, posicaoLista: int) -> Chave, int, Pagina, Pagina;
    listaTemp: list[Chave] = paginaCheia.chaves
    listaTemp = listaTemp[:posicaoLista] + [chaveNova] + listaTemp[posicaoLista:]

    metade = ORDEM / 2
    paginaNova: Pagina = Pagina()

    for i in range(metade):
        if i < metade:
            
            paginaNova
            paginaNova.filhos = paginaCheia.filhos[metade + i]
            paginaCheia.filhos[metade + i] = NULO
            
        elif i > metade:
            pagino

    

    maiorRRN += 1

    chavePromovida = listaTemp[metade]
    rrnNovaPagina = maiorRRN

    return chavePromovida, rrnNovaPagina, paginaCheia, paginaNova


def insereNaArvore(chave: Chave, rrnAtual: int, paginas: list[Pagina], maiorRRN: int):
    if rrnAtual == None:
        # chavePro = chave
        # filhoDpro = None
        return chave, None, True
    else:
        achou, pos = buscaNaPagina(chave, paginas[rrnAtual])

    if achou:
        print("Chave duplicada")
        return None, None, False
    
    chavePro, filhoDpro, promo = insereNaArvore(chave, paginas[rrnAtual].filhos[pos], paginas, maiorRRN)

    if promo == False:
        return None, None, False
    else:
        if paginas[rrnAtual].numChaves <= ORDEM:
            paginas[rrnAtual].chaves.append(chavePro)
            paginas[rrnAtual].filhos.append(filhoDpro)
            return None, None, False
        else:
            chavePro, filhoDpro, paginas[rrnAtual], novaPag = divide(chavePro, filhoDpro, paginas[rrnAtual], maiorRRN, pos)
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
            return True, rrnAtual, pos
        else:
            return buscaNaArvore(chave, paginas[rrnAtual].filhos[pos], paginas)



def construir_indices():
    raiz: Pagina = Pagina(0)
    paginas: list[Pagina] = [raiz]
    offset = 0

    with open('games.dat', 'rb') as games:
        buffer = games.read(2)

        while buffer != b'':
            tam = int.from_bytes(buffer, "little")
            buffer = games.read(tam).decode()
            
            registro:list[str] = buffer.split("|", 1)
            indice = int(registro[0])

            insercao(paginas, Chave(indice, offset))
            offset += tam + 2

            buffer = games.read(2)

    with open("btree.dat", "wb") as arvoreB:
        for i in paginas:
            linha = struct.pack("HB", i.rrn, i.numChaves)

            for j in i.chaves:
                linha += struct.pack(fmtChave, j.id, j.offset)
            
            for k in i.filhos:
                linha += struct.pack("H", k)


            arvoreB.write(linha)
    return None


def carrega_paginas() -> list[Pagina]:
    return [Pagina(1)]


def insercao(arvore: list[Pagina], novoRegistro: Chave):
    return None

def busca():
    return None


def executar_operacoes(nome_arquivo):

    print(f"\n-------> Executando operações do arquivo: {nome_arquivo} <-------\n")

    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f, open("games.dat", 'r+b') as games, open("btree.dat", 'r+b') as arvoreB:
            
            paginas = carrega_paginas(arvoreB)

            for linha in f:
                linha = linha.strip()

                if not linha:
                    continue  # pula linha vazia
                
                partes = linha.split(" ", 1)

                operacao = partes[0]
                argumento = partes[1]

                if operacao == 'b':
                    busca(paginas, int(argumento), games)
                elif operacao == 'i':
                    insercao(paginas, str(argumento), games)

                else:
                    print("Comando não identificado. Por favor, verifique o arquivo de operações.")   
                print("")

            games.close()



            return None
        


        print(f"As operações do arquivo {nome_arquivo} foram executadas com sucesso!")

    except FileNotFoundError:
        print("Erro: arquivo de operações não encontrado.")






def imprime_arvore():
    return None






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