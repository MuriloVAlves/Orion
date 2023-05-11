#define CRC_POLI 0x1021
bool CRC[sizeof(CRC_POLI) * 4];
void ClearBuffer() {
  //Essa função serve para limpar o comando "\n" do final da mensagem serial
  delay(50);
  byte trash[Serial.available()];
  Serial.readBytes(trash, Serial.available());
}
void CreateCRC(uint32_t polinomio) {
  //Cria um vetor com o polinômio fornecido
  uint32_t verifier = pow(2, ((sizeof(polinomio) * 4) - 1));
  for (byte j = 0; j < (sizeof(CRC)); j++) {
    if (polinomio & (verifier >> j)) {
      CRC[j] = 1;
    }
    else {
      CRC[j] = 0;
    }
  }
}
/******************************Função de conversão******************************/
void Convert(char *mensagem, int tamanho, boolean *resposta ) {

  uint16_t tamanhoCRC = (8 * tamanho) + (sizeof(CRC));
  boolean CRCConvert[tamanhoCRC];
  //Iniciar a transferência da mensagem para o array
  for (int i = 0; i < tamanho; i++) {
    byte caractere = mensagem[i];
    for (int j = 0; j < 8; j++) {
      int posicao = (8 * i) + j;
      if ((caractere & (0x80 >> j))) {
        CRCConvert[posicao] = 1;
      }
      else {
        CRCConvert[posicao] = 0;
      }
    }
    //Limpar o resto do array para evitar valores flutuantes
    for (int k = (8 * tamanho); k < tamanhoCRC; k++) {
      CRCConvert[k] = 0;
    }
    //Começar a sequência de CRC
    //Copiar a array de mensagem para um buffer
    boolean buff[tamanhoCRC];
    for (int i = 0; i < tamanhoCRC; i++) {
      buff[i] = CRCConvert[i];
    }
    for (int pos = 0; pos < (8 * tamanho); pos++) {
      if (buff[pos]) {
        buff[pos] = !(buff[pos]);
        for (int j = 0; j < sizeof(CRC); j++) {
          buff[(pos + j + 1)] = ((buff[pos + j + 1]) ^ (CRC[j]));
        }
      }
    }
    //transferir o valor do CRC para o array com a mensagem
    for (int k = (8 * tamanho); k < tamanhoCRC; k++) {
      CRCConvert[k] = buff[k];
    }
    //Retornar os valores para o array de resposta
    for (int k = 0; k < tamanhoCRC; k++) {
      resposta[k] = CRCConvert[k];
    }
  }
}
/******************************Função de desconversão******************************/
boolean Deconvert(char *mensagem, int tamanho, char * resposta) {
  int tamanhoR = (((tamanho)-(sizeof(CRC)))/8);
  boolean CRCDeconvert[tamanho];
  //Iniciar a transferência da mensagem para o array
  for (int i = 0; i < tamanho; i++) {
    char caractere = mensagem[i];
    if (caractere == '1') {
      CRCDeconvert[i] = 1;
    }
    else {
      CRCDeconvert[i] = 0;
    }
  }
  //Começar a sequência de CRC
  //Copiar a array de mensagem para um buffer
  boolean buff[tamanho];
  for (int i = 0; i < tamanho; i++) {
    buff[i] = CRCDeconvert[i];
  }
  for (int pos = 0; pos < (tamanho-sizeof(CRC)); pos++) {
    if (buff[pos]) {
      buff[pos] = !(buff[pos]);
      for (int j = 0; j < sizeof(CRC); j++) {
        buff[(pos + j + 1)] = ((buff[pos + j + 1]) ^ (CRC[j]));
      }
    }
  }
  //verificar o valor do CRC
  boolean verificar = 0;
  for (int k = (tamanho-sizeof(CRC)); k < tamanho; k++) {
    if (buff[k]) {
      verificar = 1;
    }
  }
  if (verificar == 1) {
    return verificar;
  }
  else {
    for (int k = 0; k < tamanhoR; k++) {
      byte caractere = 0;
      for (int c = 0; c < 8; c++) {
        if (CRCDeconvert[((8 * k) + c)]) {
          caractere += 0x80 >> c;
        }
      }
      resposta[k] = ((char) caractere);
    }
    return verificar;
  }
  return 0;
}
void setup() {
  Serial.begin(115200);
  delay(100);
  while (!Serial) {

  }
  Serial.println("Serial conectado");
  Serial.flush();
  CreateCRC(CRC_POLI);
}

void loop() {
  if (Serial.available() > 0) {
    delay(50);
    int byteRecebido = 0;
    byteRecebido = Serial.read();
    ClearBuffer();
    //Calcular o CRC
    if (byteRecebido == 114) {
      Serial.println("Iniciando CRC");
      Serial.print("Digite a mensagem \n");
      Serial.print("Esperando");
      while (Serial.available() == 0) {
        Serial.print(".");
        delay(1000);
      }
      Serial.println();
      delay(100);
      uint8_t tamanho = Serial.available();
      char mensagem[(tamanho - 1)];
      Serial.readBytesUntil(0b1010, mensagem, tamanho);
      boolean resultado[((8 * tamanho) + (sizeof(CRC)))];
      Convert(mensagem, sizeof(mensagem), resultado);
      for (int i = 0; i < ((sizeof(mensagem) * 8) + sizeof(CRC)); i++) {
        //Serial.write(resultado[i]);
        Serial.print(resultado[i]);
      }
      Serial.print("\n");
      Serial.flush();

    }
    //Verificar a mensagem
    else if (byteRecebido == 100) {
      Serial.println("Iniciando decodificação do CRC");
      Serial.print("Digite a mensagem \n");
      Serial.print("Esperando");
      while (Serial.available() == 0) {
        Serial.print(".");
        delay(1000);
      }
      Serial.println();
      uint8_t tamanho = Serial.available();
      char mensagem[(tamanho - 1)];
      Serial.readBytesUntil(0b1010, mensagem, tamanho);
      char resposta[(((tamanho-1)-(sizeof(CRC)))/8)];
      boolean falhas = Deconvert(mensagem, sizeof(mensagem), resposta);
      if(falhas){
        Serial.println("Erro na conversão");
      }
      else
      {
        for(int i = 0; i < sizeof(resposta); i++){
          Serial.print(resposta[i]);
        }
        Serial.println();
      }
    }
    else if (byteRecebido == 91) {
      Serial.println("Bye");
      Serial.end();
    }
    else {
      Serial.println(byteRecebido, BIN);
    }
  }
}
