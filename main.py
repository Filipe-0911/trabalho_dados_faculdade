import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from tkinter import ttk
from tkinter import *
import json

df = pd.read_csv("dados_2007-2023.csv")
TIME_BUSCADO = "Flamengo"
lista_json = df.to_dict(orient="records")
lista_times = sorted(
    set(item["mandante"] for item in lista_json) |
    set(item["time_fora"] for item in lista_json)
)

tamanho_grafico_1_x = 8
tamanho_grafico_1_y = 5.5

tamanho_grafico_2_x = 4.5
tamanho_grafico_2_y = 4.5

def match_and(item, filtros):
    return all(item.get(k) == v for k, v in filtros.items())

def match_or(item, condicoes):
    return any(match_and(item, cond) for cond in condicoes)

def filtrar(lista, filtros=None, regras=None):
    filtros = filtros or {}
    regras = regras or []
    return [
        item for item in lista
        if (
            all(item.get(k) == v for k, v in filtros.items() if k != "or")
            
            and (
                "or" not in filtros or
                any(all(item.get(k) == v for k, v in cond.items()) for cond in filtros["or"])
            )

            and all(regra(item) for regra in regras)
        )
    ]

def cria_filtros(ano, time):
    return {
        "temporada": ano,
        "or": [
            {"mandante": time},
            {"time_fora": time}
        ]
    }

def cria_regras(filtros):
    return {
            "vitorias": lambda p: (
                    (
                        p["mandante"] == filtros["or"][0]["mandante"] and 
                        p["gols_mandante"] > p["gols_time_fora"]
                    )
                or
                    (
                        p["time_fora"] == filtros["or"][1]["time_fora"] and 
                        p["gols_time_fora"] > p["gols_mandante"]    
                    )
            ),
            "empates": lambda p: (
                    (
                        p["mandante"] == filtros["or"][0]["mandante"] 
                        and 
                        p["gols_mandante"] == p["gols_time_fora"] 
                    )
                or 
                    (
                        p["time_fora"] == filtros["or"][1]["time_fora"] 
                        and 
                        p["gols_time_fora"] == p["gols_mandante"]
                    )
            ),
            "derrotas": lambda p: (
                    (
                        p["mandante"] == filtros["or"][0]["mandante"] 
                        and 
                        p["gols_mandante"] < p["gols_time_fora"] 
                    )
                or 
                    (
                        p["time_fora"] == filtros["or"][1]["time_fora"] 
                        and 
                        p["gols_time_fora"] < p["gols_mandante"]
                    )
                ),
    }

def busca_jogos_por_nome_time(lista, nome_time):
    anos = []
    vitorias = []
    derrotas = []
    empates = []

    for ano in range(2007, 2023):
        filtros = cria_filtros(ano, nome_time)
        regras_vitoria = cria_regras(filtros)["vitorias"]
        regras_empates = cria_regras(filtros)["empates"]
        regras_derrotas = cria_regras(filtros)["derrotas"]

        v = len(filtrar(lista, filtros, [regras_vitoria]))
        e = len(filtrar(lista, filtros, [regras_empates]))
        d = len(filtrar(lista, filtros, [regras_derrotas]))

        anos.append(ano)
        vitorias.append(v)
        empates.append(e)
        derrotas.append(d)

    return {
        "nome_time": nome_time,
        "anos": anos,
        "vitorias": vitorias,
        "empates": empates,
        "derrotas": derrotas,
        "total_jogos": [v + e + d for v, e, d in zip(vitorias, empates, derrotas)]
    }

def ano_melhor_resultado_time(nome_time=TIME_BUSCADO):
    melhor_ano = None
    melhor_resultado = -1

    for ano, v, e, d in zip(dados["anos"], dados["vitorias"], dados["empates"], dados["derrotas"]):
        resultado = v * 3 + e  # Vitória vale 3 pontos, empate vale 1 ponto
        if dados["nome_time"].find(nome_time):
            if resultado > melhor_resultado:
                melhor_resultado = resultado
                melhor_ano = ano

    return {"nome_time": nome_time, "melhor_ano": melhor_ano, "melhor_resultado": melhor_resultado}

