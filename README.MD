# 📊 Dashboard de Desempenho de Times — Brasileirão

Este projeto é um **dashboard interativo em Python** que permite visualizar o desempenho de um time ao longo dos anos no Campeonato Brasileiro.

A aplicação utiliza interface gráfica com Tkinter e gráficos com Matplotlib para apresentar estatísticas como vitórias, empates, derrotas e pontuação.

---

## 🚀 Funcionalidades

- 🔍 Seleção dinâmica de times via dropdown (combobox)
- 📅 Análise por ano
- 📊 Gráfico de:
  - Vitórias
  - Empates
  - Derrotas
- 🧮 Cálculo de:
  - Pontuação total
  - Total de vitórias
  - Melhor ano do time
- 🔄 Atualização dinâmica do dashboard ao trocar o time

---

## 🧱 Estrutura do Projeto

O projeto é dividido em algumas partes principais:

### 1. 📥 Carregamento de Dados
Os dados são carregados a partir de um arquivo JSON/CSV contendo os jogos.

---

### 2. 🔎 Filtros e Processamento

Funções responsáveis por:

- Buscar jogos por nome do time
- Calcular estatísticas:
  - vitórias
  - empates
  - derrotas
  - pontuação por ano

---

### 3. 📊 Geração de Gráficos

Utiliza **Matplotlib** para criar gráficos de barras:

- Gráfico agrupado por ano
- Exibição de valores acima das barras
- Legenda automática
- Ajuste de layout para melhor visualização

---

### 4. 🖥️ Interface Gráfica

Construída com **Tkinter**, contendo:

- Cards informativos
- Gráficos incorporados (via `FigureCanvasTkAgg`)
- Combobox para seleção de time

---

## ▶️ Como Executar

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd <nome-do-projeto>
````

---

### 2. Crie um ambiente virtual (opcional)

```bash
python -m venv venv
source venv/bin/activate  # Linux
venv\Scripts\activate     # Windows
```

---

### 3. Instale as dependências

```bash
pip install matplotlib numpy pandas
```

> ⚠️ Tkinter geralmente já vem com o Python.
> No Linux, pode ser necessário instalar:

```bash
sudo apt install python3-tk
```

---

### 4. Execute o projeto

```bash
python main.py
```

---

## 🎮 Como Usar

1. Abra a aplicação
2. Selecione um time no dropdown
3. O dashboard será atualizado automaticamente com:

   * Estatísticas do time
   * Gráficos por ano

---

## 📊 Exemplo de Visualização

* Gráfico de barras agrupadas por ano
* Valores exibidos acima de cada barra
* Legenda indicando:

  * Vitórias
  * Empates
  * Derrotas

---

## 🧠 Regras de Negócio

* Vitória = 3 pontos
* Empate = 1 ponto
* Derrota = 0 pontos

---

## 📁 Fonte dos Dados

Os dados utilizados neste projeto foram obtidos em:

👉 [https://www.kaggle.com/datasets/gustavomartino/brasileirao](https://www.kaggle.com/datasets/gustavomartino/brasileirao)

---

## 🛠️ Tecnologias Utilizadas

* Python
* Tkinter
* Matplotlib
* NumPy
* Pandas

---

## 📌 Possíveis Melhorias

* 📈 Adicionar gráfico de pontuação acumulada
* 🎨 Melhorar o design (tema escuro / moderno)
* 🌐 Transformar em aplicação web (ex: React + API)
* ⚡ Otimizar performance na troca de time
* 📊 Adicionar mais métricas (saldo de gols, aproveitamento)

---

## 👨‍💻 Autor

Projeto desenvolvido para fins de estudo e prática com visualização de dados e interfaces gráficas em Python.

---