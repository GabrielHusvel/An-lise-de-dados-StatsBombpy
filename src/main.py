
# 1 - Preparar o ambiente de desenvolvimento:
#     Crie um ambiente virtual para seu projeto utilizando uma ferramenta como venv, virtualenv ou pipenv.
#     Instale as bibliotecas necessárias (Streamlit, statsbombpy, mplsoccer, matplotlib, entre outras).

# 2 - Estruturar o projeto:
#     Crie um repositório no GitHub para hospedar o código do seu projeto.
#     Garanta que o repositório contenha um arquivo requirements.txt com as dependências necessárias para rodar o projeto.
#     Organize o código de forma clara, criando funções separadas para carregar os dados, gerar as visualizações e construir a interface do dashboard.


import streamlit as st
import pandas as pd
from statsbombpy import sb
from mplsoccer import Pitch, VerticalPitch
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns
import numpy as np
import time


# Streamlit para o modo wide
st.set_page_config(layout="wide")

# Título do App
st.title('Análise de Dados do StatsBombpy')
abas = st.tabs(["Análise por dataframes", "Visualizações Gráficas", "Comparar jogadores"])


# 3-  Definir a estrutura do dashboard:
#     Desenvolva uma interface interativa em Streamlit que permita ao usuário selecionar:
#         Um campeonato específico.
#         Uma temporada (ano).
#         Uma partida ou jogador para análise.
#     Organize o layout do dashboard em colunas, usando columns, sidebars, containers e tabs para melhorar a usabilidade.


with abas[0]:

    with st.container():
        st.subheader('Selecione Competição, Temporada e Partida')


        st.subheader('Competições e Temporadas')
        competitions = sb.competitions()
        st.dataframe(competitions)

        # Competição e Temporada na barra lateral
        competition_id = st.sidebar.selectbox(
            'Escolha a Competição',
            competitions['competition_name'].unique()
        )


        season_id = st.sidebar.selectbox(
            'Escolha a Temporada',
            competitions[competitions['competition_name'] == competition_id]['season_name'].unique()
        )

        # IDs da competição e temporada 
        competition_selected = competitions[competitions['competition_name'] == competition_id]
        season_selected = competition_selected[competition_selected['season_name'] == season_id]
        comp_id = int(season_selected['competition_id'].iloc[0])
        season_id = int(season_selected['season_id'].iloc[0])



        # Partidas da competição e temporada
        matches = sb.matches(competition_id=comp_id, season_id=season_id)

        # Ordenar partidas por data
        matches = matches.sort_values(by='match_date')

        # Opções com time e data para exibição
        match_id = st.sidebar.selectbox(
            'Escolha a Partida',
            matches['match_id'].unique(),
            format_func=lambda x: f"{matches[matches['match_id'] == x]['home_team'].values[0]} vs {matches[matches['match_id'] == x]['away_team'].values[0]} - {matches[matches['match_id'] == x]['match_date'].values[0]}"
        )

    # Escalações 
    with st.container():
        st.subheader('Escalação dos Times')

        # Lineups da partida selecionada
        team_lineup = sb.lineups(match_id=match_id)

        # Usar duas colunas 
        lineup_col1, lineup_col2 = st.columns(2)

        # Escalação dos dois times
        with lineup_col1:
            team_name_1 = list(team_lineup.keys())[0]
            st.write(f'**{team_name_1}**')
            st.dataframe(team_lineup[team_name_1])

        with lineup_col2:
            team_name_2 = list(team_lineup.keys())[1]
            st.write(f'**{team_name_2}**')
            st.dataframe(team_lineup[team_name_2])

        # Lista de todos os jogadores
        all_players = []
        for team, lineup in team_lineup.items():
            all_players.extend(lineup['player_name'].tolist())

    # Seleção de Jogadores
    with st.container():
        player_name = st.sidebar.selectbox('Escolha o jogador para análise', all_players)
   



