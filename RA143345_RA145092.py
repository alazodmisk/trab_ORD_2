# TRABALHO ORGANIZAÇÃO E RECUPERAÇÃO DE DADOS - II
# RA143345 - Pedro Henrique Bertoni de Souza
# RA145092 - Guilherme Henrique Viana Pichitelli Vitor

import io
import os
import sys
import struct


ORDEM: int = 0 ##Ordem é a quantidade de filhos de uma página
NULO: int = -1


class Chave:
    id: int
    offset: int

class Pagina:
    def __init__(self) -> None:
        self.numChaves: int = 0
        self.chaves: list[int|Chave] = [NULO] * (ORDEM - 1)
        self.filhos: list = [NULO] * ORDEM


def insercao(arvore: list[Pagina], novoRegistro: Chave):
    return None

def construir_indices():
    paginas: list[Pagina] =  []
    offset = 0

    with open('games.dat', 'rb') as games:
        buffer = games.read(2)

        while buffer != b'':
            tam = int.from_bytes(buffer, "little")
            buffer = games.read(tam).decode()
            
            registro:list[str] = buffer.split("|", 1)
            indice = int(registro[0])

            insercao(paginas, Chave(indice, offset))
            offset += tam + 2()

            buffer = games.read(2)

    with open("btree.dat", "wb") as arvoreB:
        for i in paginas:
            linha = struct.pack("I", i.numChaves)

            for j in i.chaves:
                linha += struct.pack("II", j.id, j.offset)
            
            for k in i.filhos:
                linha += struct.pack("I", k)


            arvoreB.write(linha)
    return None


def carrega_paginas() -> list[Pagina]:
    return list[Pagina]

def insercao():
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