import pandas as pd
import re
from datetime import datetime, timedelta
from io import BytesIO
import calendar


def formatar_tempo(tempo):
    total_segundos = int(tempo.total_seconds())
    sinal = "-" if total_segundos < 0 else ""
    total_segundos = abs(total_segundos)

    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60

    return f"{sinal}{horas:02d}:{minutos:02d}:{segundos:02d}"


def calcular_total_dia(entrada, saida_almoco, volta_almoco, saida_final):
    formato = "%H:%M"

    entrada_dt = datetime.strptime(entrada, formato)
    saida_almoco_dt = datetime.strptime(saida_almoco, formato)
    volta_almoco_dt = datetime.strptime(volta_almoco, formato)
    saida_final_dt = datetime.strptime(saida_final, formato)

    periodo_manha = saida_almoco_dt - entrada_dt
    periodo_tarde = saida_final_dt - volta_almoco_dt

    return periodo_manha + periodo_tarde


def completar_horarios(horarios):
    if len(horarios) == 4:
        return horarios

    if len(horarios) == 3:
        if horarios[0] < "12:00" and horarios[1] >= "12:00" and horarios[2] >= "17:00":
            return [horarios[0], "11:45", horarios[1], horarios[2]]

        return [horarios[0], horarios[1], horarios[2], "18:00"]

    if len(horarios) == 2:
        if horarios[0] >= "12:00":
            return ["07:30", "11:45", horarios[0], horarios[1]]

        return [horarios[0], horarios[1], "13:15", "18:00"]

    if len(horarios) == 1:
        return [horarios[0], "11:45", "13:15", "18:00"]

    return horarios


def completar_semanas_com_dia_zero(df_diario, ano, mes):
    df_diario = df_diario[
        df_diario["Status"] != "Padrão"
    ]

    linhas_extras = []

    ultimo_dia_mes = calendar.monthrange(ano, mes)[1]

    primeiro_dia = datetime(ano, mes, 1)
    ultimo_dia = datetime(ano, mes, ultimo_dia_mes)

    dias_semana = [
        "Segunda",
        "Terça",
        "Quarta",
        "Quinta",
        "Sexta",
        "Sábado",
        "Domingo"
    ]

    dias_antes = (primeiro_dia.weekday() + 1) % 7
    dias_depois = 6 - ((ultimo_dia.weekday() + 1) % 7)

    funcionarios = df_diario["Funcionário"].unique()

    for funcionario in funcionarios:

        for i in range(dias_antes):
            data_zero = primeiro_dia - timedelta(days=dias_antes - i)

            linhas_extras.append({
                "Dia Semana": dias_semana[data_zero.weekday()],
                "Funcionário": funcionario,
                "Dia": 0,
                "Semana": int(data_zero.strftime("%U")),
                "Entrada": "07:30",
                "Saída Almoço": "11:45",
                "Volta Almoço": "13:15",
                "Saída Final": "18:00",
                "Total do Dia": "09:00:00",
                "Saldo do Dia": "00:00:00",
                "Status": "Padrão"
            })

        for i in range(dias_depois):
            data_zero = ultimo_dia + timedelta(days=i + 1)

            linhas_extras.append({
                "Dia Semana": dias_semana[data_zero.weekday()],
                "Funcionário": funcionario,
                "Dia": 0,
                "Semana": int(data_zero.strftime("%U")),
                "Entrada": "07:30",
                "Saída Almoço": "11:45",
                "Volta Almoço": "13:15",
                "Saída Final": "18:00",
                "Total do Dia": "09:00:00",
                "Saldo do Dia": "00:00:00",
                "Status": "Padrão"
            })

    if linhas_extras:
        df_diario = pd.concat(
            [df_diario, pd.DataFrame(linhas_extras)],
            ignore_index=True
        )

    return df_diario

