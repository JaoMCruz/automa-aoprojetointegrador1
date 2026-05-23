
import pandas as pd
import re
from datetime import datetime

arquivo = "dados/horas.xlsx"

df = pd.read_excel(arquivo, sheet_name="Relógio")

horario_padrao = [
    "07:30",
    "11:45",
    "13:15",
    "18:00"
]

periodo = str(df.iloc[1, 2])

datas = re.findall(r'(\d{4})/(\d{1,2})/\d{1,2}', periodo)

ano = int(datas[0][0])
mes = int(datas[0][1])

linha_dias = df.iloc[2]

dias = []

for valor in linha_dias:

    if str(valor).isdigit():
        dias.append(int(valor))

funcionario = ""

for index, linha in df.iterrows():

    if str(linha[df.columns[0]]) == "ID":

        funcionario = str(linha[df.columns[1]]).strip()

    for i, dia in enumerate(dias):

        coluna = df.columns[i]

        valor = str(linha[coluna])

        horarios = re.findall(r'\d{2}:\d{2}', valor)

        data = datetime(ano, mes, dia)

        final_semana = data.weekday() >= 5

        if len(horarios) == 0:

            if final_semana:
                continue

            else:
                print(f"""
                Funcionário: {funcionario}
                Dia: {dia}
                Consultar folha manual
                -------------------------
                """)
                continue

        if not final_semana:

            if len(horarios) < 4:

                while len(horarios) < 4:
                    horarios.append(horario_padrao[len(horarios)])

        entrada = horarios[0] if len(horarios) > 0 else ""
        saida_almoco = horarios[1] if len(horarios) > 1 else ""
        volta_almoco = horarios[2] if len(horarios) > 2 else ""
        saida_final = horarios[3] if len(horarios) > 3 else ""

        print(f"""
            Funcionário: {funcionario}
            Dia: {dia}

            Entrada: {entrada}
            Saída almoço: {saida_almoco}
            Volta almoço: {volta_almoco}
            Saída final: {saida_final}
            -------------------------
            """)