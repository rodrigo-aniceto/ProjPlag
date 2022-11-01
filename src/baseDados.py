from flask import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import true
from app import db
import arquivos

from random import randrange
from random import randint
from datetime import datetime


#modelo de dados do BD
class Alunos(db.Model):
    __tablename__ = "alunos"
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(12), nullable=False)
    turma = db.Column(db.String(15), nullable=False)
    nome = db.Column(db.String(100))
    grupo = db.Column(db.String(50))
    notas = db.relationship("Projetos", backref="aluno")
    similaridades = db.relationship("Similaridades", backref="aluno")

    def __repr__(self):
        return str(self.id)


class Projetos(db.Model):
    __tablename__ = "projetos"
    id = db.Column(db.Integer, primary_key=True)
    nome_trabalho = db.Column(db.String(10), nullable=False)
    nota = db.Column(db.String(5))
    tempo_gasto = db.Column(db.String(25))
    prazo_restante = db.Column(db.String(2))
    id_aluno = db.Column(db.Integer, db.ForeignKey("alunos.id"))

    def __repr__(self):
        return self.nota

class Similaridades(db.Model):
    __tablename__ = "similaridades"
    id = db.Column(db.Integer, primary_key=True)
    nome_trabalho = db.Column(db.String(10), nullable=False)
    percentual = db.Column(db.String(4))
    turma = db.Column(db.String(15))
    ferramenta = db.Column(db.String(10), nullable=False)
    id_aluno = db.Column(db.Integer, db.ForeignKey("alunos.id"))
    matricula_outro_aluno = db.Column(db.String(12))

    def __repr__(self):
        return self.percentual

class RegistrosFerramentas(db.Model):
    __tablename__ = "registrosferramentas"
    id = db.Column(db.Integer, primary_key=True)
    nome_trabalho = db.Column(db.String(10), nullable=False)
    turma = db.Column(db.String(15), nullable=False)
    ferramenta = db.Column(db.String(10), nullable=False)
    data_execucao = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return str(self.id)

class Questionarios(db.Model):
    __tablename__ = "questionarios"
    id = db.Column(db.Integer, primary_key=True)
    nome_questionario = db.Column(db.String(15), nullable=False)
    nota = db.Column(db.String(5))
    id_aluno = db.Column(db.Integer, db.ForeignKey("alunos.id"))

    def __repr__(self):
        return self.nota

# usada para criar o banco
#db.drop_all()
db.create_all()
db.session.commit()


def inserir_novo_aluno(nome, matricula, turma, grupo):
    aluno = Alunos.query.filter_by(nome=nome, matricula=matricula, turma=turma).first()
    if aluno != None:
        print("aluno já existe")
        db.session.close()
        return 1
    
    novo_aluno = Alunos(nome=nome, matricula=matricula, turma=turma, grupo=grupo)
    try:
        db.session.add(novo_aluno)
        db.session.commit()
    except:
        return 1
    finally:
        db.session.close()

    return 0

def inserir_nova_nota(matricula, nota, turma, nome_trabalho, tempo_gasto, prazo_restante):
    aluno = Alunos.query.filter_by(matricula=matricula, turma=turma).first()
    if aluno != None:

        nota_antiga = Projetos.query.filter_by(id_aluno=aluno.id, nome_trabalho=nome_trabalho).first()
        #atualizar nota já existente
        if nota_antiga != None:
            nota_antiga.nota = nota
            nota_antiga.tempo_gasto = tempo_gasto
            nota_antiga.prazo_restante = str(prazo_restante)
            try:
                db.session.commit()
            except:
                return 1
            finally:
                db.session.close()
        #adicionar nova
        else:
            nova_nota = Projetos(nome_trabalho=nome_trabalho, nota=nota, id_aluno=aluno.id, tempo_gasto=tempo_gasto, prazo_restante=str(prazo_restante))
            try:
                db.session.add(nova_nota)
                db.session.commit()
            except:
                return 1
            finally:
                db.session.close()

        return 0
    return 1