# 4 - Obter dados e exibir informações básicas
#     Use a biblioteca StatsBombPy para carregar dados de competições, temporadas, partidas e jogadores.
#     Mostre, em uma página do dashboard, as seguintes informações:
#         Nome da competição, temporada e partida selecionada.
#         Estatísticas básicas da partida (gols, chutes, passes, etc.).
#         Um DataFrame exibindo os eventos da partida, como passes, finalizações e desarmes.


    # Nome da Competição, Temporada e Partida Selecionada
    st.header(f"Competição: {competition_id}")
    st.subheader(f"Temporada: {season_id}")
    match_details = matches[matches['match_id'] == match_id].iloc[0]
    st.subheader(f"Partida Selecionada: {match_details['home_team']} vs {match_details['away_team']}")
    events = sb.events(match_id=match_id)
    total_goals = len(events[events['shot_outcome'] == 'Goal'])
    st.metric("Total de Gols", total_goals)    
    st.subheader(f'Escalações - Jogo {match_id}')

    # Eventos da Partida
    st.header('Eventos da Partida')

    # Carregar eventos 
    events = sb.events(match_id=match_id)

    # Eventos principais
    main_event_types = ['Pass', 'Shot', 'Duel', 'Foul', 'Clearance']
    filtered_events = events[events['type'].isin(main_event_types)]
    st.sidebar.header("Filtros de Visualização")
    max_events = st.sidebar.slider("Quantidade de Eventos para Visualizar", min_value=5, max_value=len(events), value=3)
    max_df = filtered_events.head(max_events)
    
    # DataFrame com os eventos filtrados
    st.write(f"Eventos principais da partida ({', '.join(main_event_types)})")
    st.dataframe(max_df[['minute', 'second', 'type', 'player', 'team', 'location', 'pass_outcome', 'shot_outcome']])
  
            
            
