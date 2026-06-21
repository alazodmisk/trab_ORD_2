# TRABALHO ORGANIZAÇÃO E RECUPERAÇÃO DE DADOS - II
# RA143345 - Pedro Henrique Bertoni de Souza
# RA145092 - Guilherme Henrique Viana Pichitelli Vitor

import io
import sys
import struct

ORDEM: int = 6 ##Ordem é a quantidade de filhos de uma página
NULO: int = -1

fmtCabecalho = "h" ##Indica a raíz da Árvore
TAMCABECALHO: int = sys.getsizeof(fmtCabecalho)

TAMID: int = sys.getsizeof("H")
TAMOFFSET: int = sys.getsizeof("H")
TAMFILHO: int = sys.getsizeof("h")
fmtPagina = f"H{2*(ORDEM-1)}H{ORDEM}h" #numChaves chaves filhos
TAMPAGINA: int = sys.getsizeof(fmtPagina)

class Chave:
    def __init__(self):
        self.id: int = NULO
        self.offset: int = NULO

class Pagina:
    def __init__(self):
        self.numChaves: int = 0
        self.chaves: list[Chave] = [Chave()] * (ORDEM - 1)
        self.filhos: list = [NULO] * ORDEM



def carregaPagina(arvore: io.BufferedRandom, rrn: int) -> Pagina:
    arvore.seek(rrn*TAMPAGINA + TAMCABECALHO, 0)
    buffer = struct.unpack(fmtPagina, arvore.read(TAMPAGINA))
    pag = Pagina()
    pag.numChaves = buffer[0]
    for i in range(ORDEM-1):
        pag.chaves[i] = Chave(buffer[(i*2)+1], buffer[(i*2)+2])
    pag.filhos = list(buffer[2*(ORDEM-1) + 1:])
    return pag


def escreveNaArvore(pag: Pagina, rrnAtual: int, arvore: io.BufferedRandom):
    arvore.seek(rrnAtual*TAMPAGINA +TAMCABECALHO, 0)
    arvore.write(struct.pack("H"), pag.numChaves)
    for i in range(ORDEM-1):
        arvore.write(struct.pack("HH", pag.chaves[i].id, pag.chaves[i].offset))
    for i in range(ORDEM):
        arvore.write(struct.pack("H", pag.filhos[i]))


def divide(chaveNova: Chave, filhoDpro: int, pagOrig: Pagina, pagRRN: int, arvore: io.BufferedRandom, posLista: int):
    # pagOrig = carregaPagina(arvore, pagRRN)
    
    listChaveTemp = pagOrig.chaves[:posLista]   + [chaveNova] + pagOrig.chaves[posLista:]
    listFilhoTemp = pagOrig.filhos[:posLista+1] + [filhoDpro] + pagOrig.filhos[posLista+1:]
    metade = ORDEM // 2
    pagOrig = Pagina()
    pagNova = Pagina()

    for i in range(metade):
        pagOrig.chaves[i] = listChaveTemp[i]
        pagOrig.numChaves += 1
        pagOrig.filhos[i] = listFilhoTemp[i]
    pagOrig.filhos[metade] = listFilhoTemp[metade]

    for i in range(metade+1, ORDEM):
        pagNova.chaves[i-metade-1] = listChaveTemp[i]
        pagNova.numChaves += 1
        pagNova.filhos[i-metade-1] = listFilhoTemp[i]
    pagNova.filhos[ORDEM-metade-1] = listFilhoTemp[ORDEM]

    escreveNaArvore(pagOrig, pagRRN, arvore)
    arvore.seek(0,2)
    fim = arvore.tell()
    rrnfim = ((fim-TAMCABECALHO)/TAMPAGINA) -1
    escreveNaArvore(pagNova, rrnfim, arvore)

    arvore.seek(0,0)

    chavePromovida = listChaveTemp[metade]
    rrnNovaPagina = rrnfim
    return chavePromovida, rrnNovaPagina