def listar_alunos_trabalho(nome_turma, nome_projeto):
    lista_alunos = Alunos.query.filter_by(turma=nome_turma).order_by(Alunos.matricula).all()

    for aluno in lista_alunos:
        resultado_nota = Projetos.query.filter_by(id_aluno=aluno.id,nome_trabalho=nome_projeto).first()
        if resultado_nota != None:
            aluno.nota = resultado_nota.nota
            aluno.tempo_gasto = resultado_nota.tempo_gasto
            aluno.prazo_restante = resultado_nota.prazo_restante

            if aluno.prazo_restante == '0':
                aluno.prazo_restante = "0 dias"
            elif aluno.prazo_restante == '1':
                aluno.prazo_restante = "1 dia"
            else:
                aluno.prazo_restante = aluno.prazo_restante + " dias"
            
        lista_similaridade_jplag = Similaridades.query.filter_by(id_aluno=aluno.id,nome_trabalho=nome_projeto, ferramenta="jplag").all()
        if lista_similaridade_jplag != None:
            sim = 0
            for similaridade in lista_similaridade_jplag:
                if int(similaridade.percentual) > sim:
                    sim = int(similaridade.percentual)
            aluno.jplag = sim
        else:
            aluno.jplag = 0
        
        lista_similaridade_moss = Similaridades.query.filter_by(id_aluno=aluno.id,nome_trabalho=nome_projeto, ferramenta="moss").all()
        if lista_similaridade_moss != None:
            sim = 0
            for similaridade in lista_similaridade_moss:
                if int(similaridade.percentual) > sim:
                    sim = int(similaridade.percentual)
            aluno.moss = sim
        else:
            aluno.moss = 0
        
        aluno.existe_codigo = arquivos.existeArquivoTrabalho(nome_projeto, nome_turma, aluno.matricula+".py")
        if (aluno.existe_codigo):
            aluno.numero_linhas = arquivos.contaLinhasCodigo(nome_projeto, nome_turma, aluno.matricula+".py")
    
    db.session.close()
    return lista_alunos


#gera relatório resultados ferramentas
def listar_resultados_ferramentas(nome_turma, nome_projeto):
    lista_resultado = []
    lista_similaridades = Similaridades.query.filter_by(turma=nome_turma,nome_trabalho=nome_projeto).all()

    class elemento():
        nome1 = ""
        grupo1 = ""
        matricula1 = ""
        nota1 = ""
        jplag1 = 0
        moss1 = 0
        nome2 = ""
        grupo2 = ""
        matricula2 = ""
        nota2 = ""
        jplag2 = 0
        moss2 = 0

    for similaridade in lista_similaridades:
        alunoA = Alunos.query.filter_by(id=similaridade.id_aluno).first()
        alunoB = Alunos.query.filter_by(turma=nome_turma, matricula=similaridade.matricula_outro_aluno).first()
        #pesquisar se os dois já estão na tabela (pode ser invertido)
        encontrou = False
        if lista_resultado != []:
            for resultado in lista_resultado:
                if (resultado.matricula1 == alunoA.matricula) and (resultado.matricula2 == alunoB.matricula):
                    # alunoA e alunoB já estão na tabela
                    if similaridade.ferramenta == "jplag":
                        resultado.jplag1 = similaridade.percentual
                    elif similaridade.ferramenta == "moss":
                        resultado.moss1 = similaridade.percentual
                    encontrou = True
                    break
                elif (resultado.matricula1 == alunoB.matricula) and (resultado.matricula2 == alunoA.matricula):
                    # alunoA e alunoB estão na tabela invertidos
                    if similaridade.ferramenta == "jplag":
                        resultado.jplag2 = similaridade.percentual
                    elif similaridade.ferramenta == "moss":
                        resultado.moss2 = similaridade.percentual
                    encontrou = True
                    break
        
        if encontrou == False:
            #adicionar nova linha a tabela de maneira trivial
            aux = elemento()
            aux.nome1 = alunoA.nome
            aux.grupo1 = alunoA.grupo
            aux.matricula1 = alunoA.matricula
            aux.nota1 = Projetos.query.filter_by(id_aluno=alunoA.id,nome_trabalho=nome_projeto).first()
            if similaridade.ferramenta == "jplag":
                aux.jplag1 = similaridade.percentual
            elif similaridade.ferramenta == "moss":
                aux.moss1 = similaridade.percentual
            aux.nome2 = alunoB.nome
            aux.grupo2 = alunoB.grupo
            aux.matricula2 = alunoB.matricula
            aux.nota2 = Projetos.query.filter_by(id_aluno=alunoB.id,nome_trabalho=nome_projeto).first()
            lista_resultado.append(aux)
    
    db.session.close()
    return lista_resultado
        

def listarTurmas():
    class resultado():
        nome = ""
        projetos = 0
    
    lista_resultado = []

    lista_turmas = db.session.query(Alunos.turma).distinct().all()
    for elemento in lista_turmas:
        aux = resultado()
        aux.nome = elemento.turma
        #buscar o numero de trabalhos para essa turma
        trabs = set([])
        lista_alunos = Alunos.query.filter_by(turma=elemento.turma).all()
        for aluno in lista_alunos:

            lista_trabalhos = Projetos.query.filter_by(id_aluno=aluno.id).all()
            for trabalho in lista_trabalhos:
                trabs.add(trabalho.nome_trabalho)

        aux.projetos = len(trabs)
        lista_resultado.append(aux)
    
    db.session.close()
    return lista_resultado

