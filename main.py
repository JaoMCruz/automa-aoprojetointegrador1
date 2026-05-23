import pandas as pd
import re
from datetime import datetime, timedelta

arquivo = "dados/horas.xlsx"

df = pd.read_excel(arquivo, sheet_name="Relógio")

horario_padrao = [
    "07:30",
    "11:45",
    "13:15",
    "18:00"
]

carga_horaria_padrao = 9
carga_horaria_padrao = timedelta(
    hours=carga_horaria_padrao
)


periodo = str(df.iloc[1, 2])

datas = re.findall(r'(\d{4})/(\d{1,2})/\d{1,2}', periodo)

ano = int(datas[0][0])
mes = int(datas[0][1])

linha_dias = df.iloc[2]

dias = []

for valor in linha_dias:

    if str(valor).isdigit():
        dias.append(int(valor))

funcionario = "Desconhecido"

for index, linha in df.iterrows():

    primeira_coluna = str(linha.iloc[0]).strip()

    if primeira_coluna == "ID":

        nome = str(linha.iloc[10]).strip()

        if nome.lower() != "nan":
            funcionario = nome

        continue

    for i, dia in enumerate(dias):

        coluna = df.columns[i]

        valor = str(linha[coluna])

        horarios = re.findall(r'\d{2}:\d{2}', valor)

        data = datetime(ano, mes, dia)

        final_semana = data.weekday() >= 5

        if len(horarios) == 0:

            if final_semana:
                continue

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

                    horarios.append(
                        horario_padrao[len(horarios)]
                    )

        entrada = (
            horarios[0]
            if len(horarios) > 0
            else ""
        )

        saida_almoco = (
            horarios[1]
            if len(horarios) > 1
            else ""
        )

        volta_almoco = (
            horarios[2]
            if len(horarios) > 2
            else ""
        )

        saida_final = (
            horarios[3]
            if len(horarios) > 3
            else ""
        )

        formato = "%H:%M"

        if (
            entrada and
            saida_almoco and
            volta_almoco and
            saida_final
        ):
            entrada_dt = datetime.strptime(
                entrada,
                formato
            )

            saida_almoco_dt = datetime.strptime(
                saida_almoco,
                formato
            )

            volta_almoco_dt = datetime.strptime(
                volta_almoco,
                formato
            )

            saida_final_dt = datetime.strptime(
                saida_final,
                formato
            )

            periodo_manha = (saida_almoco_dt - entrada_dt)
            periodo_tarde = (saida_final_dt -volta_almoco_dt)
            total_hora_dia =(periodo_manha + periodo_tarde)
            
            saldo_dia = (total_hora_dia - carga_horaria_padrao)
            hora_extra = timedelta()
            hora_faltante = timedelta()

            if saldo_dia > timedelta():

                hora_extra = saldo_dia

            elif saldo_dia < timedelta():

                hora_faltante = abs(saldo_dia)



        print(f"""
            Funcionário: {funcionario}
            Dia: {dia}

            Entrada: {entrada}
            Saída almoço: {saida_almoco}
            Volta almoço: {volta_almoco}
            Saída final: {saida_final}

            Período manhã: {periodo_manha}
            Período tarde: {periodo_tarde}

            Total Hora do dia: {total_hora_dia}
            Saldo do dia: {saldo_dia}
            -------------------------
            """)