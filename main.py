import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from tkinter import ttk
from tkinter import *
import statistics

df = pd.read_csv("dados_2007-2023.csv")
TIME_BUSCADO = "Flamengo"
lista_json = df.to_dict(orient="records")
lista_times = sorted(
    set(item["mandante"] for item in lista_json) |
    set(item["time_fora"] for item in lista_json)
)

TAMANHO_GRAFICO_1_X = 7.5
TAMANHO_GRAFICO_1_Y = 5.5

TAMANHO_GRAFICO_2_X = 4.5
TAMANHO_GRAFICO_2_Y = 4.5

TAMANHO_GRAFICO_3_X = 6.8
TAMANHO_GRAFICO_3_Y = 5

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

    for ano in range(2007, 2024):
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
        if dados["nome_time"].find(nome_time) != -1:
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
        if isinstance(widget, FigureCanvasTkAgg):
            widget.destroy()

def recriar_grafico1():
    # garantir que anos sejam inteiros (evita 2010.5 etc)
    anos = [int(ano) for ano in dados["anos"]]

    fig = Figure(figsize=(TAMANHO_GRAFICO_1_X, TAMANHO_GRAFICO_1_Y))
    ax = fig.add_subplot(111)

    x = np.arange(len(anos))
    width = 0.25

    # barras
    bars_vitorias = ax.bar(x - width, dados["vitorias"], width, label="Vitórias")
    bars_empates = ax.bar(x, dados["empates"], width, label="Empates")
    bars_derrotas = ax.bar(x + width, dados["derrotas"], width, label="Derrotas")

    # eixo X (CORRIGIDO)
    ax.set_xticks(x)
    ax.set_xticklabels(anos, rotation=45, ha='right', fontsize=8)

    # títulos
    ax.set_title("Desempenho por Ano")
    ax.set_ylabel("Pontos")

    # legenda
    ax.legend()

    # função para colocar valor acima da barra
    def adicionar_rotulos(barras):
        for barra in barras:
            altura = barra.get_height()
            ax.text(
                barra.get_x() + barra.get_width() / 2,
                altura + 0.3,  # pequeno espaço acima
                f"{int(altura)}",
                ha='center',
                va='bottom',
                fontsize=8
            )

    # aplicar nos 3 conjuntos
    adicionar_rotulos(bars_vitorias)
    adicionar_rotulos(bars_empates)
    adicionar_rotulos(bars_derrotas)

    # ajustar layout (ESSENCIAL)
    fig.tight_layout()

    # renderizar no Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().place(x=0, y=50)

def recriar_grafico2():
    fig = Figure(figsize=(TAMANHO_GRAFICO_2_X, TAMANHO_GRAFICO_2_Y))
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

def recriar_grafico3():
    dados = calcular_variancia_e_desvio_padrao_dados_times(lista_json)

    nomes = [t["nome_time"] for t in dados]
    variancias = [t["variancia"] for t in dados]
    desvios = [t["desvio_padrao"] for t in dados]

    media_variancia = np.mean(variancias)
    media_desvio = np.mean(desvios)

    fig = Figure(figsize=(TAMANHO_GRAFICO_3_X, TAMANHO_GRAFICO_3_Y))
    ax = fig.add_subplot(111)

    # pontos
    ax.scatter(desvios, variancias)

    # nomes (opcional - pode poluir)
    for i, nome in enumerate(nomes):
        ax.text(desvios[i], variancias[i], nome, fontsize=7)

    # linhas de média (CRUCIAL)
    ax.axhline(media_variancia, linestyle='--')
    ax.axvline(media_desvio, linestyle='--')

    ax.set_xlabel("Desvio Padrão")
    ax.set_ylabel("Variância")
    ax.set_title("Consistência dos Times")

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame_grafico3)
    canvas.draw()
    canvas.get_tk_widget().place(x=0, y=100)

def calcular_variancia_dados(dados):
    return np.var(dados)

def calcular_desvio_padrao_dados(dados):
    return np.std(dados)

def atualizar_dashboard(event=None):
    global dados, pontuacao_por_ano, total_de_vitorias
    global label_vitorias, label_pontos

    time_selecionado = combo_time.get()

    # recalcular dados
    dados = busca_jogos_por_nome_time(lista_json, time_selecionado)
    pontuacao_por_ano = calcular_pontuacao_por_ano(dados)
    total_de_vitorias = sum(dados["vitorias"])
    ano_melhor_resultado_time_especifico = ano_melhor_resultado_time(time_selecionado)
    janela.title(f"Dashboard Brasileirão 1ª Divisão 2007-2023 - {time_selecionado}")
    app_nome.config(text=f"Dashboard Brasileirão 1ª Divisão 2007-2023 - {time_selecionado}")

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
    limpar_grafico(frame_grafico3)

    recriar_grafico1()
    recriar_grafico2()
    recriar_grafico3()