def apagarResultadosFerramenta(nomeTrabalho, nomeTurma, ferramenta):

    registro_ferramenta = RegistrosFerramentas.query.filter_by(nome_trabalho=nomeTrabalho,turma=nomeTurma, ferramenta=ferramenta).first()
    if registro_ferramenta != None:
        try:
            db.session.delete(registro_ferramenta)
            db.session.commit()
        except:
            print ("erro deletar banco de dados - registro ferramenta")
        

    lista_similaridades = Similaridades.query.filter_by(turma=nomeTurma,nome_trabalho=nomeTrabalho,ferramenta=ferramenta).all()
    try:
        for similaridade in lista_similaridades:
            db.session.delete(similaridade)
        db.session.commit()
    except:
        print ("Erro deletar banco de dados - lista similaridade")


def apagarTrabalhoTurma(nomeTrabalho, nomeTurma):

    #apagar na tabela similaridade e registros
    apagarResultadosFerramenta(nomeTrabalho,nomeTurma,"jplag")
    apagarResultadosFerramenta(nomeTrabalho,nomeTurma,"moss")
    
    #apagar em Projetos, necessario identificar ids dos alunos primeiro
    lista_alunos = Alunos.query.filter_by(turma=nomeTurma).all()
    for aluno in lista_alunos:
        notas_apagar = Projetos.query.filter_by(id_aluno=aluno.id, nome_trabalho=nomeTrabalho).all()
        try:
            for nota in notas_apagar:
                db.session.delete(nota)
            db.session.commit()
        except:
            print ("Erro deletar banco de dados - Projetos")
        finally:
            db.session.close()

def listar_resultados_ferramentas_antigo(nome_turma, nome_projeto):

    lista_resultado = []
    lista_alunos = Alunos.query.filter_by(turma=nome_turma).order_by(Alunos.matricula).all()

    class elemento():
        nome1 = ""
        grupo1 = ""
        matricula1 = ""
        nota1 = ""
        jplag1 = 0
        moss1 = 0
        nome2 = ""
        grupo2 = ""
        matricula2 = ""
        nota2 = ""
        jplag2 = 0
        moss2 = 0

    for aluno in lista_alunos:
        aux = elemento()
        aux.nome1 = aluno.nome
        aux.grupo1 = aluno.grupo
        aux.matricula1 = aluno.matricula
        aux.nota1 = Projetos.query.filter_by(id_aluno=aluno.id,nome_trabalho=nome_projeto).first()


        similaridade_jplag = Similaridades.query.filter_by(id_aluno=aluno.id,nome_trabalho=nome_projeto, ferramenta="jplag").first()
        if similaridade_jplag != None:
            aux.jplag1 = similaridade_jplag.percentual
            
            aux.matricula2 = similaridade_jplag.matricula_outro_aluno
            aluno_outro = Alunos.query.filter_by(turma=nome_turma, matricula=aux.matricula2).first()
            if aluno_outro != None:
                aux.nome2 = aluno_outro.nome
                aux.grupo2 = aluno_outro.grupo
                aux.nota2 = Projetos.query.filter_by(id_aluno=aluno_outro.id,nome_trabalho=nome_projeto).first()

        similaridade_moss = Similaridades.query.filter_by(id_aluno=aluno.id,nome_trabalho=nome_projeto, ferramenta="moss").first()
        if similaridade_moss != None:
            
            if (aux.matricula2 == ""):
                aux.moss1 = similaridade_moss.percentual
                aux.matricula2 = similaridade_moss.matricula_outro_aluno
                aluno_outro = Alunos.query.filter_by(turma=nome_turma, matricula=aux.matricula2).first()
                if aluno_outro != None:
                    aux.nome2 = aluno_outro.nome
                    aux.grupo2 = aluno_outro.grupo
                    aux.nota2 = Projetos.query.filter_by(id_aluno=aluno_outro.id,nome_trabalho=nome_projeto).first()

            else:
                matricula_outro = similaridade_moss.matricula_outro_aluno
                if (matricula_outro == aux.matricula2):
                    aux.moss1 = similaridade_moss.percentual
                else: #quando o moss e o jplag não concordam, adicionar duas linhas
                    aux2 = elemento()
                    aux2.nome1 = aux.nome1
                    aux2.grupo1 = aux.grupo1
                    aux2.matricula1 = aux.matricula1
                    aux2.nota1 = aux.nota1
                    aux2.moss1 = similaridade_moss.percentual
                    aux2.matricula2 = similaridade_moss.matricula_outro_aluno
                    aluno_outro = Alunos.query.filter_by(turma=nome_turma, matricula=aux2.matricula2).first()
                    if aluno_outro != None:
                        aux2.nome2 = aluno_outro.nome
                        aux2.grupo2 = aluno_outro.grupo
                        aux2.nota2 = Projetos.query.filter_by(id_aluno=aluno_outro.id,nome_trabalho=nome_projeto).first()
                    lista_resultado.append(aux2)

        lista_resultado.append(aux)

    db.session.close()
    return lista_resultado


