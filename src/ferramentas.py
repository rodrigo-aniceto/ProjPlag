import os
import arquivos
import baseDados
import urllib.request
import re


def executaMoss(nomeTrabalho, nomeTurma):
    if arquivos.existeTrabalhoTurma (nomeTrabalho, nomeTurma):

        if (arquivos.verificaExisteArquivoMoss(nomeTrabalho, nomeTurma)):
            arquivos.apagarArquivoMoss(nomeTrabalho, nomeTurma)

        comando = "../moss/moss -l python ../codigosAlunos/"+nomeTurma+"/"+nomeTrabalho+"/*.py"
        arq = open('../logsferramentas/moss-'+nomeTurma+'-'+nomeTrabalho+'.log', 'w')
        arq.flush()

        fp = os.popen(comando)
        arq.write(fp.read())
        fp.close()
        arq.close()

        arq = open('../logsferramentas/moss-'+nomeTurma+'-'+nomeTrabalho+'.log', 'r')
        ultima_linha = arq.readlines()[-1]

        if ultima_linha.startswith("http"):
            listaResult = coletaDadosExecucaoMoss(ultima_linha)
            resultados = geraListaSimilaridade (listaResult)
            baseDados.insereResultadosBanco(resultados, nomeTrabalho, nomeTurma, "moss")
            baseDados.insereRegistroFerrameta(nomeTrabalho,nomeTurma,"moss")
            
        arquivos.apagarArquivoMoss(nomeTrabalho, nomeTurma)

def verificaExecucaoMoss(nomeTrabalho, nomeTurma):

    registro = baseDados.buscaRegistroFerramenta(nomeTrabalho, nomeTurma, "moss")
    
    path = os.getcwd()+"/../logsferramentas/"
    lista_arquivos = os.listdir(path)
    for arquivo in lista_arquivos:
        if arquivo == "moss-"+nomeTurma+"-"+nomeTrabalho+".log":
            try:
                arq = open(path+arquivo, 'r')
                ultima_linha = arq.readlines()[-1]
            except:
                arq.close()
                return "Executando moss..."
            else:
                arq.close()
                if ultima_linha.startswith("http"):
                    return "Concluindo execução..."
                else:
                    return "ERRO comunicação servidor"

    
    if registro != None:
        return "Última execução Moss: "+ registro.data_execucao.strftime("%d/%m/%Y, %H:%M:%S")
    else:
        return "Moss ainda não executado"
    

def apagaExecucaoMoss(nomeTrabalho, nomeTurma):
    if arquivos.existeTrabalhoTurma (nomeTrabalho, nomeTurma):
        if (arquivos.verificaExisteArquivoMoss(nomeTrabalho, nomeTurma)):
            arquivos.apagarArquivoMoss(nomeTrabalho, nomeTurma)

        baseDados.apagarResultadosFerramenta(nomeTrabalho, nomeTurma, "moss")


def apagaExecucaoJplag(nomeTrabalho, nomeTurma):
    if arquivos.existeTrabalhoTurma (nomeTrabalho, nomeTurma):
        if (arquivos.verificaExistePastaJplag(nomeTrabalho, nomeTurma)):
            arquivos.apagarPastaJplag(nomeTrabalho, nomeTurma)

        baseDados.apagarResultadosFerramenta(nomeTrabalho, nomeTurma, "jplag")




def executaJplag(nomeTrabalho, nomeTurma):
    if arquivos.existeTrabalhoTurma (nomeTrabalho, nomeTurma):

        comando = "java -jar ../jplag/jplag-2.12.1-SNAPSHOT-jar-with-dependencies.jar -l python3 -s ../codigosAlunos/"+nomeTurma+"/"+nomeTrabalho+"/ -m 20\% -r ../logsferramentas/jplag/"+nomeTurma+"-"+nomeTrabalho+"/"

        # verifica se já existe pasta
        if (arquivos.verificaExistePastaJplag(nomeTrabalho, nomeTurma)):
            arquivos.apagarPastaJplag(nomeTrabalho, nomeTurma)
        # se já existir apagar pasta

        fp = os.popen(comando)
        fp.close()
        
        #lê os dados ferramenta
        listaResult = arquivos.coletaDadosExecucaoJplag(nomeTrabalho, nomeTurma)
        resultados = geraListaSimilaridade (listaResult)
        #insere no banco
        baseDados.insereResultadosBanco(resultados, nomeTrabalho, nomeTurma, "jplag")
        baseDados.insereRegistroFerrameta(nomeTrabalho,nomeTurma,"jplag")
        arquivos.apagarPastaJplag(nomeTrabalho, nomeTurma)




def verificaExecucaoJplag(nomeTrabalho, nomeTurma):

    registro = baseDados.buscaRegistroFerramenta(nomeTrabalho, nomeTurma, "jplag")
    if registro != None:
        return "Última execução Jplag: "+ registro.data_execucao.strftime("%d/%m/%Y, %H:%M:%S")
    else:
        return "Jplag ainda não executado"

