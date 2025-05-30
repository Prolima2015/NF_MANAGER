import streamlit as st
import pandas as pd
import io
import datetime
from PyPDF2 import PdfReader

st.set_page_config(page_title="Leitor de Notas Fiscais", layout="wide")
st.title("📄 Leitor e Organizador de Notas Fiscais")

st.markdown("Faça upload dos arquivos PDF das notas fiscais. O sistema tentará extrair os dados e preencher as colunas principais automaticamente.")

uploaded_files = st.file_uploader("Selecione os arquivos PDF", type="pdf", accept_multiple_files=True)

# Colunas finais da planilha
columns = [
    "Emissão", "Vencimento", "Prazo", "Fornecedor", "CNPJ Fornecedor", "CNPJ Cliente",
    "Tipo", "Descrição", "Forma de Pagamento", "Rateio", "Nota Débito"
]

data = []

# Simples função para extrair texto e simular dados (melhorado depois com padrão de regex por tipo de nota)
def extract_data_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    # Exemplos simplificados
    fornecedor = "Desconhecido"
    cnpj_fornecedor = ""
    cnpj_cliente = ""
    tipo = "Indefinido"
    descricao = "Não identificado"
    emissao = ""
    vencimento = ""

    # Simulações (substituir por regexs específicas depois)
    if "LUFT" in text:
        cnpj_cliente = "06.288.375/0001-85"
    if "NFS-e" in text:
        tipo = "NFS-e"
    if "FATURA DE LOCAÇÃO" in text:
        tipo = "Fatura"
    if "AVISO DE DÉBITO" in text:
        tipo = "Aviso de Débito"

    # Datas simuladas
    import re
    datas = re.findall(r"\d{2}/\d{2}/\d{4}", text)
    if datas:
        emissao = datas[0]
        vencimento = datas[-1] if len(datas) > 1 else datas[0]

    try:
        prazo = (pd.to_datetime(vencimento, dayfirst=True) - pd.to_datetime(emissao, dayfirst=True)).days
    except:
        prazo = ""

    return [
        emissao, vencimento, prazo, fornecedor, cnpj_fornecedor, cnpj_cliente,
        tipo, descricao, "", "", ""
    ]

if uploaded_files:
    for file in uploaded_files:
        row = extract_data_from_pdf(file)
        data.append(row)

    df = pd.DataFrame(data, columns=columns)

    edited_df = st.data_editor(df, num_rows="dynamic")

    col1, col2 = st.columns(2)
    with col1:
        csv = edited_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar como CSV", csv, "notas_fiscais.csv", "text/csv")

    with col2:
        st.info("📌 A integração com o Google Sheets será ativada na próxima versão.")
else:
    st.warning("Faça upload de pelo menos um arquivo PDF para começar.")
