import os
from sys import path
from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import arquivos
import baseDados
import ferramentas
from decouple import config

from random import randint

app = Flask(__name__)
Bootstrap(app) #isso é para colocar extensões tipo o bootstrap
db_connect = config('CONNECT_STRING')
app.config["SQLALCHEMY_DATABASE_URI"] = db_connect #string de conexão privada SQLALCHEMY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route("/")
def telaInicial():
    lista_turmas = baseDados.listarTurmas()
    return render_template('index.html', listaturmas=lista_turmas)


#relatoriotrabalho?turma=turmaExemplo&nomeprojeto=projeto1
@app.route("/relatoriotrabalho")
def relatoriotrabalho():
    nome_projeto = request.args.get("nomeprojeto")
    nome_turma = request.args.get("turma")
    if (nome_projeto == None) or (nome_turma == None):
        return "Parametros incorretos"
    
    lista_alunos = []
    mensagem = "relatorio indisponivel"
    if (arquivos.existeTurma(nome_turma) == False):
        mensagem = "Turma não cadastrada"
    elif (arquivos.existeTrabalhoTurma(nome_projeto, nome_turma) == False):
        mensagem = "Trabalho não cadastrado"
    else:
        lista_alunos = baseDados.listar_alunos_trabalho(nome_turma, nome_projeto)
    
    return render_template('relatoriotrabalho.html', mensagem=mensagem, listaalunos=lista_alunos, nomeprojeto=nome_projeto, turma=nome_turma)


@app.route("/relatorioferramentas")
def relatorioferramentas():
    nome_projeto = request.args.get("nomeprojeto")
    nome_turma = request.args.get("turma")
    if (nome_projeto == None) or (nome_turma == None):
        return "Parametros incorretos"
    
    lista_resultados = []
    mensagem = "relatório indisponivel"
    if (arquivos.existeTurma(nome_turma) == False):
        mensagem = "Turma não cadastrada"
    elif (arquivos.existeTrabalhoTurma(nome_projeto, nome_turma) == False):
        mensagem = "Trabalho não cadastrado"
    else:
        lista_resultados = baseDados.listar_resultados_ferramentas(nome_turma, nome_projeto)
    
    return render_template('relatorioferramentas.html', mensagem=mensagem, listaresultados=lista_resultados, nomeprojeto=nome_projeto, turma=nome_turma)


#@app.route("/graforelatorio?turma=<string:turma>&nomeprojeto=<string:nomeprojeto>")
@app.route("/graforelatorio")
def graforelatorio():
    
    nomeprojeto = request.args.get("nomeprojeto")
    turma = request.args.get("turma")
    ferramenta = request.args.get("ferramenta")
    percentual = request.args.get("percentual")
    
    if (nomeprojeto == None) or (turma == None):
        return "Parametros incorretos"
    
    mensagem = ""
    lista_resultados = []
    lista_nos = []
    lista_arestas = []

    if (arquivos.existeTurma(turma) == False):
        mensagem = "Turma não cadastrada"
    elif (arquivos.existeTrabalhoTurma(nomeprojeto, turma) == False):
        mensagem = "Trabalho não cadastrado"
    elif ferramenta != "moss" and ferramenta != "jplag":
        mensagem = "Ferramenta inválida"
    else:
        lista_resultados = baseDados.listarDadosGrafoFerramentas(turma, nomeprojeto, ferramenta, percentual)
        class nos:
            matricula = ""
            conteudo = ""
        class arestas:
            origem = ""
            destino = ""
            valor = ""

        
        for elemento in lista_resultados:
    
            jaExiste = False
            for item in lista_nos:
                if item.matricula == elemento.matricula1:
                    jaExiste = True
                    break
            if jaExiste == False:
                novo_no = nos()
                novo_no.matricula = elemento.matricula1
                #deixar só primeiro, ultimo nome e matricula
                novo_no.conteudo = elemento.nome1.split(' ',1)[0] + ' ' + elemento.nome1.rsplit(' ',1)[-1] + '\n' + elemento.matricula1
                lista_nos.append(novo_no)

            #mesmo para o item da direita
            jaExiste = False
            for item in lista_nos:
                if item.matricula == elemento.matricula2:
                    jaExiste = True
                    break
            if jaExiste == False:
                novo_no = nos()
                novo_no.matricula = elemento.matricula2
                novo_no.conteudo = elemento.nome2.split(' ',1)[0] + ' ' + elemento.nome2.rsplit(' ',1)[-1] + '\n' + elemento.matricula2
                lista_nos.append(novo_no)


            nova_aresta = arestas()
            nova_aresta.origem = elemento.matricula1
            nova_aresta.destino = elemento.matricula2
            # 30% - 1
            # 40% - 2
            # 50% - 3
            # 60% - 4
            # 70% - 5
            # 80% - 6
            # 90% - 7
            if int(elemento.similaridade) >= 90:
                nova_aresta.valor = '7'
            elif int(elemento.similaridade) >= 80:
                nova_aresta.valor = '6'
            elif int(elemento.similaridade) >= 70:
                nova_aresta.valor = '5'
            elif int(elemento.similaridade) >= 60:
                nova_aresta.valor = '4'
            elif int(elemento.similaridade) >= 50:
                nova_aresta.valor = '3'
            elif int(elemento.similaridade) >= 40:
                nova_aresta.valor = '2'
            else: # elemento.similaridade >= 30
                nova_aresta.valor = '1'

            lista_arestas.append(nova_aresta)

    return render_template('graforelatorio.html', mensagem=mensagem, listanos=lista_nos, listaarestas=lista_arestas, nomeprojeto=nomeprojeto, turma=turma, ferramenta=ferramenta, percentual=percentual)




