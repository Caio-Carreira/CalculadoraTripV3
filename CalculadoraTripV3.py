import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import locale

# Configurações iniciais
st.set_page_config(
    page_title=" 🖩 Calculadora Trip Premium", 
    layout="wide",
    page_icon="✈️"
)

# Configurar locale para português
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

# Estilo premium
st.markdown("""
    <style>
        :root {
            --primary: #0d3b66;
            --secondary: #f8f9fa;
            --accent: #198754;
        }
        .main {
            background-color: #ffffff;
            color: #333;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 16px;
            padding: 12px 20px;
            font-weight: 600;
            border-radius: 8px 8px 0 0;
            margin: 0 5px;
            transition: all 0.3s;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e9ecef;
        }
        .stTabs [aria-selected="true"] {
            background-color: var(--primary);
            color: white !important;
        }
        h1, h2, h3, h4 {
            color: var(--primary);
            font-weight: 700;
        }
        .dataframe th {
            background-color: var(--primary) !important;
            color: white !important;
        }
        .dataframe td {
            background-color: #f8f9fa;
        }
        .stButton>button {
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 0.7em 1.5em;
            border-radius: 8px;
            font-weight: 600;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #145d8f;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .stDownloadButton>button {
            background-color: var(--accent);
            color: white;
            padding: 0.7em 1.5em;
            border-radius: 8px;
            font-weight: 600;
            transition: 0.3s;
        }
        .stDownloadButton>button:hover {
            background-color: #146c43;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .relatorio-container {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .relatorio-dia {
            font-family: 'Consolas', monospace;
            font-size: 15px;
            margin-bottom: 10px;
            padding: 8px;
            background-color: white;
            border-radius: 6px;
            border-left: 4px solid var(--primary);
        }
        .relatorio-total {
            font-family: 'Segoe UI', sans-serif;
            font-size: 18px;
            font-weight: 700;
            margin-top: 20px;
            padding: 12px;
            background-color: var(--primary);
            color: white;
            border-radius: 6px;
            text-align: center;
        }
        .total-box {
            background-color: var(--primary);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .day-card {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 4px solid var(--primary);
        }
    </style>
""", unsafe_allow_html=True)

# Funções auxiliares
def formatar_moeda(valor):
    return locale.currency(valor, grouping=True, symbol=True)

def calcular_gasto_linha(dado, valores, deslocamento_valor, datas_deslocamento):
    deslocamento = deslocamento_valor if (dado["dia"] in datas_deslocamento) else 0
    
    # Calcula almoço
    almoco = 0
    if dado["almoco"]:
        almoco = valores["almoco_normal"]
    elif dado["almoco_feriado"]:
        if dado["tipo"] == "Feriado final de semana":
            almoco = valores["almoco_feriado_fds"]
        else:
            almoco = valores["almoco_feriado_extra"]
    
    # Calcula jantar
    jantar = 0
    if dado["jantar"]:
        jantar = valores["jantar_feriado"] if "Feriado" in dado["tipo"] else valores["jantar_normal"]
    
    row = {
        "Dia": dado["dia"],
        "Tipo": dado["tipo"],
        "Café": valores["cafe"] if dado["cafe"] else 0,
        "Almoço": almoco,
        "Jantar": jantar,
        "Frigobar": valores["frigobar"] if dado["frigobar"] else 0,
        "Lavanderia": valores["lavanderia"] if dado["lavanderia"] else 0,
        "Deslocamento": deslocamento,
        "Total": 0
    }
    
    row["Total"] = sum([row[c] for c in ["Café", "Almoço", "Jantar", "Frigobar", "Lavanderia", "Deslocamento"]])
    return row

# Título principal
st.title("✈️ Calculadora Premium de Despesas de Viagem")

# Abas principais
tabs = st.tabs(["📋 Preenchimento de Dias", "📊 Relatório Completo"])

# Sidebar premium
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; margin-bottom:30px;">
        <h2 style="color:#0d3b66;">⚙️ Configurações</h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("💰 Valores Base", expanded=True):
        valores = {
            "cafe": st.number_input("☕ Café da manhã", value=20.0, min_value=0.0),
            "almoco_normal": st.number_input("🍽️ Almoço (dia útil)", value=33.0, min_value=0.0),
            "almoco_feriado_extra": st.number_input("🍽️ Almoço (feriado dia útil)", value=25.0, min_value=0.0),
            "almoco_feriado_fds": st.number_input("🍽️ Almoço (feriado fim de semana)", value=58.0, min_value=0.0),
            "jantar_normal": st.number_input("🌙 Jantar (normal)", value=40.0, min_value=0.0),
            "jantar_feriado": st.number_input("🌙 Jantar (feriado)", value=58.0, min_value=0.0),
            "frigobar": st.number_input("🧊 Frigobar", value=15.0, min_value=0.0),
            "lavanderia": st.number_input("👕 Lavanderia", value=200.0, min_value=0.0)
        }

    st.markdown("---")
    
    with st.expander("🚗 Deslocamento", expanded=True):
        usa_calculadora = st.checkbox("Usar cálculadora de deslocamento", value=True)
        if usa_calculadora:
            deslocamento_params = {
                "distancia_viagem": st.number_input("📍 Distância (km)", value=650, min_value=1),
                "consumo_carro": st.number_input("⛽ Consumo (km/l)", value=14.0, min_value=1.0),
                "preco_combustivel": st.number_input("💵 Preço combustível", value=6.30, min_value=0.1)
            }
            valor_deslocamento = (deslocamento_params["distancia_viagem"] / deslocamento_params["consumo_carro"]) * deslocamento_params["preco_combustivel"]
        else:
            valor_deslocamento = st.number_input("💰 Valor fixo", value=350.0, min_value=0.0)
        
        st.success(f"**Valor estimado:** {formatar_moeda(valor_deslocamento)}")

