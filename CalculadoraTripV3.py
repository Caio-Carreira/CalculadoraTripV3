import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import locale

# Configurações iniciais
st.set_page_config(page_title=" 🖩 Cálculadora Trip", layout="wide")

# Configurar locale para português (formatação de números)
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

# Estilo personalizado aprimorado
st.markdown("""
    <style>
        .main {background-color: #f1f3f6; color: #333;}
        .stTabs [data-baseweb="tab"] {
            font-size: 16px;
            padding: 10px;
        }
        h1, h2, h3, h4 {
            color: #0d3b66;
            font-weight: 600;
        }
        .dataframe th, .dataframe td {
            padding: 8px;
            text-align: left;
            font-size: 15px;
        }
        .stButton>button {
            background-color: #0d3b66;
            color: white;
            border: none;
            padding: 0.5em 1em;
            border-radius: 8px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #145d8f;
            color: #fff;
        }
        .stDownloadButton>button {
            background-color: #198754;
            color: white;
            padding: 0.5em 1em;
            border-radius: 8px;
        }
        .stDownloadButton>button:hover {
            background-color: #146c43;
        }
        .css-1aumxhk {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# Lista de feriados (pode ser expandida)
feriados_brasil = [
    "01/01", # Ano Novo
    "21/04", # Tiradentes
    "01/05", # Dia do Trabalho
    "07/09", # Independência
    "12/10", # Nossa Senhora Aparecida
    "02/11", # Finados
    "15/11", # Proclamação da República
    "25/12"  # Natal
]

# Função para verificar feriados
def verificar_feriado(data):
    data_str = data.strftime("%d/%m")
    return data_str in feriados_brasil

# Função para formatar moeda
def formatar_moeda(valor):
    return locale.currency(valor, grouping=True, symbol=False)

# Função de cálculo
def calcular_gasto_linha(dado, valores, deslocamento_valor, datas_deslocamento):
    # Verifica se é dia de deslocamento
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
        "Total": 0  # Será calculado abaixo
    }
    
    # Calcula total
    row["Total"] = sum([row[c] for c in ["Café", "Almoço", "Jantar", "Frigobar", "Lavanderia", "Deslocamento"]])
    
    return row

# Título principal
st.title("🧮 Calculadora de Despesas de Viagem")

# Abas principais
tabs = st.tabs(["📋 Preenchimento de Dias", "📊 Relatório"])

# Sidebar
st.sidebar.header("⚙️ Valores Base")
with st.sidebar.expander("🔧 Configurar Valores", expanded=True):
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

st.sidebar.markdown("---")
st.sidebar.header("🚗 Parâmetros de Deslocamento")
usa_calculadora = st.sidebar.checkbox("Usar cálculadora de deslocamento", value=True)
if usa_calculadora:
    with st.sidebar.expander("🔧 Configurar Deslocamento", expanded=True):
        deslocamento_params = {
            "distancia_viagem": st.number_input("📍 Distância da viagem (km)", value=650, min_value=1),
            "consumo_carro": st.number_input("⛽ Consumo do carro (km/l)", value=14.0, min_value=1.0),
            "preco_combustivel": st.number_input("💵 Preço do combustível (R$/litro)", value=6.30, min_value=0.1)
        }
    valor_deslocamento = (deslocamento_params["distancia_viagem"] / deslocamento_params["consumo_carro"]) * deslocamento_params["preco_combustivel"]
else:
    valor_deslocamento = st.sidebar.number_input("💰 Valor fixo de deslocamento", value=350.0, min_value=0.0)

st.sidebar.success(f"💰 Deslocamento: R$ {formatar_moeda(valor_deslocamento)}")

# Variáveis para armazenamento de dados
datas_deslocamento = []
dias = []

# ------------------- ABA PRINCIPAL -------------------
with tabs[0]:
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        st.markdown("<h3 style='text-align: center;'>📅 Informe a Data de Início da Viagem</h3>", unsafe_allow_html=True)
        data_inicio = st.date_input("", key="data_inicio")

        st.markdown("<h3 style='text-align: center;'>📅 Informe a Data de Término da Viagem</h3>", unsafe_allow_html=True)
        data_fim = st.date_input("", key="data_fim")

    if data_fim < data_inicio:
        st.error("⚠️ A data de término deve ser posterior à data de início.")
    else:
        periodo_viagem = pd.date_range(start=data_inicio, end=data_fim)

        st.markdown("---")
        st.markdown("### 🧾 Preencha os dados abaixo para cada dia:")

        for data in periodo_viagem:
            dia_formatado = data.strftime("%d/%m/%Y")
            nome_dia_pt = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"][data.weekday()]
            fim_de_semana = nome_dia_pt in ["Sábado", "Domingo"]
            feriado = verificar_feriado(data)

            st.markdown(f"### {dia_formatado} ({nome_dia_pt})")
            if feriado:
                st.markdown("🎉 **Feriado Nacional**")
            
            col1, col2 = st.columns(2)
            with col1:
                cafe = st.checkbox("☕ Café da manhã", key=f"cafe_{dia_formatado}")

                almoco = False
                almoco_feriado = False

                if fim_de_semana:
                    almoco = st.checkbox("🍽️ Almoço (FDS)", key=f"almoco_{dia_formatado}")
                elif feriado:
                    almoco_feriado = st.checkbox("🍽️ Almoço Feriado", key=f"almoco_feriado_{dia_formatado}")
                else:
                    almoco = st.checkbox("🍽️ Almoço (dia útil)", key=f"almoco_{dia_formatado}")

                jantar = st.checkbox("🌙 Jantar", key=f"jantar_{dia_formatado}")
                frigobar = st.checkbox("🧊 Frigobar", key=f"frigobar_{dia_formatado}")
                lavanderia = st.checkbox("👕 Lavanderia", key=f"lavanderia_{dia_formatado}")

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

        st.markdown("---")
        st.subheader("🚗 Cadastrar Deslocamentos")
        datas_deslocamento.clear()
        qtd_deslocamentos = st.number_input("Quantos deslocamentos deseja cadastrar?", min_value=0, max_value=30, value=0)
        for i in range(qtd_deslocamentos):
            data_deslocamento = st.date_input(f"🗕️ Data do deslocamento #{i + 1}", key=f"data_deslocamento_{i}")
            datas_deslocamento.append(data_deslocamento.strftime("%d/%m/%Y"))

# ------------------- RELATÓRIO -------------------
with tabs[1]:
    st.subheader("📊 Relatório de Gastos")
    if not dias:
        st.info("ℹ️ Nenhum dado preenchido ainda. Preencha os dados na aba 'Preenchimento de Dias'.")
    else:
        linhas = [calcular_gasto_linha(dia, valores, valor_deslocamento, datas_deslocamento) for dia in dias]
        df = pd.DataFrame(linhas)
        
        # Formatação do DataFrame para exibição
        df_display = df.copy()
        for col in df_display.columns[2:]:
            df_display[col] = df_display[col].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        st.dataframe(df_display, use_container_width=True)
        
        total_geral = df["Total"].sum()
        st.markdown(f"## 💰 Total de Despesas: R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        # Gráfico de resumo
        st.markdown("---")
        st.subheader("📈 Resumo por Categoria")
        resumo = df[['Café', 'Almoço', 'Jantar', 'Frigobar', 'Lavanderia', 'Deslocamento']].sum().reset_index()
        resumo.columns = ['Categoria', 'Total']
        st.bar_chart(resumo.set_index('Categoria'))
        
        # Relatório descritivo melhorado
        st.markdown("---")
        st.subheader("📝 Relatório Descritivo")
        texto_relatorio = ["### Detalhamento por Dia\n"]
        
        for linha in df.itertuples():
            partes = [f"**{linha.Dia}** ({linha.Tipo}):"]
            itens = []
            if linha.Deslocamento > 0:
                itens.append(f"🚗 Deslocamento (R$ {linha.Deslocamento:,.2f})".replace(",", "X").replace(".", ",").replace("X", "."))
            if linha.Café > 0:
                itens.append(f"☕ Café (R$ {linha.Café:,.2f})".replace(",", "X").replace(".", ",").replace("X", "."))
            if linha.Almoço > 0:
                itens.append(f"🍽️ Almoço (R$ {linha.Almoço:,.2f})".replace(",", "X").replace(".", ",").replace("X", "."))
            if linha.Jantar > 0:
                itens.append(f"🌙 Jantar (R$ {linha.Jantar:,.2f})".replace(",", "X").replace(".", ",").replace("X", "."))
            if linha.Frigobar > 0:
                itens.append(f"🧊 Frigobar (R$ {linha.Frigobar:,.2f})".replace(",", "X").replace(".", ",").replace("X", "."))
            if linha.Lavanderia > 0:
                itens.append(f"👕 Lavanderia (R$ {linha.Lavanderia:,.2f})".replace(",", "X").replace(".", ",").replace("X", "."))
            
            partes.append(" + ".join(itens))
            partes.append(f"→ **Total: R$ {linha.Total:,.2f}**".replace(",", "X").replace(".", ",").replace("X", "."))
            texto_relatorio.append(" ".join(partes))
        
        texto_relatorio.append(f"\n### Total do Período: R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.markdown("\n\n".join(texto_relatorio))
        
        # Opções de exportação
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="⬇️ Baixar Relatório (TXT)",
                data="\n".join(texto_relatorio),
                file_name="relatorio_viagem.txt",
                mime="text/plain"
            )
        with col2:
            st.download_button(
                label="⬇️ Baixar Dados (CSV)",
                data=df.to_csv(index=False),
                file_name="dados_viagem.csv",
                mime="text/csv"
            )