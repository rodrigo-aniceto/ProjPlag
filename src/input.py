import pandas as pd
import baseDados
import arquivos
import ferramentas
from datetime import date


def calcula_diferenca_data(data_inicial, data_final):
    dia1 = int(data_inicial[:2])
    mes1 = int(data_inicial[3:5])
    ano1 = int(data_inicial[6:])

    dia2 = int(data_final[:2])
    mes2 = int(data_final[3:5])
    ano2 = int(data_final[6:])

    #print (str(dia1)+ " - " +str(mes1)+ " - "+str(ano1))
    #print (str(dia2)+ " - " +str(mes2)+ " - "+str(ano2))
    
    d1 = date(ano1, mes1, dia1)
    d2 = date(ano2, mes2, dia2)
    delta = d2 - d1
    #print("diferença de dias: "+str(delta.days))
    return delta.days

def mes_para_numero(mes):
    if mes == "janeiro": mes = "01"
    elif mes == "fevereiro": mes = "02"
    elif mes == "março": mes = "03"
    elif mes == "abril": mes = "04"
    elif mes == "maio": mes = "05"
    elif mes == "junho": mes = "06"
    elif mes == "julho": mes = "07"
    elif mes == "agosto": mes = "08"
    elif mes == "setembro": mes = "09"
    elif mes == "outubro": mes = "10"
    elif mes == "novembro": mes = "11"
    elif mes == "dezembro": mes = "12"
    else: mes = "00"

    return mes
    

def converte_data(data):
    dia = data.split()[0]
    mes = data.split()[1]
    ano = data.split()[2]

    if len(dia) == 1: dia = "0"+dia
    mes = mes_para_numero(mes) 

    data = dia+"/"+mes+"/"+ano
    return data

def inserir_planilha_projeto(turma, nome_arquivo, data_final, trabalho):

    data_final = converte_data(data_final)
    print ("data final: "+data_final)

    arquivos.criar_turma (turma)
    arquivos.criar_trabalho_turma(trabalho, turma)

    df = pd.read_csv("../input/"+nome_arquivo)

    print(len(df.index))

    for i in range(0,len(df.index)):
        #print('Nome: ' + df['Nome'][i])
        #print('Sobrenome: ' + df['Sobrenome'][0])
        #print('Endereço de email: ' + df['Endereço de email'][0])
        #print('Estado: ' + df['Estado'][0])
        #print('Iniciado em: ' + df['Iniciado em'][0])
        #print('Completo: ' + df['Completo'][0])
        #print('Tempo utilizado: ' + df['Tempo utilizado'][0]), 
        #print('Avaliar - nota: ' + df['Avaliar/10,00'][0])

        #print('Resposta' + df['Resposta 1'][0])

        nome = df['Nome'][i] + " " + df['Sobrenome'][i]
        matricula = df['Endereço de email'][i].split('@',1)[0]
        nota = df['Avaliar/10,00'][i].replace(',','.')
        data_entregue = converte_data(df['Completo'][i])
        tempo_gasto = df['Tempo utilizado'][i]

        prazo_restante = calcula_diferenca_data(data_entregue, data_final)
        #print ("Prazo restante: "+str(prazo_restante)+ " e tempo usado: "+tempo_gasto)

        print (nome+" - "+matricula+ " nota: "+nota+" tempo gasto: "+tempo_gasto+" prazo restante: "+str(prazo_restante))
        if matricula.isnumeric() == True: # evitar matriculas falsas
            baseDados.inserir_novo_aluno(nome, matricula, turma, "")
            baseDados.inserir_nova_nota_projeto(matricula, nota, turma, trabalho, tempo_gasto, prazo_restante)

            arquivos.escreve_codigo_trabalho(matricula + ".py", trabalho, turma, df['Resposta 1'][i])



def inserir_planilha_questionario(turma, nome_arquivo, questionario):

    df = pd.read_csv("../input/"+nome_arquivo)

    print(len(df.index))

    for i in range(0,len(df.index)-1):

        nome = df['Nome'][i] + " " + df['Sobrenome'][i]
        matricula = df['Endereço de email'][i].split('@',1)[0]
        nota = df['Avaliar/10,00'][i].replace(',','.')

        print ("nome: "+nome+" matricula: "+matricula+" nota: "+nota)

        baseDados.inserir_novo_aluno(nome, matricula, turma, "")
        baseDados.inserir_nova_nota_questionario(matricula, nota, turma, questionario)
