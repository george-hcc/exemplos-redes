# -*- coding: utf-8 -*-

# Importa módulo socket, que forma base das comunicações em rede em Python
import socket as sk

# Define número de porta do processo servidor
serverPort = 12000

# Cria soquete TCP do servidor
serverSocket = sk.socket(sk.AF_INET, sk.SOCK_STREAM) 
serverSocket.bind(('', serverPort)) 

# Servidor aguarda requisições de conexão TCP de cliente (parâmetro especifica número máximo de conexões em fila)
serverSocket.listen(10)

print('Servidor pronto para receber!')

while 1:
    
    # accept() aceita conexão com cliente e cria soquete provisório
    connectionSocket, addr = serverSocket.accept()
    
    # recv() recebe mensagem pelo soquete
    message = connectionSocket.recv(1024) 
    
    # Coloca string em maiúsculas
    modifiedMessage = message.decode('utf-8').upper()
    
    # send() envia mensagem modificada ao cliente pelo soquete
    connectionSocket.send(modifiedMessage.encode('utf-8'))
    
    # Fecha soquete provisório de conexão com cliente
    connectionSocket.close()
    