def insereNaArvore(chave: Chave, rrnAtual: int, arvore: io.BufferedRandom):
    if rrnAtual == NULO:
        return chave, NULO, True
    
    pag = carregaPagina(arvore, rrnAtual)
    achou, pos = buscaNaPagina(chave, pag)
    
    if achou:
        print("- Chave duplicada - Insercao interrompida.")
        return None, None, False
    
    chavePro, filhoDpro, promo = insereNaArvore(chave, pag.filhos[pos], arvore)

    if promo == False:
        return None, None, False
    
    if pag.numChaves < (ORDEM-1):
        pag.chaves = pag.chaves[:pos]   +  [chave]  + pag.chaves[pos:]
        pag.filhos = pag.filhos[:pos+1] +[filhoDpro]+ pag.filhos[pos+1:]
        pag.numChaves += 1
        escreveNaArvore(pag, rrnAtual, arvore)
        return None, None, False
    
    divide(chavePro, filhoDpro, pag, rrnAtual, arvore, pos)
    return chavePro, filhoDpro, True


def buscaNaPagina(chave: Chave, pag: Pagina):
    pos = 0
    while(pos < pag.numChaves and chave.id > pag.chaves[pos].id):
        pos += 1
    if pos < pag.numChaves and chave == pag.chaves[pos]:
        return True, pos
    else:
        return False, pos


def buscaNaArvore(chave: Chave, rrnAtual: int, arvore: io.BufferedRandom):
    if rrnAtual == None:
        return False, None, None
    else:
        pagina = carregaPagina(arvore, rrnAtual)
        achou, pos = buscaNaPagina(chave, pagina)
        if achou:
            return achou, rrnAtual, pos
        else:
            return buscaNaArvore(chave, pagina.filhos[pos], arvore)


def construir_indices():
    offset = 0
    arvoreB = open("btree.dat", "r+b")
    rrnRaiz = NULO
    arvoreB.write(struct.pack(fmtCabecalho, rrnRaiz))

    with open('games.dat', 'rb') as games:
        buffer = games.read(2)

        while buffer != b'':
            tam = int.from_bytes(buffer, "little")
            buffer = games.read(tam).decode()
            
            registro:list[str] = buffer.split("|", 1)
            indice = int(registro[0])

            chavePro, filhoDpro, promo = insereNaArvore(Chave(indice,offset), rrnRaiz, arvoreB)

            if promo:                           #raiz promoveu
                novaRaiz = Pagina()                                     #CRIA nova raiz
                novaRaiz.numChaves = 1
                novaRaiz.chaves[0] = chavePro
                novaRaiz.filhos[0] = rrnRaiz  
                novaRaiz.filhos[1] = filhoDpro

                arvoreB.seek(0,2)
                rrnRaiz = ((arvoreB.tell()-TAMCABECALHO)/TAMPAGINA)-1
                arvoreB.seek(0,0)           
                arvoreB.write(struct.pack(fmtCabecalho, rrnRaiz))       #ATUALIZA onde ta a raiz
                
                escreveNaArvore(novaRaiz, rrnRaiz, arvoreB)             #ESCREVE nova raiz
            offset += tam + 2

            buffer = games.read(2)

    arvoreB.close()
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

                pag = Pagina()
                registro = struct.unpack(fmtPagina, arvoreB.read(TAMPAGINA))
                pag.numChaves = registro[0]
                for j in range(ORDEM-1):
                    pag.chaves[j] = Chave(registro[(j*2)+1], registro[(j*2)+2])
                for j in range(ORDEM):
                    pag.filhos[j] = registro[(ORDEM * 2 - 1) + j]
                
                print("Página " + i + ":")
                print("Chaves : ")
                for i in pag.chaves:
                    print(i.id + " |", end="")
                print("Offsets : ")
                for i in pag.chaves:
                    print(i.offset + " |", end="")
                print("Offsets : ")
                for i in pag.filhos:
                    print(i + " |", end="")

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