# 5 - Criar visualizações de dados
# Utilize a biblioteca mplsoccer para gerar um mapa de passes e mapa de chutes para uma partida específica. Garanta que o gráfico seja interativo, com legendas e informações que ajudem a interpretar os dados.
# Crie visualizações adicionais com Matplotlib e Seaborn para explorar relações entre as estatísticas de uma partida ou de um jogador (por exemplo, relação entre número de passes e gols).
# Utilize a biblioteca mplsoccer para novas visualizações de acordo com sua galeria (https://mplsoccer.readthedocs.io/en/latest/gallery/index.html)         
            
            
with abas[1]:
    # Gráficos de Dados
    st.header('Visualizações Gráficas dos Eventos')

    # Controle de Tempo 
    st.sidebar.subheader('Controle de Tempo')

    # Filtrar o tempo máximo 
    max_minute = int(filtered_events['minute'].max())

    # Slider de faixa de tempo 
    selected_minute_range = st.sidebar.slider(
        'Selecione o Intervalo de Minutos da Partida',
        0, max_minute, (0, max_minute)  
    )

    # Filtrar eventos dentro do intervalo
    filtered_events_in_range = filtered_events[
        (filtered_events['minute'] >= selected_minute_range[0]) &
        (filtered_events['minute'] <= selected_minute_range[1])
    ]

    # Limpar os gráficos a cada nova seleção de tempo
    plt.clf()

    # Mapa de Passes em Sequência
    st.header('Mapa de Passes em Sequência Temporal')

    # Filtrar passes
    passes = filtered_events_in_range[filtered_events_in_range['type'] == 'Pass']

    # Gráfico de campo
    pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#22312b', line_color='white')
    fig, ax = pitch.draw(figsize=(10, 7))

    # Passes dentro do intervalo selecionado
    for i, row in passes.iterrows():
        if isinstance(row['location'], list) and isinstance(row['pass_end_location'], list):
            pitch.arrows(row['location'][0], row['location'][1],
                        row['pass_end_location'][0], row['pass_end_location'][1],
                        ax=ax, width=2, headwidth=3, color='blue', alpha=0.6)
            ax.annotate(f"{row['player']} ({row['minute']}')", (row['location'][0], row['location'][1]), color='white', fontsize=8)

  
    st.pyplot(fig)

    # Mapa de Chutes
    st.header('Mapa de Chutes')

    # Filtrar chutes
    shots = filtered_events_in_range[filtered_events_in_range['type'] == 'Shot']

    # Gráfico de campo para chutes
    fig, ax = pitch.draw(figsize=(10, 7))

    # Chutes dentro do intervalo selecionado
    for i, row in shots.iterrows():
        if isinstance(row['location'], list):
            pitch.scatter(row['location'][0], row['location'][1], ax=ax, s=100, color='red', edgecolor='black', alpha=0.7)
            ax.annotate(f"{row['player']} ({row['minute']}')", (row['location'][0], row['location'][1]), color='white', fontsize=8)

 
    st.pyplot(fig)

    # Desarmes
    st.header('Mapa de Desarmes')

    # Filtrar desarmes 
    duels = filtered_events_in_range[filtered_events_in_range['type'] == 'Duel']

    # Gráfico de campo para desarmes
    fig, ax = pitch.draw(figsize=(10, 7))

    # Desarmes dentro do intervalo selecionado
    for i, row in duels.iterrows():
        if isinstance(row['location'], list):
            pitch.scatter(row['location'][0], row['location'][1], ax=ax, s=100, color='green', edgecolor='black', alpha=0.7)
            ax.annotate(f"{row['player']} ({row['minute']}')", (row['location'][0], row['location'][1]), color='white', fontsize=8)

    st.pyplot(fig)
    
    
    # Passes ao Longo do Tempo
    st.header('Distribuição de Passes por Minuto')

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(passes['minute'], bins=10, kde=False, ax=ax, color='blue')

    ax.set_title('Distribuição de Passes ao Longo do Tempo')
    ax.set_xlabel('Minuto da Partida')
    ax.set_ylabel('Número de Passes')

    
    st.pyplot(fig)

    
    # Eventos com localização em campo 
    x = passes['location'].apply(lambda loc: loc[0] if isinstance(loc, list) else np.nan)
    y = passes['location'].apply(lambda loc: loc[1] if isinstance(loc, list) else np.nan)

    # Campo
    pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')

    # Gráfico 
    fig, ax = pitch.draw(figsize=(10, 7))
    bin_statistic = pitch.bin_statistic(x, y, statistic='count', bins=(30, 30))
    heatmap = pitch.heatmap(bin_statistic, ax=ax, cmap='coolwarm', edgecolors='white')

    # Título
    ax.set_title('Mapa de Calor dos Passes')

  
    st.pyplot(fig)

    # Filtrar os dados
    duel_data = filtered_events[['duel_type', 'duel_outcome']].dropna()

    # Tipos de Duelos vs Resultado
    st.header('Distribuição de Duelos e seus Resultados')

    duel_type_outcome = duel_data.groupby(['duel_type', 'duel_outcome']).size().unstack(fill_value=0)

    # Gráfico de barras empilhadas
    fig, ax = plt.subplots(figsize=(10, 6))
    duel_type_outcome.plot(kind='bar', stacked=True, ax=ax, color=['#1f77b4', '#ff7f0e', '#2ca02c'])

    ax.set_title('Distribuição de Duelos por Tipo e Resultado')
    ax.set_xlabel('Tipo de Duelo')
    ax.set_ylabel('Quantidade')


    st.pyplot(fig)

    # Filtrar os dados 
    pass_data = filtered_events[filtered_events['pass_technique'].notna()]

    # Distribuição de Técnicas de Passe
    st.header('Distribuição de Técnicas de Passe')

    pass_technique_count = pass_data['pass_technique'].value_counts()

    fig, ax = plt.subplots(figsize=(8, 6))
    pass_technique_count.plot(kind='bar', ax=ax, color='green')

    ax.set_title('Distribuição das Técnicas de Passe')
    ax.set_xlabel('Técnica de Passe')
    ax.set_ylabel('Quantidade')

    # Exibir 
    st.pyplot(fig)


