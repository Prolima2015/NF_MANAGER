import streamlit as st
import pandas as pd
import io
import datetime
import re
from PyPDF2 import PdfReader

st.set_page_config(page_title="Leitor de Notas Fiscais", layout="wide")
st.title("📄 Leitor e Organizador de Notas Fiscais")

st.markdown("Faça upload dos arquivos PDF das notas fiscais. O sistema tentará extrair os dados e preencher as colunas principais automaticamente.")

uploaded_files = st.file_uploader("Selecione os arquivos PDF", type="pdf", accept_multiple_files=True)

columns = [
    "Emissão", "Vencimento", "Prazo", "Fornecedor", "CNPJ Fornecedor", "CNPJ Cliente",
    "Tipo", "Descrição", "Forma de Pagamento", "Rateio", "Nota Débito"
]

data = []

# Função aprimorada de extração

def extract_data_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    fornecedor = "Desconhecido"
    cnpj_fornecedor = ""
    cnpj_cliente = ""
    tipo = "Indefinido"
    descricao = "Não identificado"
    emissao = ""
    vencimento = ""

    # Identificação do tipo da nota com padrões expandidos
    tipos_detectados = {
        "NFS-e": ["NFS-e", "SERVIÇO ELETRÔNICA", "NOTA FISCAL DE SERVIÇO"],
        "NF-e": ["NF-e", "DANFE", "NOTA FISCAL ELETRÔNICA"],
        "NFFS-e": ["FATURA DE SERVIÇOS ELETRÔNICA", "NFFS-e"],
        "Fatura": ["FATURA DE LOCAÇÃO", "FATURA DE SERVIÇO", "FATURA"],
        "Aviso de Débito": ["AVISO DE DÉBITO"],
        "CT-e": ["CONHECIMENTO DE TRANSPORTE ELETRÔNICO", "CT-e"],
        "NFC-e": ["NFC-e", "CONSUMIDOR", "NOTA FISCAL AO CONSUMIDOR"],
        "NF3-e": ["ENERGIA ELÉTRICA", "NF3-e"],
        "MDF-e": ["MANIFESTO DE DOCUMENTOS FISCAIS", "MDF-e"],
        "NFA-e": ["NOTA FISCAL AVULSA"],
        "Complementar": ["NOTA FISCAL COMPLEMENTAR"],
        "Exportação": ["NOTA FISCAL DE EXPORTAÇÃO"],
        "Remessa": ["NOTA FISCAL DE REMESSA"],
        "Devolução": ["NOTA FISCAL DE DEVOLUÇÃO"],
        "Anulação": ["NOTA FISCAL DE ANULAÇÃO"],
        "Consignação": ["VENDA POR CONSIGNAÇÃO"]
    }

    for k, v in tipos_detectados.items():
        if any(palavra in text.upper() for palavra in v):
            tipo = k
            break

    # CNPJs
    cnpjs = re.findall(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", text)
    if cnpjs:
        cnpj_fornecedor = cnpjs[0]
        if len(cnpjs) > 1:
            if cnpjs[1] != cnpj_fornecedor:
                cnpj_cliente = cnpjs[1]
            elif len(cnpjs) > 2:
                cnpj_cliente = cnpjs[2]

    # Fornecedor - tentar encontrar uma linha em maiúsculas com nome comercial
    fornecedor_match = re.search(r"(?:Raz[aã]o Social|Emitente|Fornecedor)[^\n]*\n([A-Z][A-Z\s&ÇÕÁÉÍÚÔÂÃ\-\.]{5,})", text)
    if fornecedor_match:
        fornecedor = fornecedor_match.group(1).strip()

    # Datas - pegar a primeira e última válidas
    datas = re.findall(r"\d{2}/\d{2}/\d{4}", text)
    datas_validas = []
    for d in datas:
        try:
            dt = datetime.datetime.strptime(d, "%d/%m/%Y")
            datas_validas.append(dt)
        except:
            continue

    if datas_validas:
        emissao_dt = min(datas_validas)
        vencimento_dt = max(datas_validas)
        emissao = emissao_dt.strftime("%d/%m/%Y")
        vencimento = vencimento_dt.strftime("%d/%m/%Y")
        prazo = (vencimento_dt - emissao_dt).days
    else:
        prazo = ""

    # Descrição
    descr_match = re.search(r"(?:Descri[cç][aã]o|Objeto|Referente ao)[^\n:]*[:\-\n](.*?)(\n|$)", text, re.IGNORECASE)
    if descr_match:
        descricao = descr_match.group(1).strip()

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
        st.info("📌 Integração com Google Sheets estará disponível na próxima etapa.")
else:
    st.warning("Faça upload de pelo menos um arquivo PDF para começar.")