def processar_planilha(arquivo):
    df = pd.read_excel(arquivo, sheet_name="Relógio")

    carga_horaria_diaria = timedelta(hours=9)
    dados_diarios = []

    periodo = str(df.iloc[1, 2])
    datas = re.findall(r'(\d{4})/(\d{1,2})/\d{1,2}', periodo)

    ano = int(datas[0][0])
    mes = int(datas[0][1])

    linha_dias = df.iloc[2]

    dias_colunas = []

    for coluna in df.columns:
        valor = linha_dias[coluna]

        if str(valor).replace(".0", "").isdigit():
            dia = int(float(valor))
            dias_colunas.append((dia, coluna))

    funcionario = "Desconhecido"

    for index, linha in df.iterrows():

        primeira_coluna = str(linha.iloc[0]).strip()

        if primeira_coluna == "ID":
            nome = str(linha.iloc[10]).strip()

            if nome.lower() != "nan":
                funcionario = nome

            continue

        for dia, coluna in dias_colunas:
            valor = str(linha[coluna])
            horarios = re.findall(r'\d{2}:\d{2}', valor)

            data = datetime(ano, mes, dia)

            dias_semana = [
                "Segunda",
                "Terça",
                "Quarta",
                "Quinta",
                "Sexta",
                "Sábado",
                "Domingo"
            ]

            dia_semana = dias_semana[data.weekday()]
            final_semana = data.weekday() >= 5
            semana = int(data.strftime("%U"))

            if len(horarios) == 0:
                status = "Final de semana" if final_semana else "Pendente"

                dados_diarios.append({
                    "Dia Semana": dia_semana,
                    "Funcionário": funcionario,
                    "Dia": dia,
                    "Semana": semana,
                    "Entrada": "",
                    "Saída Almoço": "",
                    "Volta Almoço": "",
                    "Saída Final": "",
                    "Total do Dia": "00:00:00",
                    "Saldo do Dia": "00:00:00",
                    "Status": status
                })

                continue

            if not final_semana and len(horarios) < 4:
                horarios = completar_horarios(horarios)

            entrada = horarios[0] if len(horarios) > 0 else ""
            saida_almoco = horarios[1] if len(horarios) > 1 else ""
            volta_almoco = horarios[2] if len(horarios) > 2 else ""
            saida_final = horarios[3] if len(horarios) > 3 else ""

            if entrada and saida_almoco and volta_almoco and saida_final:
                total_hora_dia = calcular_total_dia(
                    entrada,
                    saida_almoco,
                    volta_almoco,
                    saida_final
                )

                saldo_dia = total_hora_dia - carga_horaria_diaria

                dados_diarios.append({
                    "Dia Semana": dia_semana,
                    "Funcionário": funcionario,
                    "Dia": dia,
                    "Semana": semana,
                    "Entrada": entrada,
                    "Saída Almoço": saida_almoco,
                    "Volta Almoço": volta_almoco,
                    "Saída Final": saida_final,
                    "Total do Dia": formatar_tempo(total_hora_dia),
                    "Saldo do Dia": formatar_tempo(saldo_dia),
                    "Status": "Calculado"
                })

    df_diario = pd.DataFrame(dados_diarios)

    funcionarios_validos = df_diario[
        df_diario["Status"] == "Calculado"
    ]["Funcionário"].unique()

    df_diario = df_diario[
        df_diario["Funcionário"].isin(funcionarios_validos)
    ]

    df_diario = completar_semanas_com_dia_zero(
        df_diario,
        ano,
        mes
    )

    df_resultado = recalcular_resultado(df_diario)

    return df_diario, df_resultado


def atualizar_totais_diarios(df_diario):
    carga_horaria_diaria = timedelta(hours=9)

    for index, linha in df_diario.iterrows():

        entrada = str(linha["Entrada"]).strip()
        saida_almoco = str(linha["Saída Almoço"]).strip()
        volta_almoco = str(linha["Volta Almoço"]).strip()
        saida_final = str(linha["Saída Final"]).strip()

        campos = [entrada, saida_almoco, volta_almoco, saida_final]

        tem_horarios = all(
            campo not in ["", "nan", "None"]
            for campo in campos
        )

        if not tem_horarios:
            df_diario.at[index, "Total do Dia"] = "00:00:00"
            df_diario.at[index, "Saldo do Dia"] = "00:00:00"

            if linha["Dia Semana"] in ["Sábado", "Domingo"]:
                df_diario.at[index, "Status"] = "Final de semana"
            else:
                df_diario.at[index, "Status"] = "Pendente"

            continue

        try:
            total_dia = calcular_total_dia(
                entrada,
                saida_almoco,
                volta_almoco,
                saida_final
            )

            saldo_dia = total_dia - carga_horaria_diaria

            df_diario.at[index, "Total do Dia"] = formatar_tempo(total_dia)
            df_diario.at[index, "Saldo do Dia"] = formatar_tempo(saldo_dia)
            df_diario.at[index, "Status"] = "Calculado"

        except Exception as erro:
            df_diario.at[index, "Total do Dia"] = "Erro"
            df_diario.at[index, "Saldo do Dia"] = "Erro"
            df_diario.at[index, "Status"] = f"Erro: {erro}"

    return df_diario
        

def recalcular_resultado(df_diario):

    dados_resultado = []

    funcionarios = df_diario["Funcionário"].unique()

    for funcionario in funcionarios:

        df_funcionario = df_diario[
            df_diario["Funcionário"] == funcionario
        ]

        saldo_total = timedelta()

        for _, linha in df_funcionario.iterrows():

            status = str(
                linha["Status"]
            ).strip().lower()

            if status not in ["calculado", "falta"]:
                continue

            if status == "falta":
                saldo_total -= timedelta(hours=9)
                continue

            saldo_texto = str(
                linha["Saldo do Dia"]
            )

            try:

                negativo = saldo_texto.startswith("-")

                saldo_texto = saldo_texto.replace(
                    "-",
                    ""
                )

                horas, minutos, segundos = map(
                    int,
                    saldo_texto.split(":")
                )

                saldo = timedelta(
                    hours=horas,
                    minutes=minutos,
                    seconds=segundos
                )

                if negativo:
                    saldo *= -1

                saldo_total += saldo

            except:
                continue

        dados_resultado.append({
            "Funcionário": funcionario,
            "Saldo Final do Mês": formatar_tempo(
                saldo_total
            )
        })

    return pd.DataFrame(dados_resultado)

def gerar_excel(df_diario, df_resultado):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        for funcionario in df_diario["Funcionário"].unique():

            df_funcionario = df_diario[
                df_diario["Funcionário"] == funcionario
            ]

            nome_aba = funcionario[:31]

            df_funcionario.to_excel(
                writer,
                sheet_name=nome_aba,
                index=False
            )

        df_resultado.to_excel(
            writer,
            sheet_name="Resultado Final",
            index=False
        )

    return output.getvalue()