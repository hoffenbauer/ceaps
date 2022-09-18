import json
import pandas as pd
import plotly.express as px
import requests


def consulta_cnpj(df):
    cnpjs = [x for x in df["CNPJ_CPF"].unique() if len(x) == 18]

    dados_cnpj = ["cnpj", "uf", "municipio", "razao_social", "nome_fantasia",
                  "porte", "cnae_fiscal_descricao", "data_inicio_atividade"]

    empresas = pd.DataFrame(columns=dados_cnpj)

    cont = 0

    for x in cnpjs:
        request = requests.get("https://minhareceita.org/"+x)
        responde_json = request.json()
        nova_linha = [responde_json.get(x) for x in dados_cnpj]
        empresas.loc[len(empresas)] = nova_linha
        cont += 1
        if cont % 100 == 0 or cont == len(cnpjs):
            print(f"{cont} CNPJs processados")

    empresas["cnpj_extenso"] = [
        x for x in df["CNPJ_CPF"].unique() if len(x) == 18]
    empresas.to_csv("./dados/dados_empresas_ceaps_2021.csv", index=False)


def gera_mapa(df):
    estados_geo = json.load(open("./dados/brasil_estados.json"))

    fig_mapa = px.choropleth(df, geojson=estados_geo, locations=df.index, width=1000, height=1000,
                             color="VALOR_REEMBOLSADO", projection="mercator", color_continuous_scale=px.colors.sequential.YlOrRd)

    hover_mapa = ["<b>UF</b>: %{location}", "<b>Gasto total</b>: R$ %{z:,}"]
    hover_mapa = "<br>".join(hover_mapa)

    fig_mapa.update_traces(hovertemplate=hover_mapa)

    fig_mapa.update_geos(fitbounds="geojson", visible=False)

    fig_mapa.update_coloraxes(
        colorbar_len=0.4, colorbar_title_text="Valor gasto pelos<br>senadores por UF", colorbar_thickness=15)

    fig_mapa.update_layout(separators=",.", margin={
                           "r": 0, "t": 0, "l": 0, "b": 0}, hoverlabel=dict(font_size=18))
