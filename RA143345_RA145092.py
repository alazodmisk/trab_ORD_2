# TRABALHO ORGANIZAÇÃO E RECUPERAÇÃO DE DADOS - II
# RA143345 - Pedro Henrique Bertoni de Souza
# RA145092 - Guilherme Henrique Viana Pichitelli Vitor

import io
import sys
import struct

ORDEM: int = 7                              #Ordem é a quantidade de filhos de uma página
NULO: int = -1

# fmtNumChaves = "B" | fmtId = "h" | fmtOffset = "h" | fmtfilhos = "h"  
# fmtPagina = f"{fmtNumChaves}{2*(ORDEM-1)}{fmtId}{ORDEM}{fmtfilhos}"

fmtHeader = '<h'                            #HEADER pra indicar Raiz
TAMHEADER: int = struct.calcsize(fmtHeader)
fmtPagina = f'<B{(3*ORDEM)-2}h'
TAMPAGINA: int = struct.calcsize(fmtPagina)

class Chave:
    def __init__(self, id: int, offset: int):
        self.id = id
        self.offset = offset

class Pagina:
    def __init__(self):
        self.numChaves = 0
        self.chaves = [Chave(NULO, NULO)] * (ORDEM - 1)
        self.filhos = [NULO] * ORDEM


# Func auxiliar de TUDO
def carregaPagina(rrn: int, arvore: io.BufferedRandom) -> Pagina:
    ''' Busca em *arvore* pulando o HEADER e *rrn* paginas. Achada a
    pagina, retorna em formato Pagina() a leitura do arquivo '''

    arvore.seek(TAMHEADER, 0)
    arvore.seek(rrn*TAMPAGINA, 1)

    buffer = arvore.read(TAMPAGINA)
    tupla = struct.unpack(fmtPagina, buffer)                       #Retorna TUPLA
    pag = Pagina()

    pag.numChaves = tupla[0]                                       #numChaves
    for i in range(ORDEM-1):
        pag.chaves[i] = Chave(tupla[(2*i) +1], tupla[(2*i) +2])    #Chaves[]
    for i in range(ORDEM):
        pag.filhos[i] = tupla[(2*(ORDEM-1) +1) +i]                 #Filhos[]

    return pag

# Func auxiliar de TUDO
def escreveNaArvore(pag: Pagina, rrn: int, arvore: io.BufferedRandom):
    ''' Posiciona-se em *arvore* pulando o cabecalho e *rrn* paginas, seja
    para uma ja existente para atualiza-la ou no final do arquivo para escrita
    de uma nova Pagina(). Posicionado escreve *pag* inteira. '''

    arvore.seek(TAMHEADER, 0)
    arvore.seek(rrn*TAMPAGINA, 1)

    linha = struct.pack('<B', pag.numChaves)                         #B  = fmtNumChaves da Pagina
    for i in range(ORDEM-1):                                        #hh = fmtID + fmtOffset de cada Chave
        linha += struct.pack('<hh', pag.chaves[i].id, pag.chaves[i].offset)
    for i in range(ORDEM):                                          #h  = fmtFilho de cada referencia de Filho
        linha += struct.pack('<h', pag.filhos[i])

    arvore.write(linha)



