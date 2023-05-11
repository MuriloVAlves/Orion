import numpy as np
matrizDecoder = np.array([[0x0,0xf,0x6,0xf],[0x7,0xf,0x1,0xf],[0xf,0x5,0xf,0x3],[0xf,0x2,0xf,0x4]])

def CriarBits(recebido):
    matriz = []
    for caractere in recebido:
        if caractere == "0":
            matriz.append(False)
        else:
            matriz.append(True)
    return np.array(matriz, dtype=bool)

def CriarByte(codigo):
    resposta = 0
    for i in range(0,len(codigo)):
        if codigo[i]:
            resposta += 0x1 << ((len(codigo)-1)-i)
    return resposta

def Viterbi(array):
    caminho = np.array([0x0,0x0,0x0,0x0])
    contador = 0
    iteracoes = 0
    buffer = [False,False,False]
    for i in range(0,len(array)):
        buffer[contador] = array[i]
        contador = contador + 1
        if contador > 2:
            codigo = CriarByte(buffer)
            caminho = Hamming(codigo,iteracoes,caminho)
            iteracoes = iteracoes + 1
            contador = 0
    return caminho
        
def HammingDist(a,b):
    distancia = 0
    for i in range(0,4):
        bit1 = a >> i & 0x1
        bit2 = b >> i & 0x1
        if bit1 != bit2:
            distancia = distancia + 1
    return distancia

def Hamming(comparador,iteracao,caminhoAnterior):
    contador = 0
    caminho = caminhoAnterior
    arrayPrincipal = np.array([0xF,0xF,0xF,0xF])
    arrayAuxiliar = np.array([0xF,0xF,0xF,0xF])
    if iteracao > 1:
        arrayParcial1 = np.array([0xF,0xF,0xF,0xF])
        arrayParcial2 = np.array([0xF,0xF,0xF,0xF])
        for i in range(0,len(matrizDecoder)):
            for j in range(0,len(matrizDecoder[0])):
                if matrizDecoder[i][j] != 0xf:
                    dist = HammingDist(comparador,matrizDecoder[i][j])
                    if contador < 4:
                        arrayPrincipal[contador] = dist
                    else:
                        arrayAuxiliar[contador-4] = dist
                    contador = contador + 1
        for n in range(0,len(caminho)):
            match n:
                case 0:
                    arrayParcial1[n] = arrayPrincipal[0] + caminho[0][(len(caminho[0]))-1]
                    arrayParcial2[n] = arrayPrincipal[2] + caminho[1][(len(caminho[0]))-1]
                case 1:
                    arrayParcial1[n] = arrayAuxiliar[0] + caminho[2][(len(caminho[0]))-1]
                    arrayParcial2[n] = arrayAuxiliar[2] + caminho[3][(len(caminho[0]))-1]
                case 2:
                    arrayParcial1[n] = arrayPrincipal[1] + caminho[0][(len(caminho[0]))-1]
                    arrayParcial2[n] = arrayPrincipal[3] + caminho[1][(len(caminho[0]))-1]
                case 3:
                    arrayParcial1[n] = arrayAuxiliar[1] + caminho[2][(len(caminho[0]))-1]
                    arrayParcial2[n] = arrayAuxiliar[3] + caminho[3][(len(caminho[0]))-1]
        menor = MenorDistancia(arrayParcial1,arrayParcial2)
        menor = menor.reshape(len(matrizDecoder[0]),1)
        caminho = np.concatenate((caminho, menor),axis=1)                
    elif iteracao == 0:
        for i in range(0,len(matrizDecoder[0])):
            if matrizDecoder[0][i] != 0xf:
                dist = HammingDist(comparador,matrizDecoder[0][i])
                arrayPrincipal[i] = dist
        menor = arrayPrincipal
        caminho = menor.reshape(len(matrizDecoder[0]),1)
    else:
        for i in range(0,2):
            for j in range(0,len(matrizDecoder[0])):
                if matrizDecoder[2*i][j] != 0xf:
                    dist = HammingDist(comparador,matrizDecoder[2*i][j])
                    arrayPrincipal[contador] = dist
                    contador = contador + 1
        menor = np.array([0xF,0xF,0xF,0xF])
        for n in range(0,len(caminho)):
            match n:
                case 0:
                    menor[n] = arrayPrincipal[0] + caminho[0][(len(caminho[0]))-1]
                case 1:
                    menor[n] = arrayPrincipal[2] + caminho[2][(len(caminho[0]))-1]
                case 2:
                    menor[n] = arrayPrincipal[1] + caminho[0][(len(caminho[0]))-1]
                case 3:
                    menor[n] = arrayPrincipal[3] + caminho[2][(len(caminho[0]))-1]
        menor = menor.reshape(len(matrizDecoder[0]),1)
        caminho = np.concatenate((caminho, menor),axis=1)
    return caminho

def MenorDistancia(a,b):
    menorHD = np.array([0xF,0xF,0xF,0xF])
    for i in range(0,len(a)):
        if a[i] <= b[i]:
            menorHD[i] = a[i]
        else :
            menorHD[i] = b[i]
    return menorHD

