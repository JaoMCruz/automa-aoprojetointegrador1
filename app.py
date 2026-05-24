import streamlit as st
from main import (
    processar_planilha,
    atualizar_totais_diarios,
    recalcular_resultado,
    gerar_excel
)

st.set_page_config(
    page_title="Sistema de Horas Extras",
    page_icon="⏱️",
    layout="wide"
)

st.title("Sistema Automático de Cálculo - Horas Extras")

st.markdown("""
Sistema para leitura da planilha do relógio ponto, conferência dos horários
e geração automática do relatório de horas extras.
""")

st.divider()

planilha = st.file_uploader(
    "Envie a planilha do relógio ponto",
    type=["xlsx"]
)

folha_manual = st.file_uploader(
    "Envie as folhas ponto manual",
    type=["png", "jpg", "jpeg", "pdf"],
    accept_multiple_files=True
)

if planilha:
    st.success("Planilha carregada com sucesso!")

if folha_manual:
    st.info(f"{len(folha_manual)} folha(s) manual(is) carregada(s).")

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

    df_diario = st.session_state["df_diario"]

    st.divider()

    funcionarios = sorted(df_diario["Funcionário"].unique())

    funcionario_selecionado = st.selectbox(
        "Selecione um funcionário para visualizar",
        funcionarios
    )

    df_funcionario = df_diario[
        df_diario["Funcionário"] == funcionario_selecionado
    ].copy()

    st.subheader("Resultado Diário")

    df_editado = st.data_editor(
        df_funcionario,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key=f"editor_{funcionario_selecionado}"
    )

    indices = df_funcionario.index

    st.session_state["df_diario"].loc[
        indices,
        df_editado.columns
    ] = df_editado.values

    if st.button("Recalcular planilha"):

        st.session_state["df_diario"] = atualizar_totais_diarios(
            st.session_state["df_diario"]
        )

        st.session_state["df_resultado"] = recalcular_resultado(
            st.session_state["df_diario"]
        )

        st.success("Resultados recalculados!")

    st.divider()

    st.subheader("Resultado Final")

    st.dataframe(
        st.session_state["df_resultado"],
        use_container_width=True,
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