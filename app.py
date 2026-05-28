import streamlit as st
from main import (
    processar_planilha,
    atualizar_totais_diarios,
    recalcular_resultado,
    gerar_excel,
    processar_folha_manual_ia
)

st.set_page_config(
    page_title="Sistema de Horas Extras",
    page_icon="⏱️",
    layout="wide"
)

st.title("Sistema Automático de Cálculo - Horas Extras")

st.markdown("""
Sistema para leitura da planilha do relógio ponto, conferência dos horários,
leitura de folha manual com IA e geração automática do relatório de horas extras.
""")

st.divider()

planilha = st.file_uploader(
    "Envie a planilha do relógio ponto",
    type=["xlsx"]
)

folha_manual = st.file_uploader(
    "Envie a folha ponto manual",
    type=["png", "jpg", "jpeg", "pdf"],
    accept_multiple_files=True
)

if planilha:
    st.success("Planilha carregada com sucesso!")

if folha_manual:
    st.info(f"{len(folha_manual)} folha(s) manual(is) carregada(s).")

    if st.button("Ler folha manual com IA"):

        arquivo = folha_manual[0]

        with open("folha_temp.jpg", "wb") as f:
            f.write(arquivo.getbuffer())

        try:
            with st.spinner("Lendo folha manual com IA..."):
                df_ia = processar_folha_manual_ia("folha_temp.jpg")

            st.session_state["df_ia"] = df_ia

            st.success("Folha manual lida com IA!")

        except Exception as erro:
            st.error("A IA está indisponível no momento. Tente novamente em alguns instantes.")
            st.caption(f"Detalhe técnico: {erro}")

if st.button("Processar horas"):

    if planilha:

        with st.spinner("Processando planilha..."):
            df_diario, df_resultado = processar_planilha(planilha)

        st.session_state["df_diario"] = df_diario
        st.session_state["df_resultado"] = df_resultado

        st.success("Processamento concluído!")

    else:
        st.error("Envie uma planilha primeiro.")

if "df_diario" in st.session_state:

    st.divider()

    df_diario = st.session_state["df_diario"]

    funcionarios = sorted(df_diario["Funcionário"].unique())

    funcionario_selecionado = st.selectbox(
        "Selecione um funcionário para visualizar",
        funcionarios
    )

    df_funcionario = df_diario[
        df_diario["Funcionário"] == funcionario_selecionado
    ].copy()

    indices_originais = df_funcionario.index
    df_funcionario = df_funcionario.reset_index(drop=True)

    st.subheader("Resultado Diário")

    with st.form("form_edicao"):

        df_editado = st.data_editor(
            df_funcionario,
            width="stretch",
            hide_index=True,
            num_rows="fixed"
        )

        salvar = st.form_submit_button(
            "Salvar alterações e recalcular"
        )

    if salvar:

        st.session_state["df_diario"].loc[
            indices_originais,
            df_editado.columns
        ] = df_editado.values

        st.session_state["df_diario"] = atualizar_totais_diarios(
            st.session_state["df_diario"]
        )

        st.session_state["df_resultado"] = recalcular_resultado(
            st.session_state["df_diario"]
        )

        st.success("Alterações salvas e resultados recalculados!")
        st.rerun()

    if "df_ia" in st.session_state:

        st.divider()

        st.subheader("Resultado da IA")

        st.dataframe(
            st.session_state["df_ia"],
            width="stretch",
            hide_index=True
        )

        if st.button("Aplicar horários da IA no funcionário selecionado"):

            df_ia = st.session_state["df_ia"]

            for _, linha in df_ia.iterrows():

                dia = linha["dia"]

                entrada = linha["entrada"]
                saida_almoco = linha["saida_almoco"]
                volta_almoco = linha["volta_almoco"]
                saida_final = linha["saida_final"]

                if (
                    entrada is None or
                    saida_almoco is None or
                    volta_almoco is None or
                    saida_final is None
                ):
                    continue

                filtro = (
                    (st.session_state["df_diario"]["Funcionário"] == funcionario_selecionado) &
                    (st.session_state["df_diario"]["Dia"] == dia) &
                    (st.session_state["df_diario"]["Status"] == "Pendente")
                )

                st.session_state["df_diario"].loc[filtro, "Entrada"] = entrada
                st.session_state["df_diario"].loc[filtro, "Saída Almoço"] = saida_almoco
                st.session_state["df_diario"].loc[filtro, "Volta Almoço"] = volta_almoco
                st.session_state["df_diario"].loc[filtro, "Saída Final"] = saida_final

            st.session_state["df_diario"] = atualizar_totais_diarios(
                st.session_state["df_diario"]
            )

            st.session_state["df_resultado"] = recalcular_resultado(
                st.session_state["df_diario"]
            )

            st.success("Horários da IA aplicados apenas nos dias pendentes!")
            st.rerun()

    st.divider()

    st.subheader("Resultado Final")

    st.dataframe(
        st.session_state["df_resultado"],
        width="stretch",
        hide_index=True
    )

    excel = gerar_excel(
        st.session_state["df_diario"],
        st.session_state["df_resultado"]
    )

    st.download_button(
        "Baixar relatório Excel",
        data=excel,
        file_name="resultado_horas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )