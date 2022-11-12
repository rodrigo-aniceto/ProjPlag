import os
from sys import path
from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
import arquivos
import baseDados
import ferramentas
from decouple import config

from random import randint

app = Flask(__name__)
Bootstrap(app) #isso é para colocar extensões tipo o bootstrap

db_connect = config('CONNECT_STRING') #string de conexão privada SQLALCHEMY
file_upload_key = config('FILE_KEY') #chave secreta usada no upload de arquivos

app.config["SQLALCHEMY_DATABASE_URI"] = db_connect
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = file_upload_key
app.config['UPLOAD_FOLDER'] = '../input'

db = SQLAlchemy(app)

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Submeter")

@app.route("/", methods=['GET',"POST"])
def telaInicial():
    lista_turmas = baseDados.listarTurmas()
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # coleta do arquivo
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Salvar o arquivo
        return render_template('index.html', listaturmas=lista_turmas,form=form, mensagem="Arquivo submetido com sucesso")

    return render_template('index.html', listaturmas=lista_turmas,form=form, mensagem="")


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
    lista_trabalhos = []
    lista_questionarios = []

    if (nome_turma == None):
        mensagem = "Parametros incorretos"
    elif (arquivos.existeTurma(nome_turma) == False):
        mensagem = "Turma não cadastrada"
    else:
        lista_resultados_base, lista_trabalhos, lista_questionarios = baseDados.gera_relatorio_geral(nome_turma)

    return render_template('relatorioturma.html', mensagem=mensagem, listaresultados=lista_resultados_base, listatrabalhos=lista_trabalhos, listaquestionarios=lista_questionarios, tamanholistatrabalhos=len(lista_trabalhos), tamanholistaquestionarios=len(lista_questionarios), turma=nome_turma)


@app.route("/relatorioaluno")
def relatorioaluno():
    matricula_aluno = request.args.get("matricula")
    turma = request.args.get("turma")
    resultado_projs = baseDados.buscaRelatorioProjetosAluno(matricula_aluno, turma)
    resultado_quests = baseDados.buscaRelatorioQuestionariosAluno(matricula_aluno, turma)
    nome = baseDados.buscaNomeAluno(matricula_aluno, turma)
    return render_template("relatorioaluno.html", resultadosprojs=resultado_projs, resultadosquests=resultado_quests, matricula=matricula_aluno, nome=nome, turma=turma)


@app.route("/codigofonte")
def codigofonte():
    nomeprojeto = request.args.get("nomeprojeto")
    turma = request.args.get("turma")
    arquivo = request.args.get("arquivo")

    return "<pre><code>"+arquivos.lerCodigoTrabalho (arquivo, nomeprojeto, turma)+"</code></pre>"

'''
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
'''


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


@app.route("/vermoss")
def verifica_moss():

    nomeprojeto = request.args.get("nomeprojeto")
    turma = request.args.get("turma")
    result = ferramentas.verificaExecucaoMoss(nomeprojeto, turma)

    return result






if __name__ == "__main__":
    app.run(debug=True)