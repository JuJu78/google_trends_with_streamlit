from urllib.error import URLError
import pytrends
from pytrends.request import TrendReq
import numpy as np
import pandas as pd
from pandas import ExcelWriter
import time
import datetime
from datetime import datetime, date, time
import streamlit as st
import re
import plotly.express as px
import time
import io

######
st.title("Google Trends App 🔥", anchor=None)
st.write("Cette petite app vous permet de vérifier en un coup d'oeil quels sont les mots-clés dont la tendance de \
                            recherche a le plus augmenté pendant l'année en cours par rapport à l'année dernière. \
                            Toutes les données sont issues de Google Trends. Il est conseillé de ne pas rentrer plus \
                            de 1 000 mots-clés par jour sous peine d'un énorme crashage 💣🧨!!! On vous aura prévenu 😘")

txt = st.text_area('Taper vos expressions [une par ligne]')
keywords = re.split('\n', txt)
groupkeywords = list(zip(*[iter(keywords)]*1))
groupkeywords = zip(*[iter(keywords)] * 1)
groupkeywords = [list(x) for x in groupkeywords]
dicti = {}
i = 1

bouton = st.button("Valider", key=None)
if bouton is True:
  for trending in groupkeywords:
    try:
      pytrends = TrendReq()
      pytrends.build_payload(trending, geo = 'FR', timeframe='today 5-y', gprop='')
      dicti[i] = pytrends.interest_over_time()
      i+=1
    except:
      print("il y a eu une erreur !")

  result = pd.concat(dicti, axis=1)
  result.columns = result.columns.droplevel(0)
  result.index.rename('Dates', inplace=True)
  result = result.drop('isPartial', axis=1)

  result['Dates'] = result.index

  #coucou = pd.to_datetime(result['Dates'], format='%Y')

  trends_2017 = result.filter(like='2017', axis=0)
  trends_2018 = result.filter(like='2018', axis=0)
  trends_2019 = result.filter(like='2019', axis=0)
  trends_2020 = result.filter(like='2020', axis=0)
  trends_2021 = result.filter(like='2021', axis=0)
  trends_2022 = result.filter(like='2022', axis=0)

  mean_2017 = trends_2017.mean(axis=0)
  mean_2018 = trends_2018.mean(axis=0)
  mean_2019 = trends_2019.mean(axis=0)
  mean_2020 = trends_2020.mean(axis=0)
  mean_2021 = trends_2021.mean(axis=0)
  mean_2022 = trends_2022.mean(axis=0)

  tendance_2017 = pd.DataFrame(mean_2017, columns=['2017'])
  tendance_2018 = pd.DataFrame(mean_2018, columns=['tendances 2018'])
  tendance_2019 = pd.DataFrame(mean_2019, columns=['tendances 2019'])
  tendance_2020 = pd.DataFrame(mean_2020, columns=['tendances 2020'])
  tendance_2021 = pd.DataFrame(mean_2021, columns=['tendances 2021'])
  tendance_2022 = pd.DataFrame(mean_2022, columns=['tendances 2022'])
  tendance_2017['2017'] = tendance_2017
  tendance_2017['2018'] = tendance_2018
  tendance_2017['2019'] = tendance_2019
  tendance_2017['2020'] = tendance_2020
  tendance_2017['2021'] = tendance_2021
  tendance_2017['2022'] = tendance_2022

  pipi = tendance_2017.transpose()

  #display a graph by years
  fig = px.line(pipi, title='tendance de recherche annuelle sur les 5 dernières années')
  st.plotly_chart(fig)

  #display a table by years
  tendance_2017["% d'évolution entre 2022 et 2021"] = (tendance_2017['2022'] -
                                                                             tendance_2017[
                                                                               '2021']) / tendance_2017[
                                                                              '2021']
  tendance_2017 = tendance_2017.reindex(columns=["% d'évolution entre 2022 et 2021", '2017', '2018', '2019', '2020',
                                                 '2021', '2022'])
  trends = tendance_2017.sort_values(by="% d'évolution entre 2022 et 2021", ascending=False)
  trends

  data_group_by_month = result.groupby(by=[pd.Grouper(key="Dates", freq="M")])
  trend_by_month = data_group_by_month.mean().T

  popo = trend_by_month.transpose()

  #display a graph by years
  figu = px.line(popo, title='tendance de recherche mensuelle sur les 5 dernières années')
  st.plotly_chart(figu)

  trend_by_month

  # Create a Pandas Excel writer using XlsxWriter as the engine.
  buffer = io.BytesIO()
  with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    trends.to_excel(writer, sheet_name='trend by year')
    trend_by_month.to_excel(writer, sheet_name='trend by month')
    writer.save()

    #dowload a excel file
    st.download_button(
      label="Exporter les tableaux au format Excel",
      data=buffer,
      file_name="trends.xlsx",
      mime="application/vnd.ms-excel"
    )