'''
    #verificação manual desabilitada
    path = os.getcwd()+"/../logsferramentas/jplag"
    lista_arquivos = os.listdir(path)
    for arquivo in lista_arquivos:
        if arquivo == nomeTurma+"-"+nomeTrabalho:
            #verificar inserção BD
            return "3"

    return "0" #jplag nao executado
'''


def geraListaSimilaridade (listaResult):
    
    listaResumida = []
    
    
    # lista todos os resultados
    for elemento in listaResult:
        aux = []

        aux.append(elemento[0].split('.',1)[0]) #remover caracters depois do . e %
        aux.append(elemento[1].split('%',1)[0].split('.',1)[0])
        aux.append(elemento[2].split('.',1)[0])

        listaResumida.append(aux)
        aux = []
        aux.append(elemento[2].split('.',1)[0])
        aux.append(elemento[3].split('%',1)[0].split('.',1)[0])
        aux.append(elemento[0].split('.',1)[0])
        listaResumida.append(aux)
    
    """
    #lista resultado o maior de cada aluno
    for elemento in listaResult:
        aux = []
        aux.append(elemento[0].split('.', 1)[0]) #remover caracters depois do . e %
        aux.append(elemento[1].split('%', 1)[0].split('.',1)[0])
        aux.append(elemento[2].split('.', 1)[0])
        
        existeNaLista = False
        #verificar se aux[0] está na lista
        for elementoListaResumida in listaResumida:
            if elementoListaResumida[0] == aux[0]:
                existeNaLista = True
                # se estiver verificar se o valor que está lá é menor, se estiver atualizar
                if (int(aux[1]) > int(elementoListaResumida[1])):
                    elementoListaResumida[1] = aux[1]
                    elementoListaResumida[2] = aux[2]  
                break
        
        #fazer o append do elemento q não está na lista
        if (existeNaLista == False):
            listaResumida.append(aux)
            
        #repetir o processo para os elementos da direita na lista do jplag
        aux = []
        aux.append(elemento[2].split('.', 1)[0])
        aux.append(elemento[3].split('%', 1)[0].split('.',1)[0])
        aux.append(elemento[0].split('.', 1)[0])

        existeNaLista = False
        for elementoListaResumida in listaResumida:
            if elementoListaResumida[0] == aux[0]:
                existeNaLista = True
                if (int(aux[1]) > int(elementoListaResumida[1])):
                    elementoListaResumida[1] = aux[1]
                    elementoListaResumida[2] = aux[2]    
                break
        if (existeNaLista == False):
            listaResumida.append(aux)
    """

    return listaResumida


def coletaDadosExecucaoMoss (url):
    try:
        response =  urllib.request.urlopen(url)
        html = response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
            print(e)

    lista = html.split("\n")
    i = 1
    listaResultMoss = []
    aux = []

    for line in lista:
        if line.endswith("%)</A>") or line.endswith("%)</a>"):
            #print (line)


            if (i % 2):
                aux = []
                aux = aux + re.findall(r'\d+.py|\d+%', line)
            else:
                aux = aux + re.findall(r'\d+.py|\d+%', line)
                listaResultMoss.append(aux)

            i = i + 1
    
    return listaResultMoss


# comando execução moss:
# ../moss/moss -l python ../codigosAlunos/turmaExemplo/projeto1/*.py

'''
Checking files . . . 
OK
Uploading ../codigosAlunos/turmaExemplo/projeto1/168183553.py ...done.
Uploading ../codigosAlunos/turmaExemplo/projeto1/168183591.py ...done.
Uploading ../codigosAlunos/turmaExemplo/projeto1/168183601.py ...done.
Uploading ../codigosAlunos/turmaExemplo/projeto1/260544095.py ...done.
Query submitted.  Waiting for the server's response.
http://moss.stanford.edu/results/9/2839961034219
'''


# comando execução jplag
# java -jar ../jplag/jplag-2.12.1-SNAPSHOT-jar-with-dependencies.jar -l python3 -s ../codigosAlunos/turmaExemplo/projeto1/ -r ../logsferramentas/jplag/turmaExemplo-projeto1/

'''
...
Comparing 260401526.py-260401914.py: 0.0
Comparing 260401526.py-260423027.py: 5.3932586
Comparing 260401526.py-260449968.py: 12.526998
Comparing 260401526.py-260544095.py: 0.0
Comparing 260401914.py-260423027.py: 0.0
Comparing 260401914.py-260449968.py: 0.0
Comparing 260401914.py-260544095.py: 39.2053
Comparing 260423027.py-260449968.py: 5.633803
Comparing 260423027.py-260544095.py: 0.0
Comparing 260449968.py-260544095.py: 0.0

Writing results to: ../logsferramentas/jplag/turmaExemplo-projeto1/



para leitura do percentual exato no jplag ele tera que abrir todos os arquivos e ver o percentual pra cada código

o dado que quero está nessa linha:
<TR><TH><TH>232806342.py (76.190475%)<TH>232801256.py (13.333333%)<TH>Tokens
dos arquivos match12-top.html
'''