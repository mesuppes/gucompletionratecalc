import pandas as pd
from collections import Counter
import streamlit as st
import os

def cargar_y_mostrar_tabla(file):
    if file is not None:

        collection = pd.read_csv(file,sep=";")

        collection = pd.DataFrame(collection)

        collection['suma_cantidad_cartas'] = collection['plain_quantity'] + collection['meteorite_quantity'] + collection['shadow_quantity'] + collection['gold_quantity'] + collection['diamond_quantity']

        inventario=pd.DataFrame()

        inventario['cartas']= collection["description"]
        inventario['cantidad']= collection["suma_cantidad_cartas"]

        lista_inventarios = []

        for index, row in inventario.iterrows():
            carta = row['cartas']
            cantidad = row['cantidad']
            
            if cantidad > 0:
                lista_inventarios.extend([carta] * cantidad)

        top_decks = pd.read_excel('resultados.xlsx')

        top_decks = pd.DataFrame(top_decks)

        grupos = top_decks.groupby('name')

        dataframes_por_valor_x = {valor: grupo for valor, grupo in grupos}

        tabla=[]

        for grupo in grupos:

            df_para_valor_x_2 = dataframes_por_valor_x.get(grupo[0])

            deck=pd.DataFrame()

            deck['cartas']= df_para_valor_x_2["cards"]
            deck['cantidad']= df_para_valor_x_2["quantity"]

            lista_deck = []

            for index, row in deck.iterrows():
                carta = row['cartas']
                cantidad = row['cantidad']
                
                if cantidad > 0:
                    lista_deck.extend([carta] * cantidad)

            faltan = Counter(lista_deck)-Counter(lista_inventarios)

            faltanstr =  str(dict(faltan))

            link_deck = "https://gudecks.com"+grupo[1].link.iloc[[0]].values[0]

            win_rate = grupo[1].win_rate.iloc[[0]].values[0]

            games = grupo[1].games.iloc[[0]].values[0]

            tabla.append([str(grupo[0][2:-2]),link_deck,win_rate,games,str(round(((30-sum(faltan.values()))/30)*100,2))+" % ("+str(sum(faltan.values()))+" cards missing)",round((float(win_rate[:-1])/100)*int(games)*round(((30-sum(faltan.values()))/30),2),2),faltanstr])

        tabla = pd.DataFrame(tabla, columns=["Deck","Link","Win rate","Matches","Deck's completion rate","Z Index","Missing cards"])

        st.dataframe(tabla,column_config={
        "Link": st.column_config.LinkColumn(
            "GUdeck's link",
            display_text="GUdeck's link",
            help="The GUdeck's link of the deck",
            max_chars=200,
        ),
        "Deck's completion rate": st.column_config.Column(help="(30 - # deck's cards you owned)/30 % (# cards you need to complete the deck)"),
        "Missing cards": st.column_config.ListColumn(width = "large", help="The cards that you need to complete the deck"),
        "Z Index":  st.column_config.Column(help="This index is calculated by multiplying deck's win rate by deck's games by deck's completion rate.")
        },hide_index=True,width=1200)

st.set_page_config(
    page_title="GU completion rate calculator",
    page_icon="📟",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        #'Report a bug': "mailto:mesuppes22@gmail.com?subject=GuCard rate calculator bug",
        'About': "Gods Unchained's Top Decks completion rate calculator"
    }
)

date = os.path.getmtime('resultados.xlsx')

st.title("Gods Unchained's Top Decks completion rate calculator")
st.write("This is the Gods Unchained's Top Decks completion rate calculator. It compares the current top decks according to https://gudecks.com/meta/top-decks with your GUForge card inventory.") 
st.write("The only thing you have to do is go to https://guforge.com, type your Gods Unchained username and download the inventory of your cards in .csv format (green icon next to 'INVENTORY'). After that, upload that csv file in the box below and the app will calculate the completion rate for each top deck. It will also show you what cards are missing from your inventory to complete each deck.")
st.write("For now, your csv file is compared to the top decks according to gudecks, updating them once a day.")
st.write("Last update: "+pd.to_datetime(date, unit="s").strftime('%d-%m-%Y %H:%M')+" UTC")
#st.write("This is a project in development and not fully tested, any suggestion or advice is welcome at @gu. If you like it, you can collaborate with cryptos or gods unchained cards in 0xfsa, thanks in advance!")

file = st.file_uploader("Upload your Inventory from GUForge.com (.csv)", type=["csv"])

cargar_y_mostrar_tabla(file)