# Func auxiliar de insereNaArvore(), insercao()
def divide(chaveNova: Chave, filhoDpro: int, pagOrig: Pagina, pagRRN: int, arvore: io.BufferedRandom, posLista: int):
    tempChave = pagOrig.chaves[:posLista]   + [chaveNova] + pagOrig.chaves[posLista:]
    tempFilho = pagOrig.filhos[:posLista+1] + [filhoDpro] + pagOrig.filhos[posLista+1:]
    metade = ORDEM // 2
    pagOrig = Pagina()
    pagNova = Pagina()

    for i in range(metade):
        pagOrig.chaves[i]  = tempChave[i]
        pagOrig.filhos[i]  = tempFilho[i]
        pagOrig.numChaves += 1
    pagOrig.filhos[metade] = tempFilho[metade]

    for i in range(metade+1, ORDEM):
        pagNova.chaves[i-metade-1] = tempChave[i]
        pagNova.filhos[i-metade-1] = tempFilho[i]
        pagNova.numChaves += 1
    pagNova.filhos[ORDEM-metade-1] = tempFilho[ORDEM]

    escreveNaArvore(pagOrig, pagRRN, arvore)
    arvore.seek(0,2)
    fim = arvore.tell()
    rrnfim = ((fim-TAMHEADER)//TAMPAGINA)
    escreveNaArvore(pagNova, rrnfim, arvore)

    arvore.seek(0,0)

    chavePromovida = tempChave[metade]
    rrnNovaPagina = rrnfim
    return chavePromovida, rrnNovaPagina

# Func auxiliar de insereNaArvore(), insercao()
def atualizaRaiz(chavePro: Chave, rrnRaiz: int, filhoDpro: int, arvore: io.BufferedRandom):
    novaRaiz = Pagina()                                     #CRIA nova raiz
    novaRaiz.numChaves = 1
    novaRaiz.chaves[0] = chavePro
    novaRaiz.filhos[0] = rrnRaiz
    novaRaiz.filhos[1] = filhoDpro

    if rrnRaiz == NULO:
        rrnRaiz = 0
    else:
        arvore.seek(0,2)
        rrnRaiz = ((arvore.tell() - TAMHEADER)//TAMPAGINA)
    arvore.seek(0,0)           
    arvore.write(struct.pack(fmtHeader, rrnRaiz))       #ATUALIZA referencia da raiz
    
    escreveNaArvore(novaRaiz, rrnRaiz, arvore)             #ESCREVE nova raiz
    return rrnRaiz
    
# Func auxiliar de insereNaArvore(), buscaNaArvore()
def buscaNaPagina(chave: Chave, pag: Pagina):
    pos = 0
    while(pos < pag.numChaves and chave.id > pag.chaves[pos].id):
        pos += 1
    if pos < pag.numChaves and chave.id == pag.chaves[pos].id:
        return True, pos
    else:
        return False, pos



# Func Principal de contruir_indices()
def insereNaArvore(chave: Chave, rrnAtual: int, arvore: io.BufferedRandom):
    if rrnAtual == NULO:
        return chave, NULO, True
    
    pag = carregaPagina(rrnAtual, arvore)
    achou, pos = buscaNaPagina(chave, pag)
    
    if achou:
        print("- Chave duplicada - Insercao interrompida.")
        return None, NULO, False
    
    chavePro, filhoDpro, promo = insereNaArvore(chave, pag.filhos[pos], arvore)

    if promo == False:
        return None, filhoDpro, False
    
    if pag.numChaves < (ORDEM-1):
        pag.chaves = pag.chaves[:pos]   +  [chave]  + pag.chaves[pos:]
        pag.chaves = pag.chaves[:ORDEM-1]
        pag.filhos = pag.filhos[:pos+1] +[filhoDpro]+ pag.filhos[pos+1:]
        pag.filhos = pag.filhos[:ORDEM]
        pag.numChaves += 1

        escreveNaArvore(pag, rrnAtual, arvore)
        return None, None, False
    else:
        chavePro, filhoDpro = divide(chavePro, filhoDpro, pag, rrnAtual, arvore, pos)
        return chavePro, filhoDpro, True

# Func Principal de executar_operacoes()
def buscaNaArvore(chave: Chave, rrnAtual: int, arvore: io.BufferedRandom):
    if rrnAtual == NULO:
        return False, NULO, NULO
    else:
        pagina = carregaPagina(rrnAtual, arvore)
        achou, pos = buscaNaPagina(chave, pagina)
        if achou:
            return True, rrnAtual, pos
        else:
            return buscaNaArvore(chave, pagina.filhos[pos], arvore)

# Func Principal de executar_operacoes()
def busca(arvore: io.BufferedRandom, jogos: io.BufferedReader, id: int):
    referencia = Chave(id, NULO)
    arvore.seek(0, 0)
    rrnRaiz = struct.unpack(fmtHeader, arvore.read(TAMHEADER))[0]
    achou, rrn, pos = buscaNaArvore(referencia, rrnRaiz, arvore)
    if achou:
        referencia.offset = carregaPagina(rrn, arvore).chaves[pos].offset
        jogos.seek(referencia.offset, 0)
        tam = int.from_bytes(jogos.read(2), 'little')
        registro = jogos.read(tam).decode()
        print(f"Registro : {id}\n - {registro} ")
    else:
        print(f"Registro {id} NÃO encontrado...")

# Func Principal de executar_operacoes()
def insercao(arvore: io.BufferedRandom, jogos: io.BufferedReader, registro: str):
    jogos.seek(0,2)
    offset = jogos.tell()
    jogos.write(len(registro).to_bytes(2,'little'))
    jogos.write(registro.encode())

    buffer = registro.split("|",1)
    id = int(buffer[0])

    arvore.seek(0,0)
    rrnRaiz = struct.unpack(fmtHeader, arvore.read(TAMHEADER))[0]
    chavePro, filhoDpro, promo = insereNaArvore(Chave(id,offset), rrnRaiz, arvore)

    if promo:                           #raiz promoveu
        atualizaRaiz(chavePro, rrnRaiz, filhoDpro, arvore)



# Func FLAG -b
def construir_indices():
    with open("btree.dat", "wb") as arvoreB:
        rrnRaiz = NULO
        arvoreB.write(struct.pack(fmtHeader, rrnRaiz))

    offset = 0
    with open('games.dat', 'rb') as games, open("btree.dat", "r+b") as arvoreB:        
        buffer = games.read(2)
        k = 0

        while buffer != b'':
            tam = int.from_bytes(buffer, "little")
            buffer = games.read(tam).decode()
            
            registro = buffer.split("|", 1)
            indice = int(registro[0])

            chavePro, filhoDpro, promo = insereNaArvore(Chave(indice,offset), rrnRaiz, arvoreB)

            if promo:                           #raiz promoveu
                print("RAIZ ATUALIZADA")
                rrnRaiz = atualizaRaiz(chavePro, rrnRaiz, filhoDpro, arvoreB)             #ESCREVE nova raiz
                

            offset += tam + 2
            buffer = games.read(2)
        

    return None

# Func FLAG -e
def executar_operacoes(nome_arquivo):
    print(f"\n>>>>>>>>>>> Executando operações do arquivo: {nome_arquivo} <<<<<<<<<<<\n")

    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f, open("games.dat", 'r+b') as games, open("btree.dat", 'r+b') as arvoreB:
            
            for linha in f:
                linha = linha.strip()

                if not linha:
                    continue  # pula linha vazia
                
                partes = linha.split(" ", 1)

                operacao = partes[0]
                if len(partes) < 2:
                    if operacao == 'b':
                        print('Para operação de Busca, insira um ID de jogo a ser buscado.')
                    elif operacao == 'i':
                        print('Para operação de Inserção, insira um registro no formato: "ID|Nome|Ano|Genero|Publicadora|Plataforma"')
                    else:
                        print("Comando não identificado. Por favor, verifique o arquivo de operações.")
                    print("")
                    continue

                argumento = partes[1]

                if operacao == 'b':
                    busca(arvoreB, games, int(argumento))
                elif operacao == 'i':
                    insercao(arvoreB, games, argumento)

                else:
                    print("Comando não identificado. Por favor, verifique o arquivo de operações.")   
                print("")

        print(f"\n > Operações de {nome_arquivo} executadas com sucesso!! <\n")
        return None

    except FileNotFoundError:
        print("Erro: arquivo de operações/jogos/arvore não encontrado.")

# Func Flag -p
def imprime_arvore():
    try:
        with open("btree.dat", "rb") as arvoreB:
            print("\n>>>>>>>>>> ARVORE LEGAL <<<<<<<<<<")
            raiz = struct.unpack(fmtHeader, arvoreB.read(TAMHEADER))[0]
            buffer = arvoreB.read(TAMPAGINA)
            
            numPag = 0
            while buffer != b'':
                tupla = struct.unpack(fmtPagina, buffer)
                pag = Pagina()

                pag.numChaves = tupla[0]
                for i in range(ORDEM-1):
                    pag.chaves[i] = Chave(tupla[(i*2) +1], tupla[(i*2) +2])
                for i in range(ORDEM):
                    pag.filhos[i] = tupla[(2*(ORDEM-1) + 1) + i]
                
                print("\n")
                if numPag == raiz:
                    print("\n==================== RAIZ =====================")

                print(f"Página {numPag} :")
                print("Chaves  : ", end="|")
                for i in pag.chaves:
                    print(f" {i.id} ", end="|")
                print("\nOffsets : ", end="|")
                for i in pag.chaves:
                    print(f" {i.offset} ", end="|")
                print("\nFilhos  : ", end="|")
                for i in pag.filhos:
                    print(f" {i} ", end="|")

                if numPag == raiz:
                    print("\n===============================================")

                numPag += 1
                buffer = arvoreB.read(TAMPAGINA)
            print("\n\n>>>>>>>>>>>>>>> FIM <<<<<<<<<<<<<<\n")

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

    elif flag == '-p':
        imprime_arvore()
        
    else:
        print(f"Flag '{flag}' não reconhecida.")

if __name__ == "__main__":
    main()     
