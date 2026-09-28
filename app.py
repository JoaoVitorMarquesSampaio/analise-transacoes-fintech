import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="Fintech | Análise de Transações", layout="wide")

BASE_DIR = Path(__file__).resolve().parent

RISCO_DICT = {
    "C100": "Baixo",
    "C101": "Alto",
    "C102": "Médio",
    "C103": "Baixo",
    "C104": "Alto",
}

@st.cache_data
def carregar_dados():
    transacoes = pd.read_csv(
        BASE_DIR / "transacoes.csv",
        encoding="latin1"
    )

    cotacoes = pd.read_csv(
        BASE_DIR / "cotacoes.csv",
        encoding="utf-8"
    )

    # Limpeza e imputação por estado
    transacoes["valor"] = transacoes["valor"].fillna(
        transacoes.groupby("estado_cliente")["valor"].transform("median")
    )

    # Rastreabilidade
    transacoes["plataforma"] = "Mobile"

    # Data + fuso horário
    transacoes["data_transacao"] = pd.to_datetime(
        transacoes["data_transacao"]
    ).dt.tz_localize("America/Sao_Paulo")

    # Campos derivados com .dt
    transacoes["dia_semana"] = transacoes["data_transacao"].dt.day_name()
    transacoes["mes"] = transacoes["data_transacao"].dt.month

    # Remove duplicidades, mantendo a primeira ocorrência
    transacoes = transacoes.drop_duplicates(keep="first").copy()

    # Cruzamento por dicionário usando .map()
    transacoes["nivel_risco"] = transacoes["id_cliente"].map(RISCO_DICT)

    # Z-Score vetorizado por estado, sem for
    media_estado = transacoes.groupby("estado_cliente")["valor"].transform("mean")
    desvio_estado = transacoes.groupby("estado_cliente")["valor"].transform("std")

    transacoes["z_score"] = (
        transacoes["valor"] - media_estado
    ) / desvio_estado.replace(0, np.nan)

    anomalias = transacoes.loc[transacoes["z_score"] > 2.5].copy()

    # Filtro obrigatório com operadores bitwise (& e |)
    filtro_setembro = (
        (transacoes["mes"] == 9)
        & (transacoes["estado_cliente"].isin(["SP", "RJ"]))
        & (transacoes["valor"] > 5000)
    )
    setembro_alto_valor = transacoes.loc[filtro_setembro].copy()

    # Pivot table com subtotais
    pivot = pd.pivot_table(
        transacoes,
        index="mes",
        columns="nivel_risco",
        values="valor",
        aggfunc="sum",
        margins=True,
        margins_name="Total",
        fill_value=0,
    )

    # Série diária para o gráfico
    diario = (
        transacoes.set_index("data_transacao")["valor"]
        .resample("D")
        .sum()
        .rename("total_diario")
        .to_frame()
    )
    diario["media_movel_7d"] = diario["total_diario"].rolling(7).mean()

    return (
        transacoes,
        anomalias,
        setembro_alto_valor,
        pivot,
        diario,
        cotacoes,
    )


st.title("📊 Fintech — Análise de Transações")
st.caption("Pipeline de limpeza, transformação, agregação, detecção de anomalias e visualização.")

try:
    (
        df,
        anomalias,
        setembro_alto_valor,
        pivot,
        diario,
        cotacoes,
    ) = carregar_dados()
except FileNotFoundError:
    st.error(
        "Arquivos de dados não encontrados. Execute primeiro "
        "`python criar_dados.py` na pasta do projeto."
    )
    st.stop()

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Transações após limpeza", f"{len(df):,}".replace(",", "."))
col2.metric("Valor total", f"R$ {df['valor'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col3.metric("Anomalias (Z > 2,5)", f"{len(anomalias):,}".replace(",", "."))
col4.metric("SP/RJ > R$ 5.000 em setembro", f"{len(setembro_alto_valor):,}".replace(",", "."))

st.divider()

st.subheader("1. Dados tratados")
st.dataframe(df, use_container_width=True)

st.subheader("2. Filtro vetorizado — setembro, SP/RJ e valor > R$ 5.000")
st.dataframe(setembro_alto_valor, use_container_width=True)

st.subheader("3. Tabela dinâmica por mês e nível de risco")
st.dataframe(pivot.style.format("R$ {:,.2f}"), use_container_width=True)

st.subheader("4. Detecção de potenciais anomalias")
st.write("Critério: Z-Score por estado maior que 2,5.")
st.dataframe(
    anomalias.sort_values("z_score", ascending=False),
    use_container_width=True,
)

st.subheader("5. Evolução diária das transações")
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(diario.index, diario["total_diario"], label="Valor total diário")
ax.plot(diario.index, diario["media_movel_7d"], label="Média móvel de 7 dias")
ax.set_ylim(bottom=0)
ax.set_title("Valor total de transações e média móvel de 7 dias")
ax.set_xlabel("Data")
ax.set_ylabel("Valor (R$)")
ax.legend()
fig.autofmt_xdate()
st.pyplot(fig)
plt.close(fig)

st.subheader("6. Cotações da empresa")
st.dataframe(cotacoes, use_container_width=True)

st.download_button(
    "⬇️ Baixar transações tratadas",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="transacoes_tratadas.csv",
    mime="text/csv",
)

st.download_button(
    "⬇️ Baixar anomalias",
    data=anomalias.to_csv(index=False).encode("utf-8"),
    file_name="anomalias.csv",
    mime="text/csv",
)
