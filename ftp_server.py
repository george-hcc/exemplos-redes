#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-Name: Mini-Servidor FTP
#-Author: George Camboim - george.camboim@ee.ufcg.edu.br
#-Date: 03/04/2021
#-Description:
#    Servidor FTP testado em ambiente linux com o cliente ftp padrão do unix.
#    O tipo de transferência A (ascii) é instável no momento. O uso de sudo é
#    necessário para que o binding com as portas protegidas 20 e 21 seja possível.
#    Executar com sudo permite que o script acesse todos os arquivos do sistema
#    operacional, o que no estado atual é um possível falha de segurança.

import socket as sk
import os

# Configurações de servidor
SERVER_ADDR = '127.0.0.1'
CTRL_PORT = 21
DATA_PORT = 20
BUFF_SIZE = 1024

class FTP_connection:

    VALID_VERBS = ['USER',
                   'SYST',
                   'TYPE',
                   'PORT',
                   'STOR',
                   'RETR',
                   'QUIT',]


    def __init__(self, ctrl_socket):
        self.server_ctrl_sk = ctrl_socket
        (client_sk, client_addr) = ctrl_socket.accept()

        self.client_ctrl_sk = client_sk
        self.client_ctrl_addr = client_addr
        self.client_data_addr = None

        self.user_logged = False
        self.connection_closed = False
        self.type_flag = 'I'

        self.PROC_DICT = {'USER': self.USER_proc,
                          'SYST': self.SYST_proc,
                          'TYPE': self.TYPE_proc,
                          'PORT': self.PORT_proc,
                          'STOR': self.STOR_proc,
                          'RETR': self.RETR_proc,
                          'QUIT': self.QUIT_proc,}


    def connection_loop(self):
        print('##################################')
        print('O endereço', self.client_ctrl_addr, 'conectou-se ao servidor')
        print('Conexão cliente-servidor criada.')
        self.send_welcome_msg()

        # Loop do soquete de controle
        while not self.connection_closed:
            (req_verb, *req_param) = self.client_ctrl_sk.recv(BUFF_SIZE).decode('utf-8').split()
            print('<RECEBENDO:', ' '.join([req_verb] + req_param))
            if req_verb in self.VALID_VERBS:
                self.connection_closed = self.PROC_DICT[req_verb](req_param)
            else:
                self.connection_closed = self.except_proc()

        self.close_connection()


    def send_welcome_msg(self):
        welcome_msg = '220-Servidor FTP de testes PRONTO.\n'
        welcome_msg +='220-Somente acessos com usuário "anonymous" serão aceitos.\n'
        welcome_msg +='220-Senhas não serão pedidas.\n'
        welcome_msg +='220-Os comandos válidos nesse servidor são:\n'
        welcome_msg +='220 (' + ', '.join(self.VALID_VERBS) +')\n'
        self.send_payload(self.client_ctrl_sk, welcome_msg.encode('utf-8'))


    def USER_proc(self, req_param):
        if self.user_logged:
            self.send_payload(self.client_ctrl_sk,
                              '530 Mudança de usuário não permitida.\n'.encode('utf-8'))
        else:
            if req_param == ['anonymous']:
                self.user_logged = True
                self.send_payload(self.client_ctrl_sk,
                                  '230 Login realizado com sucesso!\n'.encode('utf-8'))
            else:
                self.send_payload(self.client_ctrl_sk,
                                  '530 Usuário inválido (tente "anonymous").\n'.encode('utf-8'))

        return False


    def SYST_proc(self, req_param):
        self.send_payload(self.client_ctrl_sk,
                          '215 UNIX Type: L8\n'.encode('utf-8'))
        return False


    def TYPE_proc(self, req_param):
        if req_param == []:
            if self.type_flag == 'A':
                self.send_payload(self.client_ctrl_sk,
                                  '211 Ascii\n'.encode('utf-8'))
            elif self.type_flag == 'I':
                self.send_payload(self.client_ctrl_sk,
                                  '211 Binário\n'.encode('utf-8'))
        elif req_param == ['A']:
            self.type_flag = 'A'
            self.send_payload(self.client_ctrl_sk,
                              '200 Novo modo de transferência: Ascii.\n'.encode('utf-8'))
        elif req_param == ['I'] or req_param == ['L', '8']:
            self.type_flag = 'I'
            self.send_payload(self.client_ctrl_sk,
                              '200 Novo modo de transferência: Binário.\n'.encode('utf-8'))
        else:
            self.send_payload(self.client_ctrl_sk,
                              '504 Tipo não implementado.\n'.encode('utf-8'))
        return False


    def PORT_proc(self, req_param):
        # Usuário não-logado
        if not self.user_logged:
            self.send_payload(self.client_ctrl_sk,
                              '530 Login é necessário para este comando.\n'.encode('utf-8'))
            return False

        # Memórizando endereço de comunicação do futuro soquete de dados
        param = req_param[0].split(',')
        addr = '.'.join(param[:4])
        port = 256*int(param[4]) + int(param[5])
        self.client_data_addr = (addr, port)
        self.send_payload(self.client_ctrl_sk,
                          ('200 Memorizado o endereço '+addr+':'+str(port)+'.\n').encode('utf-8'))
        return False


    def STOR_proc(self, req_param):
        # Usuário não-logado
        if not self.user_logged:
            self.send_payload(self.client_ctrl_sk,
                              '530 Login é necessário para este comando.\n'.encode('utf-8'))
            return False

        # Usuário não configurou porta de dados
        if not self.client_data_addr:
            msg = '503-Sequência de comandos não permitida.\n'
            msg +='503 O uso prévio do verbo PORT é necessário para permitir o uso do STOR.\n'
            self.send_payload(self.client_ctrl_sk, msg.encode('utf-8'))
            return False

        # Já existe arquivo com nome proposto
        if os.path.exists(req_param[0]):
            self.send_payload(self.client_ctrl_sk,
                              '553 Nome do arquivo não permitido.\n'.encode('utf-8'))
            return False

        # Controlando conexão e transferindo arquivo
        self.send_payload(self.client_ctrl_sk,
                          ('125 Abrindo canal de dados para receber transferência.\n"'
                           + req_param[0] + '".\n').encode('utf-8'))
        data_sk = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        data_sk.connect(self.client_data_addr)
        total_data = b''
        while True:
            partial_data = data_sk.recv(BUFF_SIZE)
            total_data += partial_data
            if len(partial_data) < BUFF_SIZE:
                break
        data_sk.close()

        # Procedimento de armazenamento de arquivo no servidor
        #####
        # Dentro dos testes que realizei com o cliente ftp padrão do unix,
        # a transferência de arquivo estava sendo vista como sucesso uma vez
        # que detectou a transferência do arquivo e fechamento da conexão
        # realizada. Qualquer mensagem enviada dentro desse try-except estava
        # sendo ignorada. Desisti de tentar forçar qualquer tipo de confirmação.
        #####
        try:
            with open(req_param[0], 'wb') as f:
                f.write(total_data)
            print('Arquivo "'+req_param[0]+'" recebido e armazenado com sucesso.')
        except IOError:
            print('###ERRO GRAVISSIMO NA ESCRITA DE ARQUIVO###')

        self.client_data_addr = None
        return False


    def RETR_proc(self, req_param):
        # Usuário não-logado
        if not self.user_logged:
            self.send_payload(self.client_ctrl_sk,
                              '530 Login é necessário para este comando.\n'.encode('utf-8'))
            return False

        # Usuário não configurou porta de dados
        if not self.client_data_addr:
            msg = '503-Sequência de comandos não permitida.\n'
            msg +='503 O uso prévio do verbo PORT é necessário para permitir o uso do STOR.\n'
            self.send_payload(self.client_ctrl_sk, msg.encode('utf-8'))
            return False

        # Procedimento de leitura de arquivo
        try:
            with open(req_param[0], 'rb') as f:
                file_data = f.read()
        except IsADirectoryError:
            self.send_payload(self.client_ctrl_sk,
                              '550 Arquivo requisitado é um diretório.\n'.encode('utf-8'))
            return False
        except FileNotFoundError:
            self.send_payload(self.client_ctrl_sk,
                              '550 Arquivo não encontrado.\n'.encode('utf-8'))
            return False
        except PermissionError:
            self.send_payload(self.client_ctrl_sk,
                              '550 Sem permissão de leitura de arquivo.\n'.encode('utf-8'))
            return False

        # Controlando conexão e transferindo arquivo
        self.send_payload(self.client_ctrl_sk,
                          ('125 Abrindo canal de dados para enviar transferência.\n"'
                           + req_param[0] + '".\n').encode('utf-8'))
        data_sk = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        data_sk.connect(self.client_data_addr)
        self.send_payload(data_sk, file_data, False)
        print('Arquivo "'+req_param[0]+'" enviado com sucesso.')
        data_sk.close()

        self.client_data_addr = None
        return False


    def QUIT_proc(self, req_param):
        self.send_payload(self.client_ctrl_sk,
                          '221 Adeus.\n'.encode('utf-8'))
        return True


    def except_proc(self):
        self.send_payload(self.client_ctrl_sk,
                          '502 Comando não implementado\n'.encode('utf-8'))
        return False


    def close_connection(self):
        self.client_ctrl_sk.close()


    def send_payload(self, client_sk, payload, print_flag=True):
        if print_flag:
            print('>ENVIANDO: "', payload, '"', sep='')
        while payload:
            n = client_sk.send(payload)
            payload = payload[n:]


def main():
    with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as ctrl_socket:
        ctrl_socket.bind((SERVER_ADDR, CTRL_PORT))
        ctrl_socket.listen(10)
        print('Servidor pronto para receber!')

        while 1:
            ftp_obj = FTP_connection(ctrl_socket)
            ftp_obj.connection_loop()
            del ftp_obj

if __name__ == '__main__':
    main()
