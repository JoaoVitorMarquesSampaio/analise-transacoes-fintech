# Fintech — Pipeline de Dados e Detecção de Anomalias

Aplicação em Python para limpeza, transformação, consolidação, análise estatística e visualização de dados de transações financeiras.

## Requisitos atendidos

- Leitura de `transacoes.csv` com `encoding="latin1"`.
- Imputação de valores ausentes de `valor` pela mediana do respectivo estado.
- Criação da coluna `plataforma` com valor `Mobile`.
- Conversão de `data_transacao` para datetime e aplicação de `America/Sao_Paulo`.
- Criação de `dia_semana` e `mes` com `.dt`.
- Remoção de duplicidades mantendo a primeira ocorrência.
- Filtro vetorizado de setembro + SP/RJ + valor acima de R$ 5.000 usando `&`.
- Associação do nível de risco com `.map()`.
- `pivot_table` por mês e nível de risco com `margins=True`.
- Z-Score vetorizado por estado, sem laço `for`, e identificação de `Z > 2.5`.
- Gráfico com API orientada a objetos (`fig, ax = plt.subplots()`).
- Valor total diário e média móvel de 7 dias com `.rolling(7).mean()`.
- Limite inferior do eixo Y iniciado em zero com `ax.set_ylim(bottom=0)`.
- Visualização em uma aplicação Streamlit.
- Botões para baixar os dados tratados e as anomalias.

## Estrutura

```text
fintech_analise/
├── app.py
├── criar_dados.py
├── requirements.txt
├── README.md
├── transacoes.csv
└── cotacoes.csv
```

## 1. Instalar dependências

```bash
pip install -r requirements.txt
```

## 2. Gerar os dados

```bash
python criar_dados.py
```

O script fornecido pelo professor gera `transacoes.csv` em `latin1` e `cotacoes.csv` em UTF-8.

## 3. Executar a aplicação

```bash
streamlit run app.py
```

Depois, abra o endereço exibido pelo Streamlit no navegador.

## 4. Publicar no GitHub

Crie um repositório no GitHub e, dentro da pasta do projeto:

```bash
git init
git add .
git commit -m "Cria aplicação de análise de transações financeiras"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
git push -u origin main
```

Substitua `SEU-USUARIO/SEU-REPOSITORIO` pelo endereço do seu repositório.

## Observação

O dicionário de risco utilizado no exercício foi definido no código com os cinco clientes presentes no script gerador:

- C100 → Baixo
- C101 → Alto
- C102 → Médio
- C103 → Baixo
- C104 → Alto
