import os
import re

#caminho ao diretorio de turmas
def gerar_path_turmas():
    return os.getcwd()+"/../codigosAlunos/"


#caminho ao diretorio de trabalhos
def gerar_path_trabalhos_turma(nomeTurma):
    return os.getcwd()+"/../codigosAlunos/"+nomeTurma+"/"

# verifica se existe uma determinada turma
def existe_turma (nomeTurma):
    path = gerar_path_turmas()
    lista = os.listdir(path)
    for pasta in lista:
        if pasta == nomeTurma:
            return True
    return False

# verifica se existe determinado trabalho em uma turma
def existe_trabalho_turma (nomeTrabalho, nomeTurma):
    if existe_turma(nomeTurma):
        path = gerar_path_trabalhos_turma(nomeTurma)
        lista = os.listdir(path)
        for pasta in lista:
            if pasta == nomeTrabalho:
                return True
    return False

# verifica se existe determinado código em um trabalho e turma
def existe_arquivo_trabalho (nomeTrabalho, nomeTurma, nomeArquivo):
    if existe_trabalho_turma(nomeTrabalho, nomeTurma):
        path = gerar_path_trabalhos_turma(nomeTurma) + nomeTrabalho + "/"
        lista = os.listdir(path)
        for arquivo in lista:
            if arquivo == nomeArquivo:
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
def criar_trabalho_turma (nomeTrabalho, nomeTurma):
    if existe_turma(nomeTurma) == False:
        return False
    
    path = gerar_path_trabalhos_turma(nomeTurma)
    lista = os.listdir(path)
    for pasta in lista:
        if pasta == nomeTrabalho:
            print ("Trabalho já existe:", nomeTrabalho)
            return False
    fp = os.popen("mkdir "+path+nomeTrabalho)
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
def listar_trabalhos_turma (nomeTurma):
    if existe_turma(nomeTurma) == False:
        return []
    path = gerar_path_trabalhos_turma(nomeTurma)
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
def apagar_trabalho_turma (nomeTrabalho, nomeTurma):
    if existe_turma(nomeTurma) == False:
        return False
    path = gerar_path_trabalhos_turma(nomeTurma)
    lista = os.listdir(path)
    for pasta in lista:
        if pasta == nomeTrabalho:
            fp = os.popen("rm -rf "+path+nomeTrabalho)
            fp.close()
            return True
    print("Trabalho não existe:", nomeTrabalho)
    return False

#retorna uma lista com todos os arquivos dentro de um determinado trabalho
def listar_codigos_trabalho (nomeTrabalho, nomeTurma):
    if existe_trabalho_turma (nomeTrabalho, nomeTurma) == False:
        return []
    
    path = gerar_path_trabalhos_turma(nomeTurma) + nomeTrabalho + "/"
    lista = os.listdir(path)
    return lista


#retorna o conteudo de um determinado arquivo
def ler_codigo_trabalho (nomeArquivo, nomeTrabalho, nomeTurma):
    if existe_trabalho_turma (nomeTrabalho, nomeTurma) == False:
        return

    path = gerar_path_trabalhos_turma(nomeTurma) + nomeTrabalho + "/"
    
    arq = open(path+nomeArquivo, 'r')
    conteudo = ""
    for line in arq:
        line = line.replace("&","&amp;")
        line = line.replace("<","&lt;")
        line = line.replace(">","&gt;")
        conteudo+=line
    
    arq.close()
    return conteudo

#retorna o numero de linhas de código de um trabalho
def conta_linhas_codigo (nomeTrabalho, nomeTurma, nomeArquivo):
    path = gerar_path_trabalhos_turma(nomeTurma) + nomeTrabalho + "/"
    arq = open(path+nomeArquivo, 'r')
    num = sum(1 for line in arq)
    arq.close()
    return num

def escreve_codigo_trabalho(nomeArquivo, nomeTrabalho, nomeTurma, conteudo):
    if existe_trabalho_turma (nomeTrabalho, nomeTurma) == False:
        return

    path = gerar_path_trabalhos_turma(nomeTurma) + nomeTrabalho + "/"
    arq = open(path+nomeArquivo, 'w')
    arq.write(conteudo)
    arq.close()
    return
    

