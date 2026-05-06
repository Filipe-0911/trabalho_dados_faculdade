import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("dados.csv")

lista_json = df.to_dict(orient="records")

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

anos = []
vitorias = []
derrotas = []
empates = []

for ano in range(2012, 2023):
    filtros = cria_filtros(ano, "Flamengo-RJ")
    regras_vitoria = cria_regras(filtros)["vitorias"]
    regras_empates = cria_regras(filtros)["empates"]
    regras_derrotas = cria_regras(filtros)["derrotas"]

    v = len(filtrar(lista_json, filtros, [regras_vitoria]))
    e = len(filtrar(lista_json, filtros, [regras_empates]))
    d = len(filtrar(lista_json, filtros, [regras_derrotas]))

    anos.append(ano)
    vitorias.append(v)
    empates.append(e)
    derrotas.append(d)
    
x = np.arange(len(anos))
width = 0.3

plt.figure(figsize=(10,5))

plt.bar(x - width, vitorias, width, label="Vitórias")
plt.bar(x, empates, width, label="Empates")
plt.bar(x + width, derrotas, width, label="Derrotas")

plt.xticks(x, anos)

plt.xlabel("Ano")
plt.ylabel("Quantidade de Jogos")
plt.title("Desempenho do Flamengo por Ano")

plt.legend()

plt.tight_layout()
plt.show()