# Variáveis para armazenamento de dados
datas_deslocamento = []
dias = []

# ------------------- ABA PRINCIPAL -------------------
with tabs[0]:
    col_center = st.columns([1, 3, 1])[1]
    with col_center:
        st.markdown("""
        <div style="text-align:center; margin-bottom:30px;">
            <h3>📅 Datas da Viagem</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data de Início", key="data_inicio")
        with col2:
            data_fim = st.date_input("Data de Término", key="data_fim")

    if data_fim < data_inicio:
        st.error("⚠️ A data de término deve ser posterior à data de início.")
    else:
        periodo_viagem = pd.date_range(start=data_inicio, end=data_fim)

        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; margin-bottom:20px;">
            <h3>🧾 Preencha os dados para cada dia</h3>
        </div>
        """, unsafe_allow_html=True)

        for data in periodo_viagem:
            dia_formatado = data.strftime("%d/%m/%Y")
            nome_dia_pt = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"][data.weekday()]
            fim_de_semana = nome_dia_pt in ["Sábado", "Domingo"]

            with st.expander(f"{dia_formatado} ({nome_dia_pt})", expanded=False):
                with st.container():
                    st.markdown(f'<div class="day-card">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        cafe = st.checkbox("☕ Café da manhã", key=f"cafe_{dia_formatado}")
                        jantar = st.checkbox("🌙 Jantar", key=f"jantar_{dia_formatado}")
                        frigobar = st.checkbox("🧊 Frigobar", key=f"frigobar_{dia_formatado}")
                        lavanderia = st.checkbox("👕 Lavanderia", key=f"lavanderia_{dia_formatado}")
                        
                        # Checkbox de feriado como última opção
                        feriado = st.checkbox("🎉 Feriado", key=f"feriado_{dia_formatado}")
                        
                        # Lógica para checkboxes de almoço
                        almoco = False
                        almoco_feriado = False
                        
                        if fim_de_semana:
                            if feriado:
                                almoco_feriado = st.checkbox("🍽️ Almoço Feriado FDS", key=f"almoco_feriado_fds_{dia_formatado}")
                            else:
                                almoco = st.checkbox("🍽️ Almoço (FDS)", key=f"almoco_{dia_formatado}")
                        elif feriado:
                            almoco_feriado = st.checkbox("🍽️ Almoço Feriado Dia Útil", key=f"almoco_feriado_{dia_formatado}")

                    # Define o tipo do dia
                    if feriado and fim_de_semana:
                        tipo_dia = "Feriado final de semana"
                    elif feriado:
                        tipo_dia = "Feriado dia útil"
                    else:
                        tipo_dia = nome_dia_pt if fim_de_semana else "Dia útil"

                    dias.append({
                        "dia": dia_formatado,
                        "tipo": tipo_dia,
                        "cafe": cafe,
                        "almoco": almoco,
                        "almoco_feriado": almoco_feriado,
                        "jantar": jantar,
                        "frigobar": frigobar,
                        "deslocamento": False,
                        "lavanderia": lavanderia
                    })
                    
                    st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        
        # Seção de deslocamentos
        st.markdown("""
        <div style="text-align:center; margin-bottom:20px;">
            <h3>🚗 Cadastrar Deslocamentos</h3>
        </div>
        """, unsafe_allow_html=True)
        
        datas_deslocamento.clear()
        qtd_deslocamentos = st.number_input("Quantos deslocamentos deseja cadastrar?", min_value=0, max_value=30, value=0)
        
        for i in range(qtd_deslocamentos):
            data_deslocamento = st.date_input(f"Data do deslocamento #{i + 1}", key=f"data_deslocamento_{i}")
            datas_deslocamento.append(data_deslocamento.strftime("%d/%m/%Y"))
        
        # Exibir total na primeira aba
        if dias:
            linhas = [calcular_gasto_linha(dia, valores, valor_deslocamento, datas_deslocamento) for dia in dias]
            df = pd.DataFrame(linhas)
            total_geral = df["Total"].sum()
            
            st.markdown("---")
            st.markdown(f"""
            <div class="total-box">
                <h3>💰 Total Estimado</h3>
                <h2>{formatar_moeda(total_geral)}</h2>
                <p style="font-size:14px; margin-bottom:0;">Consulte a aba de Relatório para detalhes</p>
            </div>
            """, unsafe_allow_html=True)

# ------------------- RELATÓRIO COMPLETO -------------------
with tabs[1]:
    st.markdown("""
    <div style="text-align:center; margin-bottom:30px;">
        <h2>📊 Relatório Completo de Gastos</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if not dias:
        st.info("ℹ️ Nenhum dado preenchido ainda. Preencha os dados na aba 'Preenchimento de Dias'.")
    else:
        linhas = [calcular_gasto_linha(dia, valores, valor_deslocamento, datas_deslocamento) for dia in dias]
        df = pd.DataFrame(linhas)
        
        # Dados consolidados
        st.markdown("### 📋 Dados Consolidados")
        df_display = df.copy()
        for col in df_display.columns[2:]:
            df_display[col] = df_display[col].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        st.dataframe(df_display, use_container_width=True)
        
        # Gráfico de resumo
        st.markdown("---")
        st.markdown("### 📈 Resumo por Categoria")
        resumo = df[['Café', 'Almoço', 'Jantar', 'Frigobar', 'Lavanderia', 'Deslocamento']].sum().reset_index()
        resumo.columns = ['Categoria', 'Total']
        st.bar_chart(resumo.set_index('Categoria'))
        
        # Relatório descritivo
        st.markdown("---")
        st.markdown("### 📝 Relatório Descritivo")
        
        with st.container():
            st.markdown('<div class="relatorio-container">', unsafe_allow_html=True)
            
            texto_relatorio = []
            for linha in df.itertuples():
                partes = [f"<div class='relatorio-dia'>{linha.Dia} –"]
                if linha.Café > 0:
                    partes.append(f"+ ☕ Café da manhã {formatar_moeda(linha.Café)}")
                if linha.Almoço > 0:
                    partes.append(f"+ 🍽️ Almoço {formatar_moeda(linha.Almoço)}")
                if linha.Jantar > 0:
                    partes.append(f"+ 🌙 Jantar {formatar_moeda(linha.Jantar)}")
                if linha.Frigobar > 0:
                    partes.append(f"+ 🧊 Frigobar {formatar_moeda(linha.Frigobar)}")
                if linha.Lavanderia > 0:
                    partes.append(f"+ 👕 Lavanderia {formatar_moeda(linha.Lavanderia)}")
                if linha.Deslocamento > 0:
                    partes.append(f"+ 🚗 Deslocamento {formatar_moeda(linha.Deslocamento)}")
                
                partes.append(f"= {formatar_moeda(linha.Total)}")
                partes.append("</div>")
                texto_relatorio.append(" ".join(partes))
            
            st.markdown("\n".join(texto_relatorio), unsafe_allow_html=True)
            
            # Total do período
            total_geral = df["Total"].sum()
            st.markdown(
                f"<div class='relatorio-total'>Total do Período: {formatar_moeda(total_geral)}</div>",
                unsafe_allow_html=True
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Exportação de dados
        st.markdown("---")
        st.markdown("### 💾 Exportar Dados")
        
        col1, col2 = st.columns(2)
        with col1:
            # Preparar texto para exportação
            texto_exportacao = []
            for linha in df.itertuples():
                partes = [f"{linha.Dia} –"]
                if linha.Café > 0:
                    partes.append(f"+ ☕ Café da manhã {formatar_moeda(linha.Café)}")
                if linha.Almoço > 0:
                    partes.append(f"+ 🍽️ Almoço {formatar_moeda(linha.Almoço)}")
                if linha.Jantar > 0:
                    partes.append(f"+ 🌙 Jantar {formatar_moeda(linha.Jantar)}")
                if linha.Frigobar > 0:
                    partes.append(f"+ 🧊 Frigobar {formatar_moeda(linha.Frigobar)}")
                if linha.Lavanderia > 0:
                    partes.append(f"+ 👕 Lavanderia {formatar_moeda(linha.Lavanderia)}")
                if linha.Deslocamento > 0:
                    partes.append(f"+ 🚗 Deslocamento {formatar_moeda(linha.Deslocamento)}")
                
                partes.append(f"= {formatar_moeda(linha.Total)}")
                texto_exportacao.append(" ".join(partes))
            
            texto_exportacao.append(f"\nTotal do Período: {formatar_moeda(total_geral)}")
            
            st.download_button(
                label="⬇️ Baixar Relatório (TXT)",
                data="\n".join(texto_exportacao),
                file_name="relatorio_viagem.txt",
                mime="text/plain",
                help="Baixe o relatório completo em formato de texto"
            )
        
        with col2:
            st.download_button(
                label="⬇️ Baixar Dados (CSV)",
                data=df.to_csv(index=False),
                file_name="dados_viagem.csv",
                mime="text/csv",
                help="Baixe os dados completos em formato CSV para Excel"
            )