import os
from sys import path
from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, SelectField, DateField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired, Optional
import arquivos
import baseDados
import ferramentas
import input
from decouple import config

from random import randint

app = Flask(__name__)
Bootstrap(app) #colocar extensão  bootstrap

db_connect = config('CONNECT_STRING') #string de conexão privada SQLALCHEMY
file_upload_key = config('FILE_KEY') #chave secreta usada no upload de arquivos

app.config["SQLALCHEMY_DATABASE_URI"] = db_connect
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = file_upload_key
app.config['UPLOAD_FOLDER'] = '../input'


baseDados.db.init_app(app)

class UploadFileForm(FlaskForm):
    file = FileField("Arquivo", validators=[InputRequired()])
    turma = StringField("Nome da Turma (ex: 2021-1):", validators=[InputRequired()])
    tarefa = StringField("Nome da Tarefa (ex: projeto1):", validators=[InputRequired()])
    tipo_tarefa = SelectField('Tipo da tarefa', id='tipotarefa', choices=[('projeto', 'Projeto'), ('questionario', 'Questionário')], validators=[InputRequired()])
    data_limite = DateField('Data limite para entrega', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField("Upload")

# TODO: função de deletar
@app.route("/", methods=['GET',"POST"])
def tela_inicial():
    lista_turmas = baseDados.listar_turmas()
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # coleta do arquivo
        nome_turma = form.turma.data
        nome_tarefa = form.tarefa.data
        tipo_tarefa = form.tipo_tarefa.data
        data_limite = form.data_limite.data
        if tipo_tarefa == "projeto" and data_limite == None:
            return render_template('index.html', listaturmas=lista_turmas,form=form, mensagem="Favor preencher a data limite")

        #print ("nome turma:", nome_turma, "nome tarefa:", nome_tarefa, "tipo_tarefa:", tipo_tarefa, "data limite:", data_limite)
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Salvar o arquivo
        nome_arquivo = input.ajustar_nome(file.filename)
        if tipo_tarefa == "projeto":
            input.inserir_planilha_projeto(nome_turma, nome_arquivo, data_limite.strftime('%d/%m/%Y'), nome_tarefa)
        else:
            input.inserir_planilha_questionario(nome_turma, nome_arquivo, nome_tarefa)

        lista_turmas = baseDados.listar_turmas()
        return render_template('index.html', listaturmas=lista_turmas,form=form, mensagem="Arquivo submetido com sucesso")

    return render_template('index.html', listaturmas=lista_turmas,form=form, mensagem="")


#relatoriotrabalho?turma=turmaExemplo&nomeprojeto=projeto1
@app.route("/relatoriotrabalho")
def relatorio_trabalho():
    nome_projeto = request.args.get("nomeprojeto")
    nome_turma = request.args.get("turma")
    if (nome_projeto == None) or (nome_turma == None):
        return "Incorrect parameters"
    
    lista_alunos = []
    mensagem = "the report is unavailable now"
    if (arquivos.existe_turma(nome_turma) == False):
        mensagem = "Class not registered"
    elif (arquivos.existe_trabalho_turma(nome_projeto, nome_turma) == False):
        mensagem = "Project not registered"
    else:
        lista_alunos = baseDados.listar_alunos_trabalho(nome_turma, nome_projeto)
    
    return render_template('relatoriotrabalho.html', mensagem=mensagem, listaalunos=lista_alunos, nomeprojeto=nome_projeto, turma=nome_turma)


@app.route("/relatorioferramentas")
def relatorio_ferramentas():
    nome_projeto = request.args.get("nomeprojeto")
    nome_turma = request.args.get("turma")
    if (nome_projeto == None) or (nome_turma == None):
        return "Incorrect parameters"
    
    lista_resultados = []
    mensagem = "the report is unavailable now"
    if (arquivos.existe_turma(nome_turma) == False):
        mensagem = "Class not registered"
    elif (arquivos.existe_trabalho_turma(nome_projeto, nome_turma) == False):
        mensagem = "Project not registered"
    else:
        lista_resultados = baseDados.listar_resultados_ferramentas(nome_turma, nome_projeto)
    
    return render_template('relatorioferramentas.html', mensagem=mensagem, listaresultados=lista_resultados, nomeprojeto=nome_projeto, turma=nome_turma)


#@app.route("/graforelatorio?turma=<string:turma>&nomeprojeto=<string:nomeprojeto>")
@app.route("/graforelatorio")
def grafo_relatorio():
    
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

    if arquivos.existe_turma(turma) == False:
        mensagem = "Class not registered"
    elif arquivos.existe_trabalho_turma(nomeprojeto, turma) == False:
        mensagem = "Project not registered"
    elif ferramenta != "moss" and ferramenta != "jplag":
        mensagem = "Invalid tool"
    else:
        lista_resultados = baseDados.listar_dados_grafo_ferramentas(turma, nomeprojeto, ferramenta, percentual)
        class nos:
            matricula = ""
            conteudo = ""
        class arestas:
            origem = ""
            destino = ""
            valor = ""

        
        for elemento in lista_resultados:
    
            ja_existe = False
            for item in lista_nos:
                if item.matricula == elemento.matricula1:
                    ja_existe = True
                    break
            if ja_existe == False:
                novo_no = nos()
                novo_no.matricula = elemento.matricula1
                #deixar só primeiro, ultimo nome e matricula
                novo_no.conteudo = elemento.nome1.split(' ',1)[0] + ' ' + elemento.nome1.rsplit(' ',1)[-1] + '\n' + elemento.matricula1
                lista_nos.append(novo_no)

            #mesmo para o item da direita
            ja_existe = False
            for item in lista_nos:
                if item.matricula == elemento.matricula2:
                    ja_existe = True
                    break
            if ja_existe == False:
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
def relatorio_turma():
    nome_turma = request.args.get("turma")
    mensagem = "Unavailable report"
    lista_resultados_base = []
    lista_trabalhos = []
    lista_questionarios = []

    if nome_turma == None:
        mensagem = "Incorrect parameters"
    elif arquivos.existe_turma(nome_turma) == False:
        mensagem = "Class not registered"
    else:
        lista_resultados_base, lista_trabalhos, lista_questionarios = baseDados.gera_relatorio_geral(nome_turma)

    return render_template('relatorioturma.html', mensagem=mensagem, listaresultados=lista_resultados_base, listatrabalhos=lista_trabalhos, listaquestionarios=lista_questionarios, tamanholistatrabalhos=len(lista_trabalhos), tamanholistaquestionarios=len(lista_questionarios), turma=nome_turma)


@app.route("/relatorioaluno")
def relatorio_aluno():
    matricula_aluno = request.args.get("matricula")
    turma = request.args.get("turma")
    resultado_projs = baseDados.busca_relatorio_projetos_aluno(matricula_aluno, turma)
    resultado_quests = baseDados.busca_relatorio_questionarios_aluno(matricula_aluno, turma)
    nome = baseDados.busca_nome_aluno(matricula_aluno, turma)
    return render_template("relatorioaluno.html", resultadosprojs=resultado_projs, resultadosquests=resultado_quests, matricula=matricula_aluno, nome=nome, turma=turma)


@app.route("/codigofonte")
def codigo_fonte():
    nomeprojeto = request.args.get("nomeprojeto")
    turma = request.args.get("turma")
    arquivo = request.args.get("arquivo")

    return "<pre><code>"+arquivos.ler_codigo_trabalho (arquivo, nomeprojeto, turma)+ "</code></pre>"

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
def run_jplag():
    
    nomeprojeto = request.args.get("nomeprojeto")
    turma = request.args.get("turma")
    ferramentas.executa_jplag(nomeprojeto, turma)

    return "ok"

@app.route("/verjplag")
def result_jplag():

    nomeprojeto = request.args.get("nomeprojeto")
    turma = request.args.get("turma")
    result = ferramentas.verifica_execucao_jplag(nomeprojeto, turma)

    return result



@app.route("/runmoss")
def run_moss():

    nomeprojeto = request.args.get("nomeprojeto")
    turma = request.args.get("turma")
    ferramentas.executa_moss(nomeprojeto, turma)

    return "ok"


@app.route("/vermoss")
def verifica_moss():

    nomeprojeto = request.args.get("nomeprojeto")
    turma = request.args.get("turma")
    result = ferramentas.verifica_execucao_moss(nomeprojeto, turma)

    return result


@app.route("/apagarturma")
def apagar_turma():
    turma = request.args.get("turma")
    #lista_trabalhos = baseDados.lista_trabalhos_turma(turma) #criar função
    # loop percorrer trabalhos
    # todo verificar se todos os dados são apagados e peercorrer questionários tbm
    #baseDados.apagarTrabalhoTurma(nomeTrabalho=trabalho,nomeTurma=turma)
    #arquivos.apagarTrabalhoTurma(nomeTrabalho=trabalho,nomeTurma=turma)



if __name__ == "__main__":
    with app.app_context():
        baseDados.db.create_all()
    app.run(debug=True)