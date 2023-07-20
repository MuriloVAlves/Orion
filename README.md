# Orion
Códigos de comunicação do projeto Orion
Este repositório é um teste de conceito de algoritmos de detecção e correção de erros para o projeto Orion do IEEE UFABC.
Os arquivos consistem em um sistema para o cálculo do CRC em um Arduino e um decoder de treliça baseado no algoritmo de Viterbi.
O CRC foi utilizado no projeto como uma tentativa inicial de usar um algoritmo de detecção de erros, mas pela questão energética, decidimos partir para um algoritmo mais confiável para a transmissão.
Para isso, seguimos para o algoritmo de treliça. Existe um código para um ESP32 que simula o comportamento de um registrador que converteria a mensagem para o algoritmo e enviaria ela para a estação de solo. O código do decoder foi escrito em Python, mas de uma forma que facilitaria a conversão para outras linguagens. Esse código do decodificador envia uma mensagem para o ESP converter, recebe a mensagem que foi passada pelo algoritmo, e inicia o processo de desconversão, tentando chegar à resposta inicial.
O código do teste do decoder aplica algumas alterações aleatórias, com a chance de inverter um bit da mensagem em 1/n (com n definido no programa). Esse código está sendo utilizado para determinar a eficiência do algoritmo em detectar e corrigir os erros, além de encontrar novas formas de melhorar o código.

A FAZER:
Tentar diminuir o tamanho do caractere - Atualmente está utilizando o código ASCII, utilizando 8 bits por caracter. Isso pode ser um problema pela questão energética do transmissor.
Caso continue usando o código ASCII, fazer alguma forma de delimitar mais corretamente se o caractere é letra, número ou espaço - Parte dos caracteres são "quebrados" por perderem a parte inicial do código que define o caractere. Ao resolver isso, pode até ocorrer de ter um caractere trocado na mensagem, mas não teria mais caracteres não representáveis.
Trabalhar em questões de bits não recebidos - Isso pode acabar quebrando todo o resto da mensagem, o que pode criar um grande problema para o projeto. Talvez utilizando o CRC, podemos confirmar se a mensagem foi recebida corretamente ou não. Essa área precisa de mais pesquisas.
