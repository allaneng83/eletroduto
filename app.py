
import streamlit as st
import math
from fpdf import FPDF
import base64

st.set_page_config(page_title="Dimensionamento de Eletrodutos", layout="centered")

st.title("Calculadora de Eletroduto Ideal")

cabos = {
    "PVC 750V": {
        1.5: 3.5, 2.5: 3.7, 4: 4.3, 6: 4.9, 10: 5.9, 16: 6.9, 25: 8.5, 35: 9.6, 50: 11.3,
        70: 12.9, 95: 14.5, 120: 15.9, 150: 18.5, 185: 20.7, 240: 23.4, 300: 26.0, 400: 29.0, 500: 33.3
    },
    "XLPE 1kV": {
        1.5: 5.5, 2.5: 6.0, 4: 6.8, 6: 7.3, 10: 8.0, 16: 9.0, 25: 10.8, 35: 12.0, 50: 13.9,
        70: 15.5, 95: 17.7, 120: 19.2, 150: 21.4, 185: 23.8, 240: 26.7, 300: 29.5, 400: 33.5, 500: 37.3
    }
}

eletrodutos = {
    "Rígido PVC": {
        '1/2"': 84.45, '3/4"': 142.46, '1"': 231.30, '1 1/4"': 409.21, '1 1/2"': 538.18,
        '2"': 875.36, '2 1/2"': 1420.60, '3"': 1931.78, '3 1/2"': 2481.61, '4"': 3395.30,
        '5"': 5064.51, '6"': 7292.89
    },
    "Flexível PVC": {
        "20 mm": 74.47, "25 mm": 113.35, "32 mm": 196.25
    },
    "Ferro Galvanizado": {
        '1/2"': 97.23, '3/4"': 240.76, '1"': 384.64, '1 1/4"': 861.56, '1 1/2"': 1178.49,
        '2"': 1409.51, '2 1/2"': 2332.46, '3"': 3128.53, '3 1/2"': 4105.59, '4"': 5049.03,
        '5"': 7595.21, '6"': 10853.94
    },
    "PEAD Corrugado": {
        "20 mm": 80.4, "25 mm": 125.6, "32 mm": 212.4, "40 mm": 288.4, "50 mm": 520.8,
        "63 mm": 860.0, "90 mm": 1767.2, "100 mm": 2164.8, "110 mm": 2774.4, "125 mm": 3398.0,
        "140 mm": 4524.0, "160 mm": 5727.6, "200 mm": 9140.0, "250 mm": 14516.0
    }
}

st.subheader("Adicione os grupos de cabos:")

grupos = []
with st.form("formulario"):
    for i in range(1, 6):
        st.markdown(f"### Grupo {i}")
        col1, col2, col3 = st.columns(3)
        with col1:
            bitola = st.selectbox(
                f"Bitola (mm²) - Grupo {i}",
                list(cabos["PVC 750V"].keys()),
                key=f"bitola_{i}",
                help="Você pode combinar cabos com diferentes bitolas no mesmo eletroduto, desde que tenham isolação compatível e a ocupação total não exceda 40% da área útil."
            )
        with col2:
            quantidade = st.number_input(
                f"Qtd. de Condutores - Grupo {i}",
                min_value=0, max_value=100, step=1, key=f"qtd_{i}",
                help="Digite a quantidade de condutores com essa bitola que passarão no mesmo eletroduto."
            )
        with col3:
            isolacao = st.selectbox(
                f"Isolação - Grupo {i}",
                list(cabos.keys()),
                key=f"iso_{i}",
                help="Todos os cabos devem ter isolação compatível com a maior tensão do circuito."
            )

        if quantidade > 0:
            diametro = cabos[isolacao][bitola]
            area = math.pi * (diametro / 2) ** 2
            area_total_grupo = area * quantidade
            grupos.append((bitola, quantidade, isolacao, diametro, area_total_grupo, area))

    tipo_eletroduto = st.selectbox(
        "Tipo de Eletroduto",
        list(eletrodutos.keys()),
        help="Escolha o tipo de eletroduto para encontrar o menor diâmetro comercial adequado."
    )
    enviar = st.form_submit_button("Calcular")

if enviar:
    st.info("🔍 A NBR 5410 permite diferentes bitolas no mesmo eletroduto, desde que todos os cabos tenham isolação compatível com a maior tensão e a ocupação total não ultrapasse 40%. Evite passar circuitos independentes no mesmo eletroduto.")

    area_total = sum(g[4] for g in grupos)
    total_condutores = sum(g[1] for g in grupos)
    ocupacao_limite = 0.4 if total_condutores >= 3 else (0.31 if total_condutores == 2 else 0.53)
    area_requerida = area_total / ocupacao_limite

    resultado = None
    for diam, area in eletrodutos[tipo_eletroduto].items():
        if area >= area_requerida:
            resultado = diam
            break

    if resultado:
        st.success(f"Eletroduto mínimo recomendado ({tipo_eletroduto}): **{resultado}**")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Memória de Cálculo - Dimensionamento de Eletroduto", ln=True, align="C")
        pdf.ln(10)

        for idx, g in enumerate(grupos):
            pdf.cell(200, 10, txt=f"Grupo {idx+1}: {g[1]}x {g[0]} mm² ({g[2]})", ln=True)
            pdf.cell(200, 10, txt=f"  - Diâmetro externo estimado: {g[3]:.2f} mm", ln=True)
            pdf.cell(200, 10, txt=f"  - Área individual do condutor: pi x ({g[3]:.2f}/2)² = {g[5]:.2f} mm²", ln=True)
            pdf.cell(200, 10, txt=f"  - Área total ocupada no grupo: {g[5]:.2f} x {g[1]} = {g[4]:.2f} mm²", ln=True)
            pdf.ln(2)

        pdf.ln(5)
        pdf.cell(200, 10, txt=f"Área total ocupada pelos condutores: {area_total:.2f} mm²", ln=True)
        pdf.cell(200, 10, txt=f"Fator de ocupação aplicado: {ocupacao_limite*100:.0f}%", ln=True)
        pdf.cell(200, 10, txt=f"Área mínima requerida: {area_total:.2f} / {ocupacao_limite} = {area_requerida:.2f} mm²", ln=True)
        pdf.cell(200, 10, txt=f"Tipo de eletroduto selecionado: {tipo_eletroduto}", ln=True)
        pdf.cell(200, 10, txt=f"Eletroduto recomendado: {resultado}", ln=True)

        pdf.ln(10)
        pdf.set_font("Arial", style="I", size=10)
        pdf.cell(200, 10, txt="Desenvolvido por Eng° Allan Oliveira", ln=True, align="C")

        pdf.output("memoria_eletroduto.pdf")

        with open("memoria_eletroduto.pdf", "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
        href = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="memoria_eletroduto.pdf">📄 Baixar Memória de Cálculo em PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
        st.error("Nenhum eletroduto disponível atende a essa ocupação. Divida os cabos em mais de um eletroduto.")

st.markdown("<hr><center><sub>Desenvolvido por Eng° Allan Oliveira</sub></center>", unsafe_allow_html=True)