# 6 - Adicionar interatividade
# Adicione seletores de jogadores e botões de filtro que permitam ao usuário visualizar apenas eventos relacionados a um jogador específico.
# Inclua botões de download que permitam ao usuário baixar os dados filtrados da partida em formato CSV.
# Utilize barras de progresso e spinners para informar ao usuário que os dados estão sendo carregados ou processados.


with abas[0]:
    st.header('Análise de Eventos por Jogador')

    # Spinner
    with st.spinner('Carregando dados das partidas...'):
        time.sleep(2) 

# Filtrar eventos pelo jogador selecionado
    player_events = events[events['player'] == player_name]

    if not player_events.empty:
        progress_bar = st.progress(0)
        
        for perc_complete in range(100):
            time.sleep(0.01)
            progress_bar.progress(perc_complete + 1)

        # Eventos filtrados 
        st.subheader(f'Eventos de {player_name}')
        st.dataframe(player_events)

        # Download dos dados filtrados
        csv = player_events.to_csv(index=False)
        st.download_button("Baixar Dados Filtrados", csv, f"{player_name}_events.csv")

    else:
       
        st.warning(f'Nenhum evento registrado para o jogador {player_name} nesta partida.')



# 7 - Incluir métricas e indicadores
#     Exiba indicadores numéricos usando a função metric() do Streamlit para mostrar, por exemplo:
#         Total de gols da partida.
#         Quantidade de passes bem-sucedidos de um jogador.
#         Taxa de conversão de chutes em gol.
#     Personalize esses indicadores com cores que realcem os valores mais importantes.


with abas[1]:


    # Separar coordenadas
    events[['x', 'y']] = events['location'].apply(pd.Series)
    events[['pass_end_x', 'pass_end_y']] = events['pass_end_location'].apply(pd.Series)
    events[['carry_end_x', 'carry_end_y']] = events['carry_end_location'].apply(pd.Series)


    teams = events['team'].unique() 

    for team in teams:
        # Filtrar eventos para o time específico
        team_events = events[events['team'] == team]

        # Passes 
        f3rd_passes = events[
            (events.team == team) & 
            (events.type == "Pass") & 
            (events.x < 80) & 
            (events.pass_end_x > 80) & 
            (events.pass_outcome.isna())
        ]

        # Contagem de passes 
        f3rd_passes_count = f3rd_passes.groupby('player').size().reset_index()
        f3rd_passes_count.rename(columns={f3rd_passes_count.columns[1]: "Passes"}, inplace=True)

        # Conduções 
        f3rd_carries = events[
            (events.type == "Carry") & 
            (events.x < 80) & 
            (events.carry_end_x > 80) & 
            (events.team == team)
        ]

        # Contagem de conduções
        f3rd_carries_count = f3rd_carries.groupby('player').size().reset_index()
        f3rd_carries_count.rename(columns={f3rd_carries_count.columns[1]: "Carries"}, inplace=True)

        # DataFrames de passes e conduções
        progressions_df = pd.merge(f3rd_passes_count, f3rd_carries_count, how="outer", on="player")
        progressions_df = progressions_df.fillna(0)  # Preencher valores NaN com 0
        progressions_df['total'] = progressions_df['Passes'] + progressions_df['Carries']

        # Ordenar pela soma de passes 
        progressions_df.sort_values(by='total', ascending=False, inplace=True)

        pass_colour = '#e21017'
        carry_colour = 'blue'

        # Inverter a ordem para plotagem correta
        progressions_df.sort_values(by='total', ascending=True, inplace=True)
        barchart_df = progressions_df[["player", "Passes", "Carries"]]

        fig, ax = plt.subplots(figsize=(10,10))

        # Estilo e tamanho do gráfico
        sns.set(rc={'axes.facecolor':'white', 'figure.facecolor':'white'})
        sns.set_style("ticks")

        # Gráfico de barras 
        barchart_df.set_index('player').plot(
            kind='barh',
            stacked=True,
            color=[pass_colour, carry_colour],
            legend=True,
            ax=ax
        )

        # Rótulos e título
        ax.set_xlabel("Progressions ", fontsize=12, weight='semibold')
        ax.set_ylabel("Player", fontsize=12, weight='semibold')
        ax.set_title(f"{team}: Progressions ", fontsize=24, weight='bold')

        # Remover bordas 
        sns.despine(top=True, right=True, left=False, bottom=False)

      
        st.pyplot(fig)


