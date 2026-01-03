import streamlit as st
import pandas as pd
from fpdf import FPDF

# Configuração da Página
st.set_page_config(page_title="HP Expert - Diagnóstico e Conduta", layout="wide")

# --- FUNÇÃO PARA GERAR PDF ---
def generate_pdf(classe, tc6m, nt_probnp, risco_texto, conduta_texto):
    pdf = FPDF()
    pdf.add_page()
    
    # --- ADICIONAR LOGOTIPO ---
    # 'logo.png' deve estar na mesma pasta do app.py
    # Parâmetros: caminho, x, y, largura (w)
    try:
        pdf.image('cemed.png', x=10, y=8, w=88)
    except:
        # Se a imagem não for encontrada, o PDF continua sem o logo
        pass

    # Cabeçalho (ajustado para dar espaço ao logo)
    pdf.set_font("Arial", "B", 16)
    pdf.ln(20) # Pula linhas para não sobrepor o logo
    pdf.cell(0, 10, "Relatorio de Avaliacao - Hipertensão Pulmonar", ln=True, align='C')
    pdf.ln(10)
    
    # Restante do conteúdo (mesma lógica anterior)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Dados Clinicos:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Classe Funcional (NYHA/OMS): {classe}", ln=True)
    pdf.cell(0, 8, f"Teste de Caminhada (6 min): {tc6m} metros", ln=True)
    pdf.cell(0, 8, f"NT-proBNP: {nt_probnp} pg/mL", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 0, 0) # Cor preta padrão
    pdf.cell(0, 10, f"Estratificacao de Risco: {risco_texto}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Conduta Sugerida:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, conduta_texto.replace("✅", "").replace("💊", "").replace("⚠️", "").replace("🚨", ""))
    
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# --- INTERFACE DO APP ---
st.title("🩺 HP Expert: Suporte à Decisão")
st.markdown("Classificação Funcional NYHA/OMS e Estratificação de Risco")
st.divider()

# Colunas principais
col_input, col_result = st.columns([1, 1.2])

with col_input:
    st.header("1. Entrada de Dados")
    
    classe_sel = st.selectbox(
        "Classe Funcional (NYHA/OMS):",
        ["Classe I", "Classe II", "Classe III", "Classe IV"],
        help="I: Sem limitações | IV: Sintomas em repouso"
    )
    
    tc6m_valor = st.slider("Caminhada de 6 min (metros):", 0, 800, 350)
    nt_probnp_valor = st.number_input("NT-proBNP (pg/mL):", min_value=0, value=500)
    
    v_perfusao = st.radio("Cintilografia V/Q positiva para TEP?", ["Não", "Sim"])

# --- LÓGICA DE ESTRATIFICAÇÃO ---
score = 0
if classe_sel in ["Classe I", "Classe II"]: score += 1
elif classe_sel == "Classe III": score += 2
else: score += 3

if tc6m_valor > 440: score += 1
elif 165 <= tc6m_valor <= 440: score += 2
else: score += 3

if nt_probnp_valor < 300: score += 1
elif 300 <= nt_probnp_valor <= 1400: score += 2
else: score += 3

media_risco = score / 3

with col_result:
    st.header("2. Resultado e Conduta")
    
    # Definindo Risco e Conduta
    if v_perfusao == "Sim":
        risco_status = "ALERTA: GRUPO 4"
        conduta = "Cintilografia alterada sugere HP Tromboembólica Crônica (HPTEC). Encaminhar para centro especializado para avaliar Tromboendarterectomia ou Angioplastia de Balão."
        st.info(f"🔍 **{conduta}**")
    else:
        if media_risco <= 1.5:
            risco_status = "BAIXO RISCO"
            conduta = "Terapia combinada oral inicial (Inibidor da PDE5 + Antagonista da Endotelina)."
            st.success(f"🟢 **{risco_status}** (Mortalidade em 1 ano < 5%)")
        elif media_risco <= 2.5:
            risco_status = "RISCO INTERMEDIÁRIO"
            conduta = "Avaliar terapia tripla oral. Considerar adição de agonistas do receptor da prostaciclina (Selexipague) ou troca para estimuladores da guanilato ciclase."
            st.warning(f"🟡 **{risco_status}** (Mortalidade em 1 ano 5-20%)")
        else:
            risco_status = "ALTO RISCO"
            conduta = "🚨 EMERGÊNCIA: Iniciar Prostanoides Parenterais (IV/SC) imediatamente. Encaminhar para avaliação de transplante pulmonar."
            st.error(f"🔴 **{risco_status}** (Mortalidade em 1 ano > 20%)")
        
        st.markdown(f"**Conduta Sugerida:**\n{conduta}")

    # --- BOTÃO DE DOWNLOAD PDF ---
    st.divider()
    try:
        pdf_bytes = generate_pdf(classe_sel, tc6m_valor, nt_probnp_valor, risco_status, conduta)
        st.download_button(
            label="📥 Baixar Relatório (PDF)",
            data=pdf_bytes,
            file_name=f"relatorio_HP_{classe_sel.replace(' ', '')}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")

# Rodapé informando critérios hemodinâmicos
with st.expander("Critérios Hemodinâmicos (Cateterismo Direito)"):
    st.write("Valores de referência para diagnóstico (ESC/ERS 2022):")
    st.latex(r"mPAP > 20 \text{ mmHg}")
    st.latex(r"PAWP \leq 15 \text{ mmHg (Pré-capilar)}")
    st.latex(r"PVR \geq 2 \text{ Wood Units}")

st.caption("Uso exclusivo para fins educacionais e suporte médico. Sempre valide com as diretrizes locais.")
