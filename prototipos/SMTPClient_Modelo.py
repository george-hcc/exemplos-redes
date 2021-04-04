# -*- coding: utf-8 -*-

# Importa módulo socket, que forma base das comunicações em rede em Python
import socket as sk
# Importa módulo base64, que forma codifica mensagem texto em binário de 64 bits
import base64 as b64
# Importa módulo sst, que implementa camada de soquete de segurança (criptografia)
import ssl

# Define nome (ou IP) e número de porta do servidor SMTP
serverName = 'smtp.gmail.com'
serverPort = 587

# Lê mensagem a enviar digitada com teclado e atribui à variável message
message = input('Sentença de entrada (letras minúsculas):') + '\r\n.\r\n'

# Cria soquete TCP do cliente
clientSocket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

# Solicita estabelecimento de conexão com servidor
clientSocket.connect((serverName, serverPort))
recv = clientSocket.recv(1024) # Aguarda confirmação 220 do servidor
print(recv.decode('utf-8'))

# Envia mensagem HELO para servidor
clientSocket.send('HELO gmail.com\r\n'.encode('utf-8'))
recv = clientSocket.recv(1024) # Aguarda confirmação 250 do servidor
print(recv.decode('utf-8'))

# Inicia sessão TLS com servidor
clientSocket.send('STARTTLS\r\n'.encode('utf-8'))
recv = clientSocket.recv(1024) # Aguarda confirmação 220 do servidor
print(recv.decode('utf-8'))
	
# Cria soquete seguro e solicita login com servidor via sessão TLS
secureclientSocket = ssl.wrap_socket(clientSocket, ssl_version=ssl.PROTOCOL_SSLv23)
secureclientSocket.send('AUTH LOGIN\r\n'.encode('utf-8'))
recv = secureclientSocket.recv(1024) # Aguarda confirmação 334 do servidor
print(recv.decode('utf-8'))
	
# Envia nome de usuário ao servidor via sessão TLS
secureclientSocket.send(b64.b64encode('SEULOGIN@gmail.com'.encode('utf-8')) + '\r\n'.encode('utf-8'))
recv = secureclientSocket.recv(1024) # Aguarda confirmação 334 do servidor
print(recv.decode('utf-8'))

# Envia senha ao servidor via sessão TLS
secureclientSocket.send(SENHA + '\r\n'.encode('utf-8')) # Substitua SENHA pela código gerado por b64.b64encode('SUASENHA'.encode('utf-8'))
recv = secureclientSocket.recv(1024) # Aguarda confirmação 235 do servidor
print(recv.decode('utf-8'))

# Introduzir aqui códido do aluno

# Fecha soquete SSL do cliente
secureclientSocket.close()

# Fecha soquete do cliente
clientSocket.close()