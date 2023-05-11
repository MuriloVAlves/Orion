#define LED 2
//Função para limpar o buffer serial
void ClearBuffer() {
  //Essa função serve para limpar o comando "\n" do final da mensagem serial
  delay(50);
  byte trash[Serial.available()];
  Serial.readBytes(trash, Serial.available());
}
//Função para atuar como shift register
byte Shift(boolean proximo, byte cadeia){
  byte shift = 0;
  shift = cadeia >> 1;
  proximo == 1 ? shift += 0b100 : shift = shift;
  return shift;
}
//Função para enviar dados
void Send (byte registrador){
  //Criar o parâmetro de resposta
        byte resposta = 0;
        byte resp0 = 0, resp1 = 0, resp2 = 0;
        for (byte k = 0; k < 3; k++){
          if(registrador & (0b100 >> k)){
            resp0++;
            if(k == 0){
              resp1++;
            }
            else if(k == 1){
              resp2++;
            }
            else{
              resp1++;
              resp2++; 
            }
          }
        }
        resposta += resp0%2 <<2;
        resposta += resp1%2 << 1;
        resposta += resp2%2;
        for (byte k =0; k < 3; k++){
          if(resposta & (0b100 >> k)){
            Serial.print("1");
          }
          else{
            Serial.print("0");
          }
        }
}
//Função para criar os bits de paridade
void Codificar (char *mensagem, byte tamanhoMensagem){
  byte shiftRegister = 0;
  char caractere;
  for(byte i = 0; i < tamanhoMensagem; i++){
     caractere = mensagem[i];
     //criar o dado e os bits de verificação
     for (int j = 0; j < 8; j++) {
        shiftRegister = Shift((caractere & (0x80 >> j)), shiftRegister);
        Send(shiftRegister);
      }
  }
  //Terminar de enviar dados do Shift Register
  for(int rest = 0; rest < 3; rest++){
    shiftRegister = Shift(0,shiftRegister);
    Send(shiftRegister);
  }
  Serial.print("\n");
  Serial.flush();
}

void setup() {
  pinMode(LED,OUTPUT);
  Serial.begin(115200);
  delay(100);
  while (!Serial) {

  }
  ClearBuffer();
}

void loop() {
  if (Serial.available() > 0) {
    delay(100);
    char byteRecebido = 0;
    byteRecebido = Serial.read();
    //Calcular o CRC
    if (byteRecebido == 114) {
      digitalWrite(LED,HIGH);
      ClearBuffer();
      while(Serial.available() == 0){
        delay(50);
      }
      delay(100);
      uint8_t tamanho = Serial.available();
      char mensagem[(tamanho - 1)];
      Serial.readBytesUntil(0b1010, mensagem, tamanho);
      Codificar(mensagem, sizeof(mensagem));
      digitalWrite(LED,LOW);
    }
    else if (byteRecebido == 91) {
      ESP.restart();
    }
    else {
      Serial.println(byteRecebido, BIN);
      ClearBuffer();
    }
  }
}