def listarDadosGrafoFerramentas(nome_turma, nome_projeto, ferramenta, percentual_minimo): #a principio recebe a ferramenta via parametro
    #para cada dupla de alunos, descobrir a maior similaridade e usar ela (direção da seta)
    # 30% - 1
    # 40% - 2
    # 50% - 3
    # 60% - 4
    # 70% - 5
    # 80% - 6
    # 90% - 7

    # primeiro nome e ultimo sobrenome, mátricula, similaridade

    class elemento():
        nome1 = ""
        matricula1 = ""
        similaridade = 0
        nome2 = ""
        matricula2 = ""

    lista_resultado = []
    lista_similaridades = Similaridades.query.filter_by(turma=nome_turma,nome_trabalho=nome_projeto, ferramenta=ferramenta).all()

    for similaridade in lista_similaridades:
        if int(similaridade.percentual) >= int(percentual_minimo):
            alunoA = Alunos.query.filter_by(id=similaridade.id_aluno).first()
            alunoB = Alunos.query.filter_by(turma=nome_turma, matricula=similaridade.matricula_outro_aluno).first()
            jaExiste = False
            for resultado in lista_resultado:
                if ((resultado.matricula1 == alunoA.matricula) and (resultado.matricula2 == alunoB.matricula)) or((resultado.matricula1 == alunoB.matricula) and (resultado.matricula2 == alunoA.matricula)):
                    jaExiste = True
                    if int(similaridade.percentual) > int(resultado.similaridade):
                        resultado.similaridade = similaridade.percentual
                        resultado.nome1 = alunoA.nome
                        resultado.nome2 = alunoB.nome
                        resultado.matricula1 = alunoA.matricula
                        resultado.matricula2 = alunoB.matricula
                    break
            if jaExiste == False:
                aux = elemento()
                aux.similaridade = similaridade.percentual
                aux.nome1 = alunoA.nome
                aux.nome2 = alunoB.nome
                aux.matricula1 = alunoA.matricula
                aux.matricula2 = alunoB.matricula
                lista_resultado.append(aux)
    db.session.close()
    return lista_resultado


def insereResultadosBanco(resultados, nomeTrabalho, nomeTurma, ferramenta):
    for resultado in resultados:
        matricula = resultado[0]
        if matricula.endswith(".py"):
            matricula = matricula[:-3]
        percentual = resultado[1]

        matricula_outro = resultado[2]
        if matricula_outro.endswith(".py"):
            matricula_outro = matricula_outro[:-3]

        aluno = Alunos.query.filter_by(turma=nomeTurma, matricula=matricula).first()
        if aluno != None:
            nova_similaridade = Similaridades(nome_trabalho=nomeTrabalho, percentual=percentual, turma=nomeTurma, ferramenta=ferramenta, id_aluno=str(aluno), matricula_outro_aluno=matricula_outro)
            try:
                db.session.add(nova_similaridade)
                db.session.commit()
            except:
                print ("Erro inserção BD - nova similaridade")
            finally:
                db.session.close()
    