def verifica_existe_pasta_jplag(nomeTrabalho, nomeTurma):
    path = os.getcwd()+"/../logsferramentas/jplag/"
    lista = os.listdir(path)
    for pasta in lista:
        if pasta == nomeTurma+"-"+nomeTrabalho:
            return True
    return False

def apagar_pasta_jplag(nomeTrabalho, nomeTurma):
    path = os.getcwd()+"/../logsferramentas/jplag/"
    fp = os.popen("rm -rf "+path+nomeTurma+"-"+nomeTrabalho)
    fp.close()

def verifica_existe_arquivo_moss(nomeTrabalho, nomeTurma):
    path = os.getcwd()+"/../logsferramentas/"
    lista = os.listdir(path)
    for arquivo in lista:
        if arquivo == "moss-"+nomeTurma+"-"+nomeTrabalho+".log":
            return True
    return False

def apagar_arquivo_moss(nomeTrabalho, nomeTurma):
    path = os.getcwd()+"/../logsferramentas/"
    fp = os.popen("rm -rf "+path+"moss-"+nomeTurma+"-"+nomeTrabalho+".log")
    fp.close()

def coleta_dados_execucao_jplag (nomeTrabalho, nomeTurma):
    path = os.getcwd()+"/../logsferramentas/jplag/"+nomeTurma+"-"+nomeTrabalho
    lista = os.listdir(path)
    
    listaResultJplag = []
    for nomeArquivo in lista:
        if nomeArquivo.endswith("top.html"):
            arq = open(path+"/"+nomeArquivo, 'r')
            for line in arq:
                if line.startswith("<TR><TH><TH>"):
                    
                    listaResultJplag.append(re.findall(r'\d+.py|\d+\.\d+', line))
                    arq.close()
                    break
    return listaResultJplag



if __name__ == "__main__":
    
    """
    lista = listarTurmas()
    print ("lista de turmas q existem:",lista)
    criarTurma("2021-2")
    criarTurma("2022-2")
    criarTurma("2023-1")
    
    lista = listarTurmas()
    print ("lista de turmas agora:",lista)
    """
    apagar_turma("2021-2")
    apagar_turma("2022-1")
    apagar_turma("2022-2")
    apagar_turma("2023-1")
    lista = listar_turmas()
    """
    print ("lista de turmas agora:",lista)
    """

    lista = listar_turmas()
    print ("lista de turmas agora:", lista)
    """
    criarTrabalhoTurma("projeto1", "2022-1")
    criarTrabalhoTurma("projeto2", "2022-1")
        
    criarTrabalhoTurma("projetoA", "turmaExemploA")
    lista = listarTrabalhosTurma("turmaExemplo")
    print ("lista de trabalhos da turmaExemplo:",lista)

    excluirTrabalhoTurma("projeto2", "turmaExemplo")
    excluirTrabalhoTurma("projeto1", "turmaExemploA")
    lista = listarTrabalhosTurma("turmaExemplo")
    print ("lista de trabalhos da turmaExemplo:",lista)

    print (ExisteTrabalhoTurma("projeto1","turmaExemplo"))
    print (ExisteTrabalhoTurma("projeto2","turmaExemplo"))

    criarTrabalhoTurma("projeto2", "turmaExemplo")
    """
    lista = listar_trabalhos_turma("turmaExemplo")
    print ("Lista de trabalhos dentro da turma de exemplo:", lista)

    lista = listar_codigos_trabalho("projeto1", "turmaExemplo")
    print ("Lista de códigos enviados em projeto1 turmaExemplo:", lista)


#    print (lerCodigoTrabalho("173402.py", "projeto1", "turmaExemplo"))
#    print (lerCodigoTrabalho("234590.py", "projeto1", "turmaExemplo"))
#    print (lerCodigoTrabalho("306411.py", "projeto1", "turmaExemplo"))