def resultado_maximo_todos_os_times(lista):
    resultados = []

    for i, time in enumerate(lista_times):
        dados_time = busca_jogos_por_nome_time(lista, time)
        resultado_time = sum(dados_time["vitorias"]) * 3 + sum(dados_time["empates"])
        resultados.append({"time": time, "resultado": resultado_time, "vitorias": sum(dados_time["vitorias"])})

    return list(map(lambda x, i: {**x, "ranking_geral": i + 1}, 
                    sorted(
                        resultados,
                        key=lambda x: (x["resultado"], x["vitorias"]),
                        reverse=True
                    )
                    , range(len(resultados))))

def calcular_pontuacao_por_ano(dados):
    pontuacao_por_ano = []
    
    for index, ano in enumerate(dados["anos"]):
        obj = {
                "ano": ano,
                "vitorias": dados["vitorias"][index],
                "empates": dados["empates"][index],
                "derrotas": dados["derrotas"][index],
                "pontuacao": dados["vitorias"][index] * 3 + dados["empates"][index]
            }
        pontuacao_por_ano.append(obj)

    return pontuacao_por_ano

def criar_card(frame_pai, titulo, valor, melhor_ano, pos_x, pos_y, tamanho_frame_x=200, tamanho_frame_y=100, ultimo_texto=""):
    frame = Frame(frame_pai, width=tamanho_frame_x, height=tamanho_frame_y, bg=BRANCO, relief="flat")
    frame.place(x=pos_x, y=pos_y)

    Label(frame, width=1, height=1, bg=AZUL).place(x=0, y=0)

    Label(
        frame,
        text=titulo,
        font=("Ivy 10 bold"),
        bg=BRANCO,
        fg=PRETO
    ).place(x=20, y=5)

    label_valor = Label(
        frame,
        text=valor,
        font=("Ivy 18 bold"),
        bg=BRANCO,
        fg=AZUL_MARINHO
    )
    label_valor.place(x=40, y=35)

    label_ano = Label(
        frame,
        text=ultimo_texto,
        font=("Ivy 10 bold"),
        bg=BRANCO,
        fg=VERDE
    )
    label_ano.place(x=20, y=70)

    return frame, label_valor, label_ano