def Reverter(caminhoSobrevivente,tamanho):
    codigo = ""
    posicaoAnterior = 0
    primeiraRegresssao = True
    for i in range(tamanho-1, -1, -1):
        if (i-1) >= 0 and primeiraRegresssao == False:
            estadoPresente = np.array(caminhoSobrevivente[:,(i-1)])
            print(estadoPresente)
        else:
            if primeiraRegresssao:
                estadoFuturo = np.array(caminhoSobrevivente[:,i])
                estadoPresente = np.array(caminhoSobrevivente[:,(i-1)])
            else:
                estadoPresente = []
        posicaoAnterior = Retroceder(estadoFuturo,estadoPresente,posicaoAnterior,primeiraRegresssao)
        codigo = codigo + posicaoAnterior[1]
        posicaoAnterior = posicaoAnterior[0]
        primeiraRegresssao = False
    return codigo

def Retroceder(a,b,pAnt,regressao):
    posicao = 0
    posicaoAnterior = 0
    if regressao:
        duplo = False
        menorValor = 999999
        for i in range(0,4):
            if a[i] <= menorValor:
                if duplo:
                    print("Existem valores ambíguos")
                menorValor = a[i]
                posicao = i
                duplo = True
    else:
        posicao = pAnt
    '''---Retornando pontos da matriz e não realmente as posições---'''
    if len(b) != 0:
        match posicao:
            case 0:
                if b[0] < b[1]:
                    posicaoAnterior = b[0]
                elif b[0] > b[1]:
                    posicaoAnterior = b[1]
                else:
                    print("Existem valores ambíguos")
                    posicaoAnterior = b[0]
        
            case 1:
                if b[2] < b[3]:
                    posicaoAnterior = b[2]
                elif b[2] > b[3]:
                    posicaoAnterior = b[3]
                else:
                    print("Existem valores ambíguos")
                    posicaoAnterior = b[2]
            case 2:
                if b[0] < b[1]:
                    posicaoAnterior = b[0]
                elif b[0] > b[1]:
                    posicaoAnterior = b[1]
                else:
                    print("Existem valores ambíguos")
                    posicaoAnterior = b[0]

            case 3:
                if b[2] < b[3]:
                    posicaoAnterior = b[2]
                elif b[2] > b[3]:
                    posicaoAnterior = b[3]
                else:
                    print("Existem valores ambíguos")
                    posicaoAnterior = b[2]
    else:
        print("Fim da mensagem")
        print("Decodificando...")
    bitCodificado = DescobrirBit(posicao,posicaoAnterior)
    return posicaoAnterior, bitCodificado

def DescobrirBit(posicaoFinal,posicaoInicial):
    bitRetirado = ""
    match posicaoFinal:
        case 0:
            if posicaoInicial == 0:
                bitRetirado = "0"
            else:
                bitRetirado = "1"
        case 1:
            if posicaoInicial == 2:
                bitRetirado = "0"
            else:
                bitRetirado = "1"
        case 2:
            if posicaoInicial == 0:
                bitRetirado = "0"
            else:
                bitRetirado = "1"
        case 3:
            if posicaoInicial == 2:
                bitRetirado = "0"
            else:
                bitRetirado = "1"
    return bitRetirado

def CriarChar(bits):
    resposta = ""
    for i in range(0,(len(bits)//8)):
        buffer = 0
        for j in range(0,8):
            if bits[j+(i*8)]:
                buffer += 0x1 << j
        resposta = resposta + chr(buffer)
    resposta = resposta [::-1]
    return resposta

'''
Antiga função retroceder

def Retroceder(a,b,pAnt,regressao):
posicao = 0
posicaoAnterior = 0
if regressao:
    duplo = False
    menorValor = 999999
    for i in range(0,4):
        if a[i] <= menorValor:
            if duplo:
                print("Existem valores ambíguos")
            menorValor = a[i]
            posicao = i
            duplo = True
else:
    posicao = pAnt
if len(b) != 0:
    match posicao:
        case 0:
            if b[0] < b[1]:
                posicaoAnterior = b[0]
            elif b[0] > b[1]:
                posicaoAnterior = b[1]
            else:
                print("Existem valores ambíguos")
                posicaoAnterior = b[0]
        
        case 1:
            if b[2] < b[3]:
                posicaoAnterior = b[2]
            elif b[2] > b[3]:
                posicaoAnterior = b[3]
            else:
                print("Existem valores ambíguos")
                posicaoAnterior = b[2]
        case 2:
            if b[0] < b[1]:
                posicaoAnterior = b[0]
            elif b[0] > b[1]:
                posicaoAnterior = b[1]
            else:
                print("Existem valores ambíguos")
                posicaoAnterior = b[0]

        case 3:
            if b[2] < b[3]:
                posicaoAnterior = b[2]
            elif b[2] > b[3]:
                posicaoAnterior = b[3]
            else:
                print("Existem valores ambíguos")
                posicaoAnterior = b[2]
else:
    print("Fim da mensagem")
    print("Decodificando...")
bitCodificado = DescobrirBit(posicao,posicaoAnterior)
return posicaoAnterior, bitCodificado
'''