#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Name: Mini-Cliente SMTP Gmail
#Author: George Camboim - george.camboim@ee.ufcg.edu.br
#Date: 04/04/2021
#Description:
#    Esse cliente faz poucas checagens em cima dos dados inseridos pelo usuário.
#    Caso a requisição não tenha sucesso, não foi implementado mecanismos de controle
#    para tentar novamente. Se o email do usuário estiver configurado corretamente e
#    as informações de login fornecidas também, o programa irá funcionar.

import socket as sk
import base64 as b64
import ssl
from getpass import getpass

server_name = 'smtp.gmail.com'
server_port = 587

def is_valid_mail(mail, login=False):
    if mail.count('@') != 1:
        print('>Isso não aparenta ser um email...')
        return False
    if login:
        _, domain = mail.split('@')
        if domain != 'gmail.com':
            print('>Seu email de login deve estar em @gmail.com')
            return False
    return True


def send_mail(login_mail, password, to_mail, data):
    ################
    print('>Criando soquete e fazendo comunicação inicial.')
    clientSocket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    clientSocket.connect((server_name, server_port))
    recv = clientSocket.recv(1024) # Aguarda confirmação 220 do servidor
    print(recv.decode('utf-8'))

    clientSocket.send('HELO gmail.com\r\n'.encode('utf-8'))
    recv = clientSocket.recv(1024) # Aguarda confirmação 250 do servidor
    print(recv.decode('utf-8'))

    ################
    print('>Iniciando sessão TLS com servidor e solicitando login.')
    clientSocket.send('STARTTLS\r\n'.encode('utf-8'))
    recv = clientSocket.recv(1024) # Aguarda confirmação 220 do servidor
    print(recv.decode('utf-8'))

    secureclientSocket = ssl.wrap_socket(clientSocket, ssl_version=ssl.PROTOCOL_SSLv23)
    secureclientSocket.send('AUTH PLAIN\r\n'.encode('utf-8'))
    recv = secureclientSocket.recv(1024) # Aguarda confirmação 334 do servidor
    print(recv.decode('utf-8'))

    ################
    print('>Enviando nome de usuário ao servidor via sessão TLS')
    secureclientSocket.send(b64.b64encode(('\00'+login_mail+'\00'+password).encode('utf-8')) \
                            + '\r\n'.encode('utf-8'))
    recv = secureclientSocket.recv(1024) # Aguarda confirmação 235 do servidor
    print(recv.decode('utf-8'))

    secureclientSocket.send(('MAIL FROM: <'+login_mail+'>\r\n').encode('utf-8'))
    recv = secureclientSocket.recv(1024) # Aguarda confirmação 250 do servidor
    print(recv.decode('utf-8'))

    secureclientSocket.send(('RCPT TO: <'+to_mail+'>\r\n').encode('utf-8'))
    recv = secureclientSocket.recv(1024) # Aguarda confirmação 250 do servidor
    print(recv.decode('utf-8'))

    secureclientSocket.send('DATA\r\n'.encode('utf-8'))
    recv = secureclientSocket.recv(1024) # Aguarda confirmação 354 do servidor
    print(recv.decode('utf-8'))

    secureclientSocket.send(data.encode('utf-8'))
    recv = secureclientSocket.recv(1024) # Aguarda confirmação 250 do servidor
    print(recv.decode('utf-8'))

    ################
    print('>Fechando sessão, TSL e soquete de conexão.')
    secureclientSocket.send('QUIT\r\n'.encode('utf-8'))
    recv = secureclientSocket.recv(1024) # Aguarda confirmação 221 do servidor
    print(recv.decode('utf-8'))

    secureclientSocket.close()
    clientSocket.close()


def main():
    print('>Cliente SMTP de testes do Gmail.')

    while True:
        login_mail = input('>Digite seu login: ')
        if is_valid_mail(login_mail, login=True):
            print('>Email aceito!')
            break

    password = getpass('>Digite sua senha: ')

    while True:
        to_mail = input('>Digite o email destinatário: ')
        if is_valid_mail(to_mail):
            print('>Destinatário aceito!')
            break

    subject = input('>Digite o assunto: ')

    message = input('>Digite a mensagem: ')

    data = 'Subject: '+subject+'\r\n\r\n'
    data+= message+'\r\n'
    data+='.\r\n'

    send_mail(login_mail, password, to_mail, data)


if __name__ == '__main__':
    main()
