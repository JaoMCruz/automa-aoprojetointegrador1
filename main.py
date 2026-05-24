import pandas as pd
import re
from datetime import datetime, timedelta

arquivo = "dados/horas.xlsx"

df = pd.read_excel(arquivo, sheet_name="Relógio")

horario_padrao = ["07:30", "11:45", "13:15", "18:00"]

carga_horaria_diaria = timedelta(hours=9)

totais_funcionarios = {}
dados_diarios = []


def formatar_tempo(tempo):
    total_segundos = int(tempo.total_seconds())
    sinal = "-" if total_segundos < 0 else ""
    total_segundos = abs(total_segundos)

    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60

    return f"{sinal}{horas:02d}:{minutos:02d}:{segundos:02d}"


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

            if funcionario not in totais_funcionarios:
                totais_funcionarios[funcionario] = {
                    "semanas": {}
                }

        continue

    for dia, coluna in dias_colunas:
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

        if not final_semana and len(horarios) < 4:
            horarios = completar_horarios(horarios)

        entrada = horarios[0] if len(horarios) > 0 else ""
        saida_almoco = horarios[1] if len(horarios) > 1 else ""
        volta_almoco = horarios[2] if len(horarios) > 2 else ""
        saida_final = horarios[3] if len(horarios) > 3 else ""

        if entrada and saida_almoco and volta_almoco and saida_final:
            formato = "%H:%M"

            entrada_dt = datetime.strptime(entrada, formato)
            saida_almoco_dt = datetime.strptime(saida_almoco, formato)
            volta_almoco_dt = datetime.strptime(volta_almoco, formato)
            saida_final_dt = datetime.strptime(saida_final, formato)

            periodo_manha = saida_almoco_dt - entrada_dt
            periodo_tarde = saida_final_dt - volta_almoco_dt
            total_hora_dia = periodo_manha + periodo_tarde
            saldo_dia = total_hora_dia - carga_horaria_diaria

            semana = ((dia - 1) // 7) + 1

            if semana not in totais_funcionarios[funcionario]["semanas"]:
                totais_funcionarios[funcionario]["semanas"][semana] = {
                    "total_trabalhado": timedelta(),
                    "dias_calculados": 0
                }

            totais_funcionarios[funcionario]["semanas"][semana]["total_trabalhado"] += total_hora_dia
            totais_funcionarios[funcionario]["semanas"][semana]["dias_calculados"] += 1

            dados_diarios.append({
                "Funcionário": funcionario,
                "Dia": dia,
                "Entrada": entrada,
                "Saída Almoço": saida_almoco,
                "Volta Almoço": volta_almoco,
                "Saída Final": saida_final,
                "Total do Dia": formatar_tempo(total_hora_dia),
                "Saldo do Dia": formatar_tempo(saldo_dia)
            })

dados_resultado = []

for funcionario, dados in totais_funcionarios.items():
    saldo_final_mes = timedelta()

    for semana, totais in dados["semanas"].items():
        total_semana = totais["total_trabalhado"]
        dias_calculados = totais["dias_calculados"]

        carga_semana = carga_horaria_diaria * dias_calculados
        saldo_semana = total_semana - carga_semana

        saldo_final_mes += saldo_semana

    dados_resultado.append({
        "Funcionário": funcionario,
        "Saldo Final do Mês": formatar_tempo(saldo_final_mes)
    })

df_diario = pd.DataFrame(dados_diarios)
df_resultado = pd.DataFrame(dados_resultado)

print("\n===== RESULTADO DIÁRIO =====")
print(df_diario.to_string(index=False))

print("\n===== RESULTADO FINAL =====")
print(df_resultado.to_string(index=False))

with pd.ExcelWriter("resultado_horas.xlsx", engine="openpyxl") as writer:

    for funcionario in df_diario["Funcionário"].unique():

        df_funcionario = df_diario[
            df_diario["Funcionário"] == funcionario
        ]

        df_funcionario.to_excel(
            writer,
            sheet_name=funcionario[:31],
            index=False
        )

    df_resultado.to_excel(
        writer,
        sheet_name="Resultado Final",
        index=False
    )