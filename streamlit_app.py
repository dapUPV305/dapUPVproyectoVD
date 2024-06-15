import streamlit as st
import pandas as pd
import altair as alt
from st_pages import Page, show_pages, add_page_title

def run():
    st.set_page_config(
        page_title="Principal",
        page_icon="⚽",
    )
    show_pages(
        [
            Page("streamlit_app.py", "Home", "⚽"),
            Page("pages/plots.py", "Datos por temporadas", "📊"),
        ]
    )

    st.markdown("# Bienvenidos a mi proyecto: Datos por equipos de la Liga Española de Fútbol")
    st.write(
        """
        En este proyecto se podrá ver información sobre los equipos de fútbol de la liga y sus resultados a través de las temporadas.\n
        Primero comencemos viendo quienas han sido campeones de la liga y cuantos títulos poseen.    
        """
    )

    winners_plot()

def winners_plot():
    @st.cache_data
    def get_winners_table():
        df = pd.read_excel("WinnersSpanishLeague.xlsx")
        return df

    try:
        df = get_winners_table()
        teams = st.multiselect(
            "##### Elige algún campeón de la liga:", set(df.Team.values.tolist()), ["FC Barcelona", "Real Madrid", "Real Betis", "Athletic Bilbao"]
        )
        if not teams:
            st.error("Por favor, seleccione algún equpipo.")
        else:
            data = df[(df["Season"].isin([x for x in df['Season'] if not x in [1938,1937,1939]])) & df['Team'].isin(teams)].groupby("Team").count()
            st.write("### Títulos ganados desde las temporadas **1929-2023**")

            data = data.reset_index()
            data = data.rename(
                columns={"Team": "Equipo", "Season": "Títulos"}
            )
            chart = (
                alt.Chart(data)
                .mark_bar()
                .encode(
                    x=alt.X("Equipo:N", axis=alt.Axis(labelAngle=-45)),
                    y="Títulos:Q",
                    color=alt.Color('Títulos', legend=None)
,
                )
            )
            st.altair_chart(chart, use_container_width=True)
    except Exception as e:
        st.error(
            """
            Error: %s
            """
            % e
        )

if __name__ == "__main__":
    run()
