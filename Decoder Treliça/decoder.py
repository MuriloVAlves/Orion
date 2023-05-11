import functions as decoder
import time as timer
import serial as serial

Serial = serial.Serial()
Serial.baudrate = 115200
Serial.port = 'COM4'
Serial.setRTS(False)
Serial.setDTR(False)
Serial.open()
print(Serial)
mensagem = ""
Serial.reset_input_buffer()
Serial.reset_output_buffer()
while Serial.isOpen():
    if Serial.in_waiting:
        recebido = Serial.readline()
        print(recebido)
    fala = input("O que você quer fazer?(Enviar/Sair): ")
    if fala ==  "Sair":
        Serial.write(b"[")
        Serial.close() 
    elif fala == "Enviar":
        resposta = b""
        Serial.write(b"r")
        mensagem = input("Digite sua mensagem: ")
        mensagem = bytes(mensagem,'utf-8')
        mensagem = mensagem + b"\n"
        Serial.write(mensagem)
        Serial.flush()
        espera = True
        print("Espere...")
        timer.sleep(1)
        while Serial.inWaiting():
            resposta = resposta + Serial.readline(1)
        resposta = resposta.decode('ascii')
        print("Recebido: ")
        print(resposta)
        print("Criando caminho...")
        i = decoder.CriarBits(resposta)
        caminho = decoder.Viterbi(i)
        print(caminho)
        print(len(caminho[0]),"bits recebidos")
        s = decoder.Reverter(caminho,len(caminho[0]))
        s = decoder.CriarBits(s.removeprefix("00"))
        s = decoder.CriarChar(s)
        print(s)