import streamlit as st
import pandas as pd
import altair as alt
from st_pages import Page, show_pages, add_page_title


def data_historic():
    @st.cache_data
    def get_historic_data_matchs():
        df = pd.read_csv("spain.csv")
        winners_match = []
        loser_match = []

        for _, row in df.iterrows():
            if row['hgoal'] > row['vgoal']:
                winners_match.append(row['home'])
                loser_match.append(row['visitor'])
            elif row['hgoal'] < row['vgoal']:
                winners_match.append(row['visitor'])
                loser_match.append(row['home'])
            elif row['hgoal'] == row['vgoal']:
                winners_match.append("Draw")
                loser_match.append("Draw")

        df['winner'] = pd.Series(winners_match)
        df['loser'] = pd.Series(loser_match)

        return df

    try:
        df = get_historic_data_matchs()
        st.write("##### Selecciona un rango de temporadas")
        seasons_range = [x for x in range(1923, 2023) if not x in [
            1937, 1938, 1939]]
        selected_number_min = st.selectbox(
            'Desde:',
            seasons_range
        )
        selected_number_max = st.selectbox(
            'Hasta:',
            seasons_range,
            len(seasons_range)-1
        )
        teams = st.multiselect(
            "##### Elige algún equipo:", set(df.home.values.tolist()), [
                "FC Barcelona", "Real Madrid", "Real Betis", "Athletic Bilbao"]
        )

        if selected_number_min > selected_number_max:
            st.error("Por favor, seleccione un rango válido.")
        elif not teams:
            st.error("Por favor, seleccione al menos un equipo.")
        else:
            seasons_range = list(
                range(selected_number_min, selected_number_max+1))
            data_1 = df[df['winner'].isin(teams) & df['Season'].isin(seasons_range)][['winner', 'Season', 'Date']].groupby(
                ['Season', 'winner']).count().reset_index().rename(columns={'winner': 'Equipo', 'Date': 'Victorias', 'Season': 'Temporada'})
            a = df[df['home'].isin(teams) & df['Season'].isin(seasons_range)][[
                'home', 'hgoal']].rename(columns={'home': 'Equipo', 'hgoal': 'Goles'})
            b = df[df['visitor'].isin(teams) & df['Season'].isin(seasons_range)][[
                'visitor', 'vgoal']].rename(columns={'visitor': 'Equipo', 'vgoal': 'Goles'})
            data_2 = pd.concat([a, b])
            heatmap_data = df[(df['winner'].isin(teams)) & df['loser'].isin(teams) & df['Season'].isin(
                seasons_range)].groupby(['winner', 'loser']).count().reset_index()

            boxplot = alt.Chart(data_1).mark_boxplot().encode(
                x=alt.X("Equipo:N", axis=alt.Axis(labelAngle=0)),
                y='Victorias:Q',
                color=alt.Color('Equipo', legend=None)
            ).properties(
                title='Victorias por temporadas ({}-{})'.format(
                    selected_number_min, selected_number_max)
            )

            violin_plot = alt.Chart(data_2, width=200).transform_density(
                'Goles',
                as_=['Goles', 'Proporción'],
                extent=[0, data_2['Goles'].max()+1],
                groupby=['Equipo']
            ).mark_area(orient='horizontal').encode(
                alt.X('Proporción:Q')
                    .stack('center')
                    .impute(None)
                    .title(None)
                    .axis(labels=False, values=[0], grid=False, ticks=True),
                alt.Y('Goles:Q', axis=alt.Axis(values=list  (range(0, data_2['Goles'].max()+1)))),
                alt.Color('Equipo:N', legend=None),
                alt.Column('Equipo:N')
                    .spacing(0)
                    .header(titleOrient='bottom', labelOrient='bottom', labelPadding=0)
            ).configure_view(
                stroke=None
            ).properties(
                title='Proporción de número de goles anotados por partidos (temporadas {}-{})'.format(
                    selected_number_min, selected_number_max)
            )

            base = alt.Chart(heatmap_data).encode(
                x=alt.X('loser:O', title='Equipo perdedor', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('winner:O', title='Equipo ganador'),
            )

            text = base.mark_text().encode(
                text='Date:Q',
                color=alt.Color('Date', title='Victorias'),
            )

            # The correlation heatmap itself
            cor_plot = base.mark_rect().encode(
                color=alt.Color('Date', title='Victorias'),
            ).properties(
                title='Distribución de victorias entre los equipos (temporadas {}-{})'.format(
                    selected_number_min, selected_number_max)
            )

            st.altair_chart(boxplot, use_container_width=True)
            st.altair_chart(violin_plot, use_container_width=False)
            st.altair_chart(cor_plot + text, use_container_width=True)
    except Exception as e:
        st.error(
            """
            Error: %s
            """
            % e
        )


st.set_page_config(page_title="Datos históricos", page_icon="📊")
show_pages(
    [
        Page("streamlit_app.py", "Home", "⚽"),
        Page("pages/plots.py", "Datos por temporadas", "📊"),
    ]
)
st.markdown("# Datos históricos por equipos")
st.sidebar.header("Datos históricos")

data_historic()