@app.route("/relatorioturma")
def relatorioturma():
    nome_turma = request.args.get("turma")
    mensagem = "relatório indisponivel"
    lista_resultados_base = []

    if (nome_turma == None):
        mensagem = "Parametros incorretos"
    elif (arquivos.existeTurma(nome_turma) == False):
        mensagem = "Turma não cadastrada"
    else:
        lista_resultados_base = baseDados.gera_relatorio_geral(nome_turma)
        #criação de lista com todos os trabalhos
        lista_trabalhos = []
        for resultado in lista_resultados_base:
            for trabalho in resultado.nomes_trabalhos:
                if trabalho not in lista_trabalhos:
                    lista_trabalhos.append(trabalho)
        lista_trabalhos.sort()
        
        #adiciona a tabela informações dos trabalhos que o aluno não fez
        for resultado in lista_resultados_base:
            if len(resultado.nomes_trabalhos) != len(lista_trabalhos):
                i=0
                for trabalho in lista_trabalhos:
                    if i < len(resultado.nomes_trabalhos):
                        if (resultado.nomes_trabalhos[i] == trabalho):
                            i = i+1
                        else:
                            #adicionar na posição i de resultado.nomes_trabalhos trabalho e 0 nessa posiação nas outras 
                            resultado.nomes_trabalhos.insert(i, trabalho)
                            resultado.notas_trabalhos.insert(i, '0.00')
                            resultado.similaridade_jplag.insert(i, '0')
                            resultado.similaridade_moss.insert(i, '0')
                            i = i + 1
                    else:
                        resultado.nomes_trabalhos.append(trabalho)
                        resultado.notas_trabalhos.append('0.00')
                        resultado.similaridade_jplag.append('0')
                        resultado.similaridade_moss.append('0')
                        i = i + 1

    return render_template('relatorioturma.html', mensagem=mensagem, listaresultados=lista_resultados_base, listatrabalhos=lista_trabalhos, tamanholistatrabalhos=len(lista_trabalhos), turma=nome_turma)


@app.route("/relatorioaluno")
def relatorioaluno():
    matricula_aluno = request.args.get("matricula")
    turma = request.args.get("turma")

    return ""

@app.route("/codigofonte")
def codigofonte():
    nomeprojeto = request.args.get("nomeprojeto")
    turma = request.args.get("turma")
    arquivo = request.args.get("arquivo")

    return "<pre><code>"+arquivos.lerCodigoTrabalho (arquivo, nomeprojeto, turma)+"</code></pre>"


@app.route("/codigo")
def codigo():

    resposta = "<P>Seguem os códigos fontes:</p>"
    
    #receber lista de códigos
    lista = arquivos.listarCodigosTrabalho("projeto1", "turmaExemplo")

    for arquivo in lista:
        resposta+="<p>Segue o conteúdo do arquivo "+arquivo+"</p>"
        conteudo = arquivos.lerCodigoTrabalho(arquivo, "projeto1", "turmaExemplo")
        resposta+="<pre><code>"+conteudo+"</code></pre>"

    return resposta



@app.route("/runjplag")
def runjplag():
    
    nomeprojeto = request.args.get("nomeprojeto")
    turma = request.args.get("turma")
    ferramentas.executaJplag(nomeprojeto, turma)

    return "ok"

@app.route("/verjplag")
def resultjplag():

    nomeprojeto = request.args.get("nomeprojeto")
    turma = request.args.get("turma")
    result = ferramentas.verificaExecucaoJplag(nomeprojeto, turma)

    return result



@app.route("/runmoss")
def runmoss():

    nomeprojeto = request.args.get("nomeprojeto")
    turma = request.args.get("turma")
    ferramentas.executaMoss(nomeprojeto, turma)

    return "ok"


#isso eh temporario
@app.route("/vermoss")
def verifica_moss():

    nomeprojeto = request.args.get("nomeprojeto")
    turma = request.args.get("turma")
    result = ferramentas.verificaExecucaoMoss(nomeprojeto, turma)

    return result






if __name__ == "__main__":
    app.run(debug=True)