dados = busca_jogos_por_nome_time(lista_json, TIME_BUSCADO)
ano_melhor_resultado = ano_melhor_resultado_time()
resultado_maximo_times_lista = [time for time in resultado_maximo_todos_os_times(lista_json)]

resultado_maximo_times = [time for time in resultado_maximo_times_lista if time["time"] == TIME_BUSCADO][0]



ano_melhor_resultado_time_especifico = ano_melhor_resultado_time(TIME_BUSCADO)
total_de_vitorias = sum(dados["vitorias"])
pontuacao_por_ano = calcular_pontuacao_por_ano(dados)

def transformar_dados(lista):
    df = pd.DataFrame(lista)

    # Criar dois DataFrames: mandante e visitante
    mandante = df[['temporada', 'mandante', 'gols_mandante', 'gols_time_fora']].copy()
    mandante.columns = ['ano', 'time', 'gols_pro', 'gols_contra']

    visitante = df[['temporada', 'time_fora', 'gols_time_fora', 'gols_mandante']].copy()
    visitante.columns = ['ano', 'time', 'gols_pro', 'gols_contra']

    # Juntar tudo
    jogos = pd.concat([mandante, visitante], ignore_index=True)

    # Criar resultado
    def resultado(row):
        if row['gols_pro'] > row['gols_contra']:
            return 'vitoria'
        elif row['gols_pro'] < row['gols_contra']:
            return 'derrota'
        else:
            return 'empate'

    jogos['resultado'] = jogos.apply(resultado, axis=1)

    # Agrupar
    agrupado = jogos.groupby(['time', 'ano', 'resultado']).size().unstack(fill_value=0)

    # Garantir colunas
    for col in ['vitoria', 'empate', 'derrota']:
        if col not in agrupado:
            agrupado[col] = 0

    agrupado['total_jogos'] = agrupado.sum(axis=1)

    # Montar estrutura final
    resultado_final = []

    for time, grupo in agrupado.groupby(level=0):
        grupo = grupo.reset_index(level=0, drop=True).sort_index()

        resultado_final.append({
            'nome_time': time,
            'anos': grupo.index.tolist(),
            'vitorias': grupo['vitoria'].tolist(),
            'empates': grupo['empate'].tolist(),
            'derrotas': grupo['derrota'].tolist(),
            'total_jogos': grupo['total_jogos'].tolist()
        })

    return resultado_final

def calcular_variancia_e_desvio_padrao_dados_times(lista):
    dados = list(map(lambda x: {"nome_time": x["nome_time"], "pontos": (x["vitorias"] * 3) + x["empates"]}, transformar_dados(lista)))
    dados = list(
        map(
            lambda x : {
                "nome_time" : x["nome_time"],
                "variancia": float(calcular_variancia_dados(x["pontos"])),
                "desvio_padrao": float(calcular_desvio_padrao_dados(x["pontos"]))
                }
             ,
             dados
        )
    )
    return dados

# Variáveis de gráfico

TITULO = f"Dashboard Brasileirão 1ª Divisão 2007-2023 - {TIME_BUSCADO}"
BRANCO = "#ffffff"
CINZA = "#676767"
PRETO = "#000000"
AZUL = "#3780c9"
AZUL_MARINHO = "#1b3a5c"
VERDE = "#33b88b"

janela = Tk()
janela.title(TITULO)
janela.geometry("1920x700")
janela.resizable(width=True, height=True)

frame_top = Frame(janela, width=1920, height=60, pady=0, padx=0, bg=BRANCO, relief="flat")
frame_top.grid(row=0, column=0)
combo_time = ttk.Combobox(frame_top, values=lista_times, state="readonly")
combo_time.set(TIME_BUSCADO)
combo_time.place(x=900, y=20)

combo_time.bind("<<ComboboxSelected>>", atualizar_dashboard)

frame_quadro = Frame(janela, width=1920, height=700, pady=15, padx=7, relief="flat")
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

recriar_grafico1()

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

frame_grafico3, _, _ = criar_card(
    frame_quadro,
    "Variância e Desvio padrão das pontuações",
    "Consistência dos times",
    "",
    pos_x=1230,
    pos_y=0,
    tamanho_frame_x=700,
    tamanho_frame_y=610
)

recriar_grafico2()
recriar_grafico3()

janela.mainloop()