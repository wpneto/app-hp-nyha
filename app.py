import streamlit as st
import pandas as pd

# Configuração da página para Mobile e Desktop
st.set_page_config(page_title="HP ClinApp", layout="wide", initial_sidebar_state="collapsed")

# Cabeçalho
st.title("🩺 HP ClinApp")
st.subheader("Suporte à Decisão: Diagnóstico e Risco na HP")

# --- BARRA LATERAL / ENTRADA DE DADOS ---
with st.expander("📝 Dados do Paciente", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        classe_oms = st.selectbox(
            "Classe Funcional (OMS/NYHA):",
            ["Classe I", "Classe II", "Classe III", "Classe IV"],
            help="I: Sem sintomas | IV: Sintomas em repouso"
        )
        tc6m = st.slider("Teste de Caminhada 6 min (metros):", 0, 800, 350)
    
    with col2:
        nt_probnp = st.number_input("NT-proBNP (pg/mL):", value=500)
        v_perfusao = st.radio("Cintilografia V/Q alterada?", ["Não", "Sim"])

# --- LÓGICA DE ESTRATIFICAÇÃO ---
st.divider()
st.header("📊 Avaliação de Risco e Conduta")

# Cálculo de pontuação simplificado
score = 0
if classe_oms in ["Classe I", "Classe II"]: score += 1
elif classe_oms == "Classe III": score += 2
else: score += 3

if tc6m > 440: score += 1
elif 165 <= tc6m <= 440: score += 2
else: score += 3

if nt_probnp < 300: score += 1
elif 300 <= nt_probnp <= 1400: score += 2
else: score += 3

media = score / 3

# Exibição de Resultados
res_col1, res_col2 = st.columns([1, 2])

with res_col1:
    if media <= 1.5:
        st.success("🟢 BAIXO RISCO\n(Mortalidade < 5%)")
    elif media <= 2.5:
        st.warning("🟡 RISCO INTERMEDIÁRIO\n(Mortalidade 5-20%)")
    else:
        st.error("🔴 ALTO RISCO\n(Mortalidade > 20%)")

with res_col2:
    if v_perfusao == "Sim":
        st.info("🔍 **Alerta de Grupo 4:** Cintilografia alterada sugere HP Tromboembólica Crônica. Avaliar indicação de Tromboendarterectomia.")
    else:
        st.markdown("**Conduta Recomendada (Grupo 1):**")
        if media <= 1.5:
            st.write("- Iniciar terapia combinada oral (Inibidor PDE5 + ARE).")
        elif media <= 2.5:
            st.write("- Terapia tripla oral ou considerar análogos da prostaciclina.")
        else:
            st.write("- **Emergência:** Prostanoides IV/SC e avaliação para transplante.")

st.caption("⚠️ Uso exclusivo para profissionais de saúde. Baseado nas diretrizes ESC/ERS 2022.")
