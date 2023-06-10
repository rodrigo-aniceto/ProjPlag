import os
import re

#caminho ao diretorio de turmas
def gerarPathTurmas():
    return os.getcwd()+"/../codigosAlunos/"


#caminho ao diretorio de trabalhos
def gerarPathTrabalhosTurma(nomeTurma):
    return os.getcwd()+"/../codigosAlunos/"+nomeTurma+"/"

# verifica se existe uma determinada turma
def existeTurma (nomeTurma):
    path = gerarPathTurmas()
    lista = os.listdir(path)
    for pasta in lista:
        if pasta == nomeTurma:
            return True
    return False

# verifica se existe determinado trabalho em uma turma
def existeTrabalhoTurma (nomeTrabalho, nomeTurma):
    if existeTurma(nomeTurma):
        path = gerarPathTrabalhosTurma(nomeTurma)
        lista = os.listdir(path)
        for pasta in lista:
            if pasta == nomeTrabalho:
                return True
    return False

# verifica se existe determinado código em um trabalho e turma
def existeArquivoTrabalho (nomeTrabalho, nomeTurma, nomeArquivo):
    if existeTrabalhoTurma(nomeTrabalho, nomeTurma):
        path = gerarPathTrabalhosTurma(nomeTurma)+nomeTrabalho+"/"
        lista = os.listdir(path)
        for arquivo in lista:
            if arquivo == nomeArquivo:
                return True
    return False




# cria uma pasta referente a uma nova turma, sucesso: True, se já existir com esse nome: False
# TODO validar as strings de entrada para não permitir caracteris que não podem ser usados em nome de pasta
def criarTurma (nome):
    path = gerarPathTurmas()
    lista = os.listdir(path)
    for pasta in lista:
        if pasta == nome:
            print ("Turma já existe:", nome)
            return False
    fp = os.popen("mkdir "+path+nome)
    fp.close()
    return True

# cria uma pasta referente a um novo trabalho, sucesso: True, se já existir com esse nome ou não existir a turma: False
def criarTrabalhoTurma (nomeTrabalho, nomeTurma):
    if existeTurma(nomeTurma) == False:
        return False
    
    path = gerarPathTrabalhosTurma(nomeTurma)
    lista = os.listdir(path)
    for pasta in lista:
        if pasta == nomeTrabalho:
            print ("Trabalho já existe:", nomeTrabalho)
            return False
    fp = os.popen("mkdir "+path+nomeTrabalho)
    fp.close()
    return True


# retorna a lista de pastas referentes a turmas
def listarTurmas ():
    path = gerarPathTurmas()
    lista = os.listdir(path)
    #print (lista)
    #print (len(lista))
    return lista

# retorna a lista de pastas referentes aos trabalhos
def listarTrabalhosTurma (nomeTurma):
    if existeTurma(nomeTurma) == False:
        return []
    path = gerarPathTrabalhosTurma(nomeTurma)
    lista = os.listdir(path)
    return lista


# exclui o diretório de uma turma, sucesso: True, se não existir com esse nome: False
def apagarTurma (nome):
    path = gerarPathTurmas()
    lista = os.listdir(path)
    for pasta in lista:
        if pasta == nome:
            fp = os.popen("rm -rf "+path+nome)
            fp.close()
            return True
    print("Turma não existe:", nome)
    return False

# exclui o diretório de um trabalho, sucesso: True, se não existir com esse nome, ou não existir a turma: False
def apagarTrabalhoTurma (nomeTrabalho, nomeTurma):
    if existeTurma(nomeTurma) == False:
        return False
    path = gerarPathTrabalhosTurma(nomeTurma)
    lista = os.listdir(path)
    for pasta in lista:
        if pasta == nomeTrabalho:
            fp = os.popen("rm -rf "+path+nomeTrabalho)
            fp.close()
            return True
    print("Trabalho não existe:", nomeTrabalho)
    return False

#retorna uma lista com todos os arquivos dentro de um determinado trabalho
def listarCodigosTrabalho (nomeTrabalho, nomeTurma):
    if existeTrabalhoTurma (nomeTrabalho, nomeTurma) == False:
        return []
    
    path = gerarPathTrabalhosTurma(nomeTurma)+nomeTrabalho+"/"
    lista = os.listdir(path)
    return lista


#retorna o conteudo de um determinado arquivo
def lerCodigoTrabalho (nomeArquivo, nomeTrabalho, nomeTurma):
    if existeTrabalhoTurma (nomeTrabalho, nomeTurma) == False:
        return

    path = gerarPathTrabalhosTurma(nomeTurma)+nomeTrabalho+"/"
    
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
def contaLinhasCodigo (nomeTrabalho, nomeTurma, nomeArquivo):
    path = gerarPathTrabalhosTurma(nomeTurma)+nomeTrabalho+"/"
    arq = open(path+nomeArquivo, 'r')
    num = sum(1 for line in arq)
    arq.close()
    return num

def escreveCodigoTrabalho(nomeArquivo, nomeTrabalho, nomeTurma, conteudo):
    if existeTrabalhoTurma (nomeTrabalho, nomeTurma) == False:
        return

    path = gerarPathTrabalhosTurma(nomeTurma)+nomeTrabalho+"/"
    arq = open(path+nomeArquivo, 'w')
    arq.write(conteudo)
    arq.close()
    return
    

def verificaExistePastaJplag(nomeTrabalho, nomeTurma):
    path = os.getcwd()+"/../logsferramentas/jplag/"
    lista = os.listdir(path)
    for pasta in lista:
        if pasta == nomeTurma+"-"+nomeTrabalho:
            return True
    return False

def apagarPastaJplag(nomeTrabalho, nomeTurma):
    path = os.getcwd()+"/../logsferramentas/jplag/"
    fp = os.popen("rm -rf "+path+nomeTurma+"-"+nomeTrabalho)
    fp.close()

def verificaExisteArquivoMoss(nomeTrabalho, nomeTurma):
    path = os.getcwd()+"/../logsferramentas/"
    lista = os.listdir(path)
    for arquivo in lista:
        if arquivo == "moss-"+nomeTurma+"-"+nomeTrabalho+".log":
            return True
    return False

def apagarArquivoMoss(nomeTrabalho, nomeTurma):
    path = os.getcwd()+"/../logsferramentas/"
    fp = os.popen("rm -rf "+path+"moss-"+nomeTurma+"-"+nomeTrabalho+".log")
    fp.close()

def coletaDadosExecucaoJplag (nomeTrabalho, nomeTurma):
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
    apagarTurma("2021-2")
    apagarTurma("2022-1")
    apagarTurma("2022-2")
    apagarTurma("2023-1")
    lista = listarTurmas()
    """
    print ("lista de turmas agora:",lista)
    """

    lista = listarTurmas()
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
    lista = listarTrabalhosTurma("turmaExemplo")
    print ("Lista de trabalhos dentro da turma de exemplo:", lista)

    lista = listarCodigosTrabalho("projeto1", "turmaExemplo")
    print ("Lista de códigos enviados em projeto1 turmaExemplo:", lista)


#    print (lerCodigoTrabalho("173402.py", "projeto1", "turmaExemplo"))
#    print (lerCodigoTrabalho("234590.py", "projeto1", "turmaExemplo"))
#    print (lerCodigoTrabalho("306411.py", "projeto1", "turmaExemplo"))