# 8 - Criar formulários interativos
#     Desenvolva formulários simples que permitam ao usuário escolher, por exemplo, a quantidade de eventos a serem visualizados, o intervalo de tempo de uma partida ou a comparação entre dois jogadores.
#     Use elementos como caixas de texto, dropdowns, radio buttons e checkboxes para tornar a interação mais fluida.

with abas[2]:
 
    st.subheader("Comparação entre Jogadores")

    # Seletores para os jogadores
    player_1 = st.selectbox("Escolha o Primeiro Jogador", events['player'].unique())
    player_2 = st.selectbox("Escolha o Segundo Jogador", events['player'].unique(), index=1)

   
    player_1_data = events[events['player'] == player_1]
    player_2_data = events[events['player'] == player_2]

    # Função para contar tipos de eventos
    def get_player_stats(player_data):
        
        total_passes = len(player_data[player_data['type'] == 'Pass'])
        successful_passes = len(player_data[(player_data['type'] == 'Pass') & (player_data['pass_outcome'] == 'Complete')])
        total_shots = len(player_data[player_data['type'] == 'Shot'])
        goals = len(player_data[player_data['shot_outcome'] == 'Goal'])
        conversion_rate = (goals / total_shots) if total_shots > 0 else 0
        duels_won = len(player_data[(player_data['type'] == 'Duel') & (player_data['duel_outcome'] == 'Won')])
        
      
        return {
            'Total Passes': total_passes,
            'Passes Completos': successful_passes,
            'Total de Chutes': total_shots,
            'Gols': goals,
            'Taxa de Conversão de Chutes': f"{conversion_rate:.2%}",
            'Desarmes Vencidos': duels_won
        }

 
    player_1_stats = get_player_stats(player_1_data)
    player_2_stats = get_player_stats(player_2_data)

    # DataFrame comparativo
    comparison_df = pd.DataFrame({
        'Métricas': ['Total Passes', 'Passes Completos', 'Total de Chutes', 'Gols', 'Taxa de Conversão de Chutes', 'Desarmes Vencidos'],
        player_1: [player_1_stats['Total Passes'], player_1_stats['Passes Completos'], player_1_stats['Total de Chutes'],
                player_1_stats['Gols'], player_1_stats['Taxa de Conversão de Chutes'], player_1_stats['Desarmes Vencidos']],
        player_2: [player_2_stats['Total Passes'], player_2_stats['Passes Completos'], player_2_stats['Total de Chutes'],
                player_2_stats['Gols'], player_2_stats['Taxa de Conversão de Chutes'], player_2_stats['Desarmes Vencidos']]
    })

    # Exibir tabela comparativa
    st.write(f"Comparação de Eventos entre {player_1} e {player_2}:")
    st.table(comparison_df)



# 9 - Implementar funcionalidades avançadas
#     Utilize o Cache do Streamlit para otimizar o carregamento de dados, especialmente se estiver utilizando bases de dados grandes.
#     Armazene o estado da sessão do usuário utilizando Session State, garantindo que a interação do usuário não seja perdida quando ele navegar entre páginas.



# 10 - Publicar o projeto
#     Realize o deploy da aplicação utilizando o Streamlit Community Cloud. Verifique se o deploy foi bem-sucedido e que todas as funcionalidades estão funcionando conforme esperado.
#     Compartilhe o link da aplicação publicada e o repositório no GitHub.