def limpar_grafico(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def atualizar_dashboard(event=None):
    global dados, pontuacao_por_ano, total_de_vitorias
    global label_vitorias, label_pontos

    time_selecionado = combo_time.get()

    # recalcular dados
    dados = busca_jogos_por_nome_time(lista_json, time_selecionado)
    pontuacao_por_ano = calcular_pontuacao_por_ano(dados)
    total_de_vitorias = sum(dados["vitorias"])
    ano_melhor_resultado_time_especifico = ano_melhor_resultado_time(time_selecionado)
    janela.title(f"Dashboard Brasileirão 1ª Divisão 2012-2022 - {time_selecionado}")
    app_nome.config(text=f"Dashboard Brasileirão 1ª Divisão 2012-2022 - {time_selecionado}")

    resultado_time = [
        t for t in resultado_maximo_todos_os_times(lista_json)
        if t["time"] == time_selecionado
    ][0]

    # atualizar textos corretamente
    label_vitorias.config(text=total_de_vitorias)
    label_pontos.config(text=resultado_time["resultado"])
    label_ano1.config(text=f"Melhor Ano: {ano_melhor_resultado_time_especifico['melhor_ano']}")
    label_ano2.config(text=f"Ranking Geral: {resultado_time['ranking_geral']}º")

    # limpar e recriar gráficos
    limpar_grafico(frame_grafico)
    limpar_grafico(frame_grafico2)

    recriar_grafico1()
    recriar_grafico2()


dados = busca_jogos_por_nome_time(lista_json, TIME_BUSCADO)
ano_melhor_resultado = ano_melhor_resultado_time()
resultado_maximo_times_lista = [time for time in resultado_maximo_todos_os_times(lista_json)]
# print(resultado_maximo_times_lista)
resultado_maximo_times = [time for time in resultado_maximo_times_lista if time["time"] == TIME_BUSCADO][0]

# print(json.dumps(resultado_maximo_times_lista, indent=4))

ano_melhor_resultado_time_especifico = ano_melhor_resultado_time(TIME_BUSCADO)
total_de_vitorias = sum(dados["vitorias"])
pontuacao_por_ano = calcular_pontuacao_por_ano(dados)

TITULO = f"Dashboard Brasileirão 1ª Divisão 2012-2022 - {TIME_BUSCADO}"
BRANCO = "#efefef"
CINZA = "#676767"
PRETO = "#000000"
AZUL = "#3780c9"
AZUL_MARINHO = "#1b3a5c"
VERDE = "#33b88b"

janela = Tk()
janela.title(TITULO)
janela.geometry("1200x700")
janela.resizable(width=False, height=False)

frame_top = Frame(janela, width=1370, height=60, pady=0, padx=0, bg=BRANCO, relief="flat")
frame_top.grid(row=0, column=0)
combo_time = ttk.Combobox(frame_top, values=lista_times, state="readonly")
combo_time.set(TIME_BUSCADO)
combo_time.place(x=900, y=20)

combo_time.bind("<<ComboboxSelected>>", atualizar_dashboard)

frame_quadro = Frame(janela, width=1370, height=700, pady=15, padx=7, relief="flat")
frame_quadro.grid(row=1, column=0, pady=6, sticky=NW)

#config frametop
app_nome = Label(frame_top, text=TITULO, height=2, padx=5, pady=5, font=("Ivy 14 bold", 20), bg=BRANCO, fg=PRETO, relief='flat', anchor=N)
app_nome.place(x=0, y=5)



#configurando framequadro
# Total de vitórias
frame1, label_vitorias, label_ano1 = criar_card(
    frame_quadro,
    "Total de Vitórias",
    total_de_vitorias,
    ano_melhor_resultado_time_especifico['melhor_ano'],
    ultimo_texto=f"Melhor Ano: {ano_melhor_resultado_time_especifico['melhor_ano']}",
    pos_x=0,
    pos_y=0
)

#configurando framequadro 2
# Total de pontos
frame2, label_pontos, label_ano2 = criar_card(
    frame_quadro,
    "Total de Pontos",
    resultado_maximo_times['resultado'],
    resultado_maximo_times['ranking_geral'],
    ultimo_texto=f"Ranking Geral: {resultado_maximo_times['ranking_geral']}º",
    pos_x=210,
    pos_y=0
)

#configurando framequadro 3
#quantidade de vitórias, empates e derrotas por ano

frame_grafico, _, _ = criar_card(
    frame_quadro,
    "Quantidade de vitórias, empates e derrotas por ano",
    "",
    "",
    tamanho_frame_x=800,
    tamanho_frame_y=610,
    pos_x=420,
    pos_y=0
)

fig = Figure(figsize=(tamanho_grafico_1_x, tamanho_grafico_1_y))
ax = fig.add_subplot(111)

x = np.arange(len(dados["anos"]))
width = 0.20

bars_vitorias = ax.bar(x - width, dados["vitorias"], width, label="Vitórias")
bars_empates = ax.bar(x, dados["empates"], width, label="Empates")
bars_derrotas = ax.bar(x + width, dados["derrotas"], width, label="Derrotas")

# eixo X
ax.set_xticks(x)
ax.set_xticklabels(dados["anos"])

# títulos
ax.set_title("Desempenho por Ano")
ax.set_ylabel("Jogos")

# legenda
ax.legend()

# função para colocar valor acima da barra
def adicionar_rotulos(barras):
    for barra in barras:
        altura = barra.get_height()
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            altura,
            f"{int(altura)}",
            ha='center',
            va='bottom',
            fontsize=8
        )

