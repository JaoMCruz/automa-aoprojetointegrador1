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

        df_atualizado = atualizar_totais_diarios(
            st.session_state["df_diario"]
        )

        st.session_state["df_diario"] = df_atualizado

        st.session_state["df_resultado"] = recalcular_resultado(
            df_atualizado
        )

        st.success("Alterações salvas e resultados recalculados!")
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