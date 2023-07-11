import os
import re

#caminho ao diretorio de turmas
def gerar_path_turmas():
    return os.getcwd()+"/../codigosAlunos/"


#caminho ao diretorio de trabalhos
def gerar_path_trabalhos_turma(nome_turma):
    return os.getcwd()+"/../codigosAlunos/"+nome_turma+ "/"

# verifica se existe uma determinada turma
def existe_turma (nome_turma):
    path = gerar_path_turmas()
    lista = os.listdir(path)
    for pasta in lista:
        if pasta == nome_turma:
            return True
    return False

# verifica se existe determinado trabalho em uma turma
def existe_trabalho_turma (nome_trabalho, nome_turma):
    if existe_turma(nome_turma):
        path = gerar_path_trabalhos_turma(nome_turma)
        lista = os.listdir(path)
        for pasta in lista:
            if pasta == nome_trabalho:
                return True
    return False

# verifica se existe determinado código em um trabalho e turma
def existe_arquivo_trabalho (nome_trabalho, nome_turma, nome_arquivo):
    if existe_trabalho_turma(nome_trabalho, nome_turma):
        path = gerar_path_trabalhos_turma(nome_turma) + nome_trabalho + "/"
        lista = os.listdir(path)
        for arquivo in lista:
            if arquivo == nome_arquivo:
                return True
    return False




# cria uma pasta referente a uma nova turma, sucesso: True, se já existir com esse nome: False
# TODO validar as strings de entrada para não permitir caracteris que não podem ser usados em nome de pasta
def criar_turma (nome):
    path = gerar_path_turmas()
    lista = os.listdir(path)
    for pasta in lista:
        if pasta == nome:
            print ("Turma já existe:", nome)
            return False
    fp = os.popen("mkdir "+path+nome)
    fp.close()
    return True

# cria uma pasta referente a um novo trabalho, sucesso: True, se já existir com esse nome ou não existir a turma: False
def criar_trabalho_turma (nome_trabalho, nome_turma):
    if existe_turma(nome_turma) == False:
        return False
    
    path = gerar_path_trabalhos_turma(nome_turma)
    lista = os.listdir(path)
    for pasta in lista:
        if pasta == nome_trabalho:
            print ("Trabalho já existe:", nome_trabalho)
            return False
    fp = os.popen("mkdir " + path + nome_trabalho)
    fp.close()
    return True


# retorna a lista de pastas referentes a turmas
def listar_turmas ():
    path = gerar_path_turmas()
    lista = os.listdir(path)
    #print (lista)
    #print (len(lista))
    return lista

# retorna a lista de pastas referentes aos trabalhos
def listar_trabalhos_turma (nome_turma):
    if existe_turma(nome_turma) == False:
        return []
    path = gerar_path_trabalhos_turma(nome_turma)
    lista = os.listdir(path)
    return lista


# exclui o diretório de uma turma, sucesso: True, se não existir com esse nome: False
def apagar_turma (nome):
    path = gerar_path_turmas()
    lista = os.listdir(path)
    for pasta in lista:
        if pasta == nome:
            fp = os.popen("rm -rf "+path+nome)
            fp.close()
            return True
    print("Turma não existe:", nome)
    return False

# exclui o diretório de um trabalho, sucesso: True, se não existir com esse nome, ou não existir a turma: False
def apagar_trabalho_turma (nome_trabalho, nome_turma):
    if existe_turma(nome_turma) == False:
        return False
    path = gerar_path_trabalhos_turma(nome_turma)
    lista = os.listdir(path)
    for pasta in lista:
        if pasta == nome_trabalho:
            fp = os.popen("rm -rf " + path + nome_trabalho)
            fp.close()
            return True
    print("Trabalho não existe:", nome_trabalho)
    return False

#retorna uma lista com os arquivos dentro de um determinado trabalho
def listar_codigos_trabalho (nome_trabalho, nome_turma):
    if existe_trabalho_turma (nome_trabalho, nome_turma) == False:
        return []
    
    path = gerar_path_trabalhos_turma(nome_turma) + nome_trabalho + "/"
    lista = os.listdir(path)
    return lista


#retorna o conteudo de um determinado arquivo
def ler_codigo_trabalho (nome_arquivo, nome_trabalho, nome_turma):
    if existe_trabalho_turma (nome_trabalho, nome_turma) == False:
        return

    path = gerar_path_trabalhos_turma(nome_turma) + nome_trabalho + "/"
    
    arq = open(path + nome_arquivo, 'r')
    conteudo = ""
    for line in arq:
        line = line.replace("&","&amp;")
        line = line.replace("<","&lt;")
        line = line.replace(">","&gt;")
        conteudo+=line
    
    arq.close()
    return conteudo

#retorna o numero de linhas de código de um trabalho
def conta_linhas_codigo (nome_trabalho, nome_turma, nome_arquivo):
    path = gerar_path_trabalhos_turma(nome_turma) + nome_trabalho + "/"
    arq = open(path + nome_arquivo, 'r')
    num = sum(1 for line in arq)
    arq.close()
    return num

def escreve_codigo_trabalho(nome_arquivo, nome_trabalho, nome_turma, conteudo):
    if existe_trabalho_turma (nome_trabalho, nome_turma) == False:
        return

    path = gerar_path_trabalhos_turma(nome_turma) + nome_trabalho + "/"
    arq = open(path + nome_arquivo, 'w')
    arq.write(conteudo)
    arq.close()
    return
    

def verifica_existe_pasta_jplag(nome_trabalho, nome_turma):
    path = os.getcwd()+"/../logsferramentas/jplag/"
    lista = os.listdir(path)
    for pasta in lista:
        if pasta == nome_turma+ "-"+nome_trabalho:
            return True
    return False

def apagar_pasta_jplag(nome_trabalho, nome_turma):
    path = os.getcwd()+"/../logsferramentas/jplag/"
    fp = os.popen("rm -rf " + path + nome_turma + "-" + nome_trabalho)
    fp.close()

def verifica_existe_arquivo_moss(nome_trabalho, nome_turma):
    path = os.getcwd()+"/../logsferramentas/"
    lista = os.listdir(path)
    for arquivo in lista:
        if arquivo == "moss-"+nome_turma+ "-"+nome_trabalho+ ".log":
            return True
    return False

def apagar_arquivo_moss(nome_trabalho, nome_turma):
    path = os.getcwd()+"/../logsferramentas/"
    fp = os.popen("rm -rf " + path +"moss-" + nome_turma + "-" + nome_trabalho + ".log")
    fp.close()

def coleta_dados_execucao_jplag (nome_trabalho, nome_turma):
    path = os.getcwd() +"/../logsferramentas/jplag/" + nome_turma + "-" + nome_trabalho
    lista = os.listdir(path)
    
    lista_result_jplag = []
    for nome_arquivo in lista:
        if nome_arquivo.endswith("top.html"):
            arq = open(path +"/" + nome_arquivo, 'r')
            for line in arq:
                if line.startswith("<TR><TH><TH>"):
                    
                    lista_result_jplag.append(re.findall(r'\d+.py|\d+\.\d+', line))
                    arq.close()
                    break
    return lista_result_jplag
