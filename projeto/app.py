import streamlit as st
import pandas as pd
import plotly.express as px
import kagglehub


# Carregando dados
path = kagglehub.dataset_download("adharshinikumar/2025-hearing-wellness-survey")
try:
    df = pd.read_csv(path + "/Hearing well-being Survey Report.csv")
except FileNotFoundError:
    st.error("Arquivo 'Hearing well-being Survey Report.csv' não encontrado!")
    st.stop()

st.set_page_config(
    page_title="Pesquisa sobre Bem-Estar Auditivo",
    page_icon="🎧",
    layout="wide",
)

# Barra lateral (Filtros)
st.sidebar.header("Filtros")

# Filtro de Idades
ages_available = sorted(df['Age_group'].unique())
ages_selected = st.sidebar.multiselect(
    "Selecione a(s) Faixa(s) Etária(s):",
    ages_available,
    default=ages_available
)

# Filtro de Uso dos Fones
daily_headphone_use_available = sorted(df['Daily_Headphone_Use'].unique())
daily_headphone_use_selected = st.sidebar.multiselect(
    "Selecione o Tempo de Uso de Fones:",
    daily_headphone_use_available,
    default=daily_headphone_use_available
)

# Filtro de Desconforto no Ouvido
ear_discomfort_options = ['Todos'] + sorted(df['Ear_Discomfort_After_Use'].unique())
ear_discomfort_selected = st.sidebar.radio(
    "Sente Desconforto no Ouvido?", # Rótulo corrigido
    ear_discomfort_options,
    index=0  # 'index=0' define "Todos" como o padrão
)

# Filtro de Interesse no App
interest_app_options = ['Todos'] + sorted(df['Interest_in_Hearing_App'].unique())
interest_app_selected = st.sidebar.selectbox(
    "Interesse no Aplicativo de Audição:", # Rótulo corrigido
    interest_app_options,
    index=0 # 'index=0' define "Todos" como o padrão
)

# Filtragem do DataFrame
df_filtrado = df[
    (df['Age_group'].isin(ages_selected)) &
    (df['Daily_Headphone_Use'].isin(daily_headphone_use_selected))
]
# Lógica para "Todos"
if ear_discomfort_selected != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Ear_Discomfort_After_Use'] == ear_discomfort_selected]

if interest_app_selected != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Interest_in_Hearing_App'] == interest_app_selected]


# --- Título Principal ---
st.title("🎧 Dashboard de Análise sobre Bem-Estar Auditivo")
st.markdown("Use os filtros na barra lateral para explorar os dados da pesquisa.")
st.subheader("Resumo Geral dos Participantes")

# Verificamos se o dataframe filtrado não está vazio para evitar erros
if not df_filtrado.empty:
    total_participantes = df_filtrado.shape[0]
    faixa_etaria_predominante = df_filtrado['Age_group'].mode()[0]
    principal_barreira = df_filtrado['Hearing_Test_Barrier'].mode()[0]

    # Cálculo da porcentagem de interessados no App
    total_interessados = (df_filtrado['Interest_in_Hearing_App'] == 'Yes, that would be helpful').sum()
    percentual_interesse = (total_interessados / total_participantes) * 100 if total_participantes > 0 else 0

else:
    total_participantes = 0
    faixa_etaria_predominante = "N/A"
    principal_barreira = "N/A"
    percentual_interesse = 0

# Criando as 4 colunas para as métricas
col1, col2, col3, col4 = st.columns(4)

# Exibindo cada métrica em sua respectiva coluna
col1.metric("Total de Participantes", f"{total_participantes}")
col2.metric("Faixa Etária Predominante", faixa_etaria_predominante)
col3.metric("Principal Barreira p/ Teste", principal_barreira)
col4.metric("Interesse em App", f"{percentual_interesse:.1f}%")

# Adicionando uma linha divisória
st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos Interativos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown("##### Distribuição por Faixa Etária")
    if not df_filtrado.empty:
        # Pegou 10 com maiores salários
        age_counts = df_filtrado['Age_group'].value_counts().reset_index()
        age_counts.columns = ['Faixa Etária', 'Número de Participantes']
        age_counts = age_counts.sort_values('Faixa Etária')
        fig_age = px.bar(
            age_counts,
            x='Faixa Etária',
            y='Número de Participantes',
            text_auto=True,  # Adiciona os valores diretamente nas barras
            color='Faixa Etária',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        # Mover o titulo um pouco para a direita
        fig_age.update_layout(title="", showlegend=False)
        st.plotly_chart(fig_age, use_container_width=True)   # Exibir gráfico no st
    else:
        st.warning("Nenhum dado para exibir.")

with col_graf2:
    st.markdown("##### Uso Diário de Fones de Ouvido")
    if not df_filtrado.empty:
        headphone_counts = df_filtrado['Daily_Headphone_Use'].value_counts().reset_index()
        headphone_counts.columns = ['Tempo de Uso', 'Número de Participantes']
        fig_headphone_counts = px.bar(
            headphone_counts,
            x='Número de Participantes',
            y='Tempo de Uso',
            orientation='h',
            text_auto=True,
            color='Tempo de Uso', # Colore cada barra com uma cor diferente
        )
        fig_headphone_counts.update_layout(title="", showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_headphone_counts, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir.")

st.markdown("---")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    st.markdown("##### Frequência de 'FOMO Auditivo'")
    if not df_filtrado.empty:
        # Contar os valores da coluna 'Hearing_FOMO'
        fomo_counts = df_filtrado['Hearing_FOMO'].value_counts().reset_index()
        fomo_counts.columns = ['Frequência', 'Número de Participantes']

        # Definir a ordem correta das categorias
        fomo_order = ['Never', 'Rarely', 'Sometimes', 'Yes often']
        fig_fomo_order = px.bar(
            fomo_counts,
            x='Frequência',
            y='Número de Participantes',
            text_auto=True,
            category_orders={'Frequência': fomo_order},
            color='Frequência',
            color_discrete_sequence=px.colors.sequential.Magma_r
        )
        fig_fomo_order.update_layout(title="", showlegend=False)
        st.plotly_chart(fig_fomo_order, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir.")

with col_graf4:
    st.markdown("##### Interesse em App por Faixa Etária")
    if not df_filtrado.empty:
        age_order = sorted(df_filtrado['Age_group'].unique())
        fig_age_interest = px.bar(
            df_filtrado,
            x='Age_group',
            color='Interest_in_Hearing_App',
            barmode='group',
            text_auto=True,
            labels={
                'Age_group': 'Faixa Etária',
                'count': 'Participantes',
                'Interest_in_Hearing_App': 'Interesse no App'
            },
            category_orders={'Age_group': age_order}
        )
        fig_age_interest.update_layout(title="")
        st.plotly_chart(fig_age_interest, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir.")

st.markdown("---")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados Filtrados")
st.dataframe(df_filtrado)