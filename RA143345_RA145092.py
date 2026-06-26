# TRABALHO ORGANIZAÇÃO E RECUPERAÇÃO DE DADOS - II
# RA143345 - Pedro Henrique Bertoni de Souza
# RA145092 - Guilherme Henrique Viana Pichitelli Vitor

import io
import sys
import struct

ORDEM: int = 7
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
    pagina, retorna a leitura do arquivo em formato Pagina(). '''

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
    para uma ja existente ou no final do arquivo. Assim, escreve *pag* inteira. '''

    arvore.seek(TAMHEADER, 0)
    arvore.seek(rrn*TAMPAGINA, 1)

    linha = struct.pack('<B', pag.numChaves)                         #B  = fmtNumChaves da Pagina
    for i in range(ORDEM-1):                                        #hh = fmtID + fmtOffset de cada Chave
        linha += struct.pack('<hh', pag.chaves[i].id, pag.chaves[i].offset)
    for i in range(ORDEM):                                          #h  = fmtFilho de cada referencia de Filho
        linha += struct.pack('<h', pag.filhos[i])

    arvore.write(linha)


# Func auxiliar de insereNaArvore(), atualizaRaiz()
def novoRrn(arvore: io.BufferedRandom) -> int:
    ''' Posiciona-se no final de *arvore* e retorna o RRN para inserções no final do arquivo. '''
    arvore.seek(0,2)
    offsetFim = arvore.tell()
    return ((offsetFim - TAMHEADER)//TAMPAGINA)

# Func auxiliar de insereNaArvore()
def divide(chaveNova: Chave, filhoDpro: int, pagOrig: Pagina, pagRRN: int, arvore: io.BufferedRandom, posLista: int):
    ''' Trata Overflow de Chaves em uma pagina *pagOrig*.
    - Encontra *pagOrig* em *arvore* de acordo com seu *pagRRN*. Aloca temporariamente uma lista de suas
    Chaves e outra de seus filhos, inserindo *chaveNova* e *filhoDpro* de acordo com *posLista*.
    - *pagOrig* é reinicializada e _pagNova_ é criada. Extraindo das listas temporárias, as informações
    até antes da metade (pagOrig) e após a metade (pagNova).
    - Retorna a Chave na metade da lista temporária e RRN de _pagNova_. '''

    chValidas = pagOrig.chaves[:pagOrig.numChaves]
    fiValidos = pagOrig.filhos[:pagOrig.numChaves+1]

    tempChave = chValidas[:posLista]   + [chaveNova] + chValidas[posLista:]
    tempFilho = fiValidos[:posLista+1] + [filhoDpro] + fiValidos[posLista+1:]
    metade = len(chValidas)// 2
    chPromo = tempChave[metade]

    pag1 = Pagina()
    pag2 = Pagina()

    for i in range(metade):
        pag1.chaves[i]  = tempChave[i]
        pag1.filhos[i]  = tempFilho[i]
        pag1.numChaves += 1
    pag1.filhos[metade] = tempFilho[metade]

    for i in range(metade+1, ORDEM):
        pag2.chaves[i-metade-1] = tempChave[i]
        pag2.filhos[i-metade-1] = tempFilho[i]
        pag2.numChaves += 1
    pag2.filhos[ORDEM-metade-1] = tempFilho[ORDEM]

    escreveNaArvore(pag1, pagRRN, arvore)
    fimRRN = novoRrn(arvore)
    escreveNaArvore(pag2, fimRRN, arvore)


    return chPromo, fimRRN    # chavePromovida, novoRRN 

# Func auxiliar de insereNaArvore(), insercao()
def atualizaRaiz(chavePro: Chave, rrnRaiz: int, filhoDpro: int, arvore: io.BufferedRandom):
    ''' Para casos de divisão da pagina raiz da arvore.
    Cria uma nova pagina _novaRaiz_ para ser promovida, recebendo *chavePro* como unica
    chave e *rrnRaiz* e *filhoDpro* como seus filhos. Acessa *arvore* e atualiza seu 
    cabecalho com RRN da nova Raiz. '''
    
    novaRaiz = Pagina()                                     #CRIA nova raiz
    novaRaiz.numChaves = 1
    novaRaiz.chaves[0] = chavePro
    novaRaiz.filhos[0] = rrnRaiz
    novaRaiz.filhos[1] = filhoDpro

    if rrnRaiz == NULO:
        rrnRaiz = 0
    else:
        rrnRaiz = novoRrn(arvore)
    arvore.seek(0,0)           
    arvore.write(struct.pack(fmtHeader, rrnRaiz))       #ATUALIZA referencia da raiz
    
    escreveNaArvore(novaRaiz, rrnRaiz, arvore)             #ESCREVE nova raiz
    return rrnRaiz
    
# Func auxiliar de insereNaArvore(), buscaNaArvore()
def buscaNaPagina(chave: Chave, pag: Pagina):
    ''' Vasculha *pagina* procurando por *chave* a partir de seu id. Caso
    encontre ou não, retorna onde está/poderia estar. '''

    pos = 0
    while(pos < pag.numChaves and chave.id > pag.chaves[pos].id):
        pos += 1
    if pos < pag.numChaves and chave.id == pag.chaves[pos].id:
        return True, pos
    else:
        return False, pos

# Func auxiliar de busca()
def buscaNaArvore(chave: Chave, rrnAtual: int, arvore: io.BufferedRandom):
    ''' Vasculha a pagina em *arvore* no RRN *rrnAtual*.
    - Caso encontre *chave* retorna o RRN da pagina onde está, e sua posicao na mesma.
    - Caso contrário, aplica uma recursão com um de seus filhos, até sair de uma folha. '''

    if rrnAtual == NULO:
        return False, NULO, NULO
    else:
        pagina = carregaPagina(rrnAtual, arvore)
        achou, pos = buscaNaPagina(chave, pagina)
        if achou:
            return True, rrnAtual, pos
        else:
            return buscaNaArvore(chave, pagina.filhos[pos], arvore)


# Func Principal de contruir_indices(), auxiliar de insercao()
def insereNaArvore(chave: Chave, rrnAtual: int, arvore: io.BufferedRandom):
    ''' Desce por *arvore* a partir de *rrnAtual* ate encontrar uma folha.
    - Caso encontre *chave* no caminho interrompre o processo.
    - Caso chegue numa folha comeca a recursao de insercao. Retorna a chave promovida
    e seu filho a direita para chamada anterior, até haver uma insercao sem divisao. '''

    if rrnAtual == NULO:
        return chave, NULO, True
    
    pag = carregaPagina(rrnAtual, arvore)
    achou, pos = buscaNaPagina(chave, pag)
    
    if achou:                       # Não permite inserções de IDs repetidos
        return None, None, False
    
    chavePro, filhoDpro, promo = insereNaArvore(chave, pag.filhos[pos], arvore)

    if not promo:
        return None, filhoDpro, False
    
    if pag.numChaves < (ORDEM-1):
        pag.chaves = pag.chaves[:pos]   +  [chave]  + pag.chaves[pos:ORDEM-2]
        pag.filhos = pag.filhos[:pos+1] +[filhoDpro]+ pag.filhos[pos+1:ORDEM-1]
        pag.numChaves += 1

        escreveNaArvore(pag, rrnAtual, arvore)
        return None, NULO, False
    
    chavePro, filhoDpro = divide(chavePro, filhoDpro, pag, rrnAtual, arvore, pos)
    return chavePro, filhoDpro, True

# Func Principal de executar_operacoes()
def busca(arvore: io.BufferedRandom, jogos: io.BufferedReader, id: int):
    ''' Vaculha *arvore* a partir de sua raiz por uma chave com *id*. Caso
    encontre, extrai seu offset e faz leitura em *jogos*. '''

    referencia = Chave(id, NULO)
    arvore.seek(0,0)
    rrnRaiz = struct.unpack(fmtHeader, arvore.read(TAMHEADER))[0]

    achou, rrn, pos = buscaNaArvore(referencia, rrnRaiz, arvore)

    if achou:
        referencia.offset = carregaPagina(rrn, arvore).chaves[pos].offset
        jogos.seek(referencia.offset, 0)

        tam = int.from_bytes(jogos.read(2), 'little')
        registro = jogos.read(tam).decode()
        print(f" >> Busca Registro : {id}\n    - {registro} ")
    else:
        print(f" >> Busca Registro {id} NÃO encontrado...")

# Func Principal de executar_operacoes()
def insercao(arvore: io.BufferedRandom, jogos: io.BufferedReader, registro: str):
    ''' Tenta inserir (id,offset) de *registro* em *arvore*. Caso seja possivel
    acessa *jogos* e escreve *registro*. '''

    buffer = registro.split("|",2)
    id = int(buffer[0])

    jogos.seek(0,2)
    offset = jogos.tell()
    
    arvore.seek(0,0)
    rrnRaiz = struct.unpack(fmtHeader, arvore.read(TAMHEADER))[0]
    chavePro, filhoDpro, promo = insereNaArvore(Chave(id,offset), rrnRaiz, arvore)

    if promo or filhoDpro == NULO:                           #raiz promoveu
        if promo:
            rrnRaiz = atualizaRaiz(chavePro, rrnRaiz, filhoDpro, arvore)

        jogos.write(len(registro).to_bytes(2,'little'))
        jogos.write(registro.encode())
        
        print(f" >> Registro {id}:'{buffer[1]}' aceito. Inserção realizada.")
    else:
        print(f" >> Chave '{id}' duplicada. Inserção interrompida.")



# Func FLAG -b
def construir_indices():
    with open("btree.dat", "wb") as arvoreB:
        rrnRaiz = NULO
        arvoreB.write(struct.pack(fmtHeader, rrnRaiz))

    offset = 0
    with open('games.dat', 'rb') as games, open("btree.dat", "r+b") as arvoreB:        
        buffer = games.read(2)

        while buffer != b'':
            tam = int.from_bytes(buffer, "little")
            buffer = games.read(tam).decode()
            
            registro = buffer.split("|", 1)
            indice = int(registro[0])

            arvoreB.seek(0, 0)
            rrnRaiz = struct.unpack(fmtHeader, arvoreB.read(TAMHEADER))[0]

            chavePro, filhoDpro, promo = insereNaArvore(Chave(indice,offset), rrnRaiz, arvoreB)

            if promo:                                                           #raiz promoveu
                rrnRaiz = atualizaRaiz(chavePro, rrnRaiz, filhoDpro, arvoreB) 
                
            offset += tam + 2
            buffer = games.read(2)
        
    print(f"\n >> ORDEM {ORDEM} : Arvore 'btree.dat' construída com sucesso. \n")
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

        print(f">>>>>>>>>>> Operações de {nome_arquivo} executadas com sucesso!! <\n")
        return None

    except FileNotFoundError:
        print("Erro: arquivo de operações/games.dat/btree.dat não encontrado.\n")

# Func Flag -p
def imprime_arvore():
    try:
        with open("btree.dat", "rb") as arvoreB:
            print("\n>>>>>>>>>>>>>>>>> ARVORE LEGAL <<<<<<<<<<<<<<<<<<")
            raiz = struct.unpack(fmtHeader, arvoreB.read(TAMHEADER))[0]
            numPag = 0

            buffer = arvoreB.read(TAMPAGINA)
            while buffer != b'':
                tupla = struct.unpack(fmtPagina, buffer)
                pag = Pagina()

                pag.numChaves = tupla[0]
                for i in range(ORDEM-1):
                    pag.chaves[i] = Chave(tupla[(i*2) +1], tupla[(i*2) +2])
                for i in range(ORDEM):
                    pag.filhos[i] = tupla[(2*(ORDEM-1) +1) +i]
                
                print("\n")
                if numPag == raiz:
                    print("\n======================== RAIZ ===========================")

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
                    print("\n=========================================================")

                numPag += 1
                buffer = arvoreB.read(TAMPAGINA)
            print("\n\n>>>>>>>>>>>>>>>>>>>>> FIM <<<<<<<<<<<<<<<<<<<<<\n")

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