def buscaRelatorioAluno(matricula, turma):
    result = []
    aluno = Alunos.query.filter_by(turma=turma, matricula=matricula).first()
    class elemento():
        nome_trabalho = ""
        nota = ""
        tempo_gasto = ""
        prazo_restante = ""
        jplag = 0
        moss = 0
        existe_codigo = False
        numero_linhas = 0

    if aluno != None:
        notas = Projetos.query.filter_by(id_aluno=aluno.id).order_by(Projetos.nome_trabalho).all()
        for resultado_nota in notas:
            elemento_result = elemento()

            elemento_result.nome_trabalho = resultado_nota.nome_trabalho
            elemento_result.nota = resultado_nota.nota
            elemento_result.tempo_gasto = resultado_nota.tempo_gasto
            
            
            if (resultado_nota.prazo_restante == '0'):
                elemento_result.prazo_restante = "0 dias"
            elif (resultado_nota.prazo_restante == '1'):
                elemento_result.prazo_restante = "1 dia"
            else:
                elemento_result.prazo_restante = resultado_nota.prazo_restante + " dias"

            lista_similaridade_jplag = Similaridades.query.filter_by(id_aluno=aluno.id,nome_trabalho=resultado_nota.nome_trabalho, ferramenta="jplag").all()
            if lista_similaridade_jplag != None:
                sim = 0
                for similaridade in lista_similaridade_jplag:
                    if int(similaridade.percentual) > sim:
                        sim = int(similaridade.percentual)
                elemento_result.jplag = sim
            else:
                elemento_result.jplag = 0

            lista_similaridade_moss = Similaridades.query.filter_by(id_aluno=aluno.id,nome_trabalho=resultado_nota.nome_trabalho, ferramenta="moss").all()
            if lista_similaridade_moss != None:
                sim = 0
                for similaridade in lista_similaridade_moss:
                    if int(similaridade.percentual) > sim:
                        sim = int(similaridade.percentual)
                elemento_result.moss = sim
            else:
                elemento_result.moss = 0
            
            elemento_result.existe_codigo = arquivos.existeArquivoTrabalho(resultado_nota.nome_trabalho, turma, matricula+".py")
            if (elemento_result.existe_codigo):
                elemento_result.numero_linhas = arquivos.contaLinhasCodigo(resultado_nota.nome_trabalho, turma, matricula+".py")
            result.append(elemento_result)

    db.session.close()
    return result


def gera_relatorio_geral(turma):

    lista_resultado = []

    class elemento:
        def __init__(self):
            self.nome_aluno = ""
            self.matricula = ""
            self.grupo = ""
            self.nomes_trabalhos = []
            self.notas_trabalhos = []
            self.similaridade_jplag = []
            self.similaridade_moss = []

            #serão inseridos novos campos

    lista_alunos = Alunos.query.filter_by(turma=turma).order_by(Alunos.matricula).all()
    for aluno in lista_alunos:
        aux = elemento()
        aux.nome_aluno = aluno.nome
        aux.grupo = aluno.grupo
        aux.matricula = aluno.matricula
        lista_trabalhos = Projetos.query.filter_by(id_aluno=aluno.id).order_by(Projetos.nome_trabalho).all()
        for trabalho in lista_trabalhos:
            aux.nomes_trabalhos.append(trabalho.nome_trabalho)
            aux.notas_trabalhos.append(trabalho.nota)
            
            aux.similaridade_jplag.append('0')
            aux.similaridade_moss.append('0')

            similaridades = Similaridades.query.filter_by(id_aluno=aluno.id, nome_trabalho=trabalho.nome_trabalho).all()
            for similaridade in similaridades:
                if similaridade.ferramenta == "moss":
                    aux.similaridade_moss[-1] = similaridade.percentual
                elif similaridade.ferramenta == "jplag":
                    aux.similaridade_jplag[-1] = similaridade.percentual
        lista_resultado.append(aux)

    db.session.close()
    return lista_resultado


def insereRegistroFerrameta(nomeTrabalho, nomeTurma, ferramenta):
    registro_ferramenta = RegistrosFerramentas.query.filter_by(nome_trabalho=nomeTrabalho,turma=nomeTurma, ferramenta=ferramenta).first()
    if registro_ferramenta != None:
        registro_ferramenta.data_execucao = datetime.now()
        try:
            db.session.commit()
        except:
            print ("Erro atualização BD - registro ferramentas")
    else:
        novo_registro = RegistrosFerramentas(nome_trabalho=nomeTrabalho,turma=nomeTurma,ferramenta=ferramenta)
        try:
            db.session.add(novo_registro)
            db.session.commit()
        except:
            print ("Erro inserção BD - registro ferramentas")
    db.session.close()

def buscaRegistroFerramenta(nomeTrabalho, nomeTurma, ferramenta):
    registro_ferramenta = RegistrosFerramentas.query.filter_by(nome_trabalho=nomeTrabalho,turma=nomeTurma, ferramenta=ferramenta).first()
    db.session.close()
    return registro_ferramenta

def buscaNomeAluno(matricula, turma):
    aluno = Alunos.query.filter_by(matricula=matricula, turma=turma).first()
    if aluno != None:
        db.session.close()
        return aluno.nome    
        
    db.session.close()
    return