# aplicar nos 3 conjuntos
adicionar_rotulos(bars_vitorias)
adicionar_rotulos(bars_empates)
adicionar_rotulos(bars_derrotas)

# inserir no tkinter
canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
canvas.draw()
canvas.get_tk_widget().place(x=0, y=50)



#grafico 2

frame_grafico2, _, _ = criar_card(
    frame_quadro,
    "Pontuação por ano",
    "",
    "",
    pos_x=0,
    pos_y=110,
    tamanho_frame_x=410,
    tamanho_frame_y=500
)

fig = Figure(figsize=(tamanho_grafico_2_x, tamanho_grafico_2_y))
ax = fig.add_subplot(111)

# separar dados
anos = [item["ano"] for item in pontuacao_por_ano]
pontuacoes = [item["pontuacao"] for item in pontuacao_por_ano]

y = np.arange(len(anos))

bars = ax.barh(y, pontuacoes)

# eixo Y com os anos (mesmo repetidos)
ax.set_yticks(y)
ax.set_yticklabels(anos)

ax.set_title("Pontuação por Ano")
ax.set_xlabel("Pontuação")

# valores ao lado das barras
for barra in bars:
    largura = barra.get_width()
    ax.text(
        largura + 1,
        barra.get_y() + barra.get_height() / 2,
        f"{int(largura)}",
        va='center',
        fontsize=8
    )

# opcional: inverter ordem
ax.invert_yaxis()

# inserir no tkinter
canvas = FigureCanvasTkAgg(fig, master=frame_grafico2)
canvas.draw()
canvas.get_tk_widget().place(x=0, y=40)


def recriar_grafico1():
    fig = Figure(figsize=(tamanho_grafico_1_x, tamanho_grafico_1_y))
    ax = fig.add_subplot(111)

    x = np.arange(len(dados["anos"]))
    width = 0.20

    bars_vitorias = ax.bar(x - width, dados["vitorias"], width, label="Vitórias")
    bars_empates = ax.bar(x, dados["empates"], width, label="Empates")
    bars_derrotas = ax.bar(x + width, dados["derrotas"], width, label="Derrotas")

    # eixo X
    ax.set_xticks(x)
    ax.set_xticklabels(dados["anos"])

    # títulos
    ax.set_title("Desempenho por Ano")
    ax.set_ylabel("Jogos")

    # legenda
    ax.legend()

    # função para colocar valor acima da barra
    def adicionar_rotulos(barras):
        for barra in barras:
            altura = barra.get_height()
            ax.text(
                barra.get_x() + barra.get_width() / 2,
                altura,
                f"{int(altura)}",
                ha='center',
                va='bottom',
                fontsize=8
            )

    # aplicar nos 3 conjuntos
    adicionar_rotulos(bars_vitorias)
    adicionar_rotulos(bars_empates)
    adicionar_rotulos(bars_derrotas)

    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().place(x=0, y=50)

def recriar_grafico2():
    fig = Figure(figsize=(tamanho_grafico_2_x, tamanho_grafico_2_y))
    ax = fig.add_subplot(111)

    # separar dados
    anos = [item["ano"] for item in pontuacao_por_ano]
    pontuacoes = [item["pontuacao"] for item in pontuacao_por_ano]

    y = np.arange(len(anos))

    bars = ax.barh(y, pontuacoes)

    # eixo Y com os anos (mesmo repetidos)
    ax.set_yticks(y)
    ax.set_yticklabels(anos)

    ax.set_title("Pontuação por Ano")
    ax.set_xlabel("Pontuação")

    # valores ao lado das barras
    for barra in bars:
        largura = barra.get_width()
        ax.text(
            largura + 1,
            barra.get_y() + barra.get_height() / 2,
            f"{int(largura)}",
            va='center',
            fontsize=8
        )

    # opcional: inverter ordem
    ax.invert_yaxis()

    canvas = FigureCanvasTkAgg(fig, master=frame_grafico2)
    canvas.draw()
    canvas.get_tk_widget().place(x=0, y=40)

janela.mainloop()