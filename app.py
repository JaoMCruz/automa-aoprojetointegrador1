import streamlit as st
import pandas as pd

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
    st.warning("Processamento será integrado na próxima etapa.")