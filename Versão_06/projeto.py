import os
import toml
import time
import logging
import streamlit as st
from google import genai
import plotly.express as px
from google.genai import types 
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import spacy
from wordcloud import WordCloud
from collections import Counter
from streamlit_autorefresh import st_autorefresh
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from streamlit_extras.switch_page_button import switch_page


# ====================== CONFIGURAÇÕES GERAIS ========================= #
st.set_page_config(
    page_title='EcoTech',
    page_icon='https://i.postimg.cc/SR0VrsJg/Favecon-removebg-preview.png',
    layout="wide"
)

# ====================== CHAVE API GEMINI ============================= #
# 1. LER OS SEGREDOS DO ST.SECRETS
SECRETS_FILE = os.path.join(".streamlit","secrets.toml")

try:
    # Tenta ler o arquivo TOML diretamente
    with open(SECRETS_FILE, 'r', encoding='utf-8') as f:
        config = toml.load(f)
        
    # --- Lendo as variáveis do dicionário 'config' ---
    API_KEY = config["gemini_api_key"]
    MODEL_NAME = config["modelo_gemini"]
    SYSTEM_INSTRUCTION = config["system_instruction"] 
    
except FileNotFoundError:
    st.error(f"Erro: Arquivo de segredos não encontrado em '{SECRETS_FILE}'.")
    st.info("Certifique-se de que você está executando 'streamlit run' na pasta raiz do projeto.")
    st.stop()
    
except KeyError as e:
    st.error(f"Erro: Chave de segredo {e} não encontrada no arquivo secrets.toml. Verifique a grafia.")
    st.stop()

@st.cache_resource
def get_gemini_model():
    """
    Configura o Gemini e retorna o objeto Client da nova biblioteca google-genai.
    """
    try:
        # A nova biblioteca 'google-genai' usa genai.Client() para inicializar a conexão
        client = genai.Client(api_key=API_KEY) 
        return client
    
    except Exception as e:
        st.error(f"Falha ao configurar o Gemini ou carregar o modelo '{MODEL_NAME}': {e}")
        st.stop()

# ⚠️ DEFINIÇÃO DA VARIÁVEL 'modelo' GLOBALMENTE ⚠️
# 'modelo' agora é o objeto Client
modelo = get_gemini_model()

# ==================================================================== #
# ======================== MENU LATERAL ============================== #
with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=["Informações", "Sobre e Entrevistas", "Opiniões", "Pontos de Coleta", "ChatBot"],
        icons=["none","none","none","none", "none"],
        default_index=0,
    )

# ==================================================================== #
# ======================= ABA INFORMAÇÕES ============================ #
if selected == "Informações":
    st.header(f"ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ{selected}", divider="green")
    
    st.markdown("#### Descarte de Lixo Eletrônico")
    
    st.markdown(
        "Descarte de Lixo Eletrônico, conhecido também como e-lixo ou REEE "
        "(Resíduo de Equipamentos Elétricos e Eletrônicos).\n\n"
        "Para descartar lixo eletrônico de forma correta, é necessário encontrar "
        "pontos de coleta especializados, como ecopontos e centros de reciclagem. "
        "Algumas empresas têm programas de logística reversa que permitem que os "
        "clientes devolvam os seus produtos usados para reciclagem.\n\n"
        "É muito importante se atentar de que as baterias de lítio "
        "(em celulares, notebooks etc.) permanecem nos equipamentos durante a coleta.\n\n"
        "**Malefícios do Descarte Incorreto:** O descarte inadequado causa danos "
        "à saúde e ao meio ambiente, contribuindo para a contaminação do solo e da água."
    )
    
    st.markdown(
        "### Tipos de Lixo Eletrônico:\n"
        "O lixo eletrônico é classificado em quatro (4) categorias diferentes:\n\n"
        "- **Linha Verde:** Incluindo dispositivos como computadores, laptops, celulares, tablets etc. "
        "Eles contêm metais preciosos e componentes que necessitam um cuidado especial para evitar impactos ambientais.\n"
        "- **Linha Branca:** Eletrodomésticos de grande porte, como geladeiras, freezers, máquinas de lavar e micro-ondas. "
        "Esses itens têm componentes recicláveis e precisam ser tratados adequadamente para promover a reciclagem eficiente.\n"
        "- **Linha Marrom:** Refere-se a equipamentos de áudio e vídeo, incluindo televisores, rádios, câmeras e aparelhos de som. "
        "Muitos desses dispositivos contêm substâncias tóxicas que requerem tratamento específico para evitar o impacto ambiental.\n"
        "- **Linha Azul:** Eletrodomésticos de uso geral, como ferramentas elétricas e eletrônicas, brinquedos, dispositivos médicos e de monitoramento."
    )
    # Link da imagem
    url_imagem = "https://vcx.solutions/wp-content/uploads/2021/12/4-categoria-de-lixos-eletronicos_Prancheta-1-1024x836.png"

    # Mostrar a imagem com largura média
    st.image(url_imagem, caption="Categorias de Lixo Eletrônico", width=500)

    st.markdown(
        "### O que descartar?\n"
        "- **Dispositivos:** Celulares, computadores (notebooks, desktops), tablets, monitores, impressoras, controles remotos, câmeras.\n"
        "- **Eletrodomésticos:** Geladeiras, fogões, micro-ondas, cafeteiras, torradeiras, ventiladores.\n"
        "- **Equipamentos de comunicações:** Fones de ouvido, cabos, carregadores.\n"
        "- **Outros:** Pilhas e baterias (de celular, de brinquedos, etc.), lâmpadas fluorescentes, CDs e DVDs."
    )
    
    st.markdown(
        "### Bateria de Lítio\n"
        "Bateria íon-lítio ou bateria de íon lítio é um tipo de bateria recarregável "
        "muito utilizada em equipamentos eletrônicos portáteis."
    )
    # Link da imagem
    url_imagem = "https://tse2.mm.bing.net/th/id/OIP.O6bVxbkVhabSKwwdyt4qxgHaKe?w=1131&h=1600&rs=1&pid=ImgDetMain&o=7&rm=3"

    # Mostrar a imagem com largura média
    st.image(url_imagem, caption="Descarte de Bateria de Lítio", width=300)
    st.markdown(
        "### Risco da bateria de Lítio\n"
        "O principal risco é o de incêndio, já que as baterias de íon-lítio combinam "
        "materiais de alta energia com eletrólitos, muitas vezes inflamáveis. "
        "Danos no separador dentro das baterias podem causar um curto-circuito interno "
        "com altas chances de fuga térmica."
        
    )
    
    st.markdown(
        "### Lâmpadas fluorescentes\n"
        "O descarte correto de lâmpadas fluorescentes é essencial para proteger o meio "
        "ambiente e nossa saúde, pois contêm mercúrio, um metal pesado tóxico. "
        "Elas não devem ser jogadas no lixo comum, mas sim encaminhadas para pontos de "
        "coleta específicos ou empresas especializadas em tratamento de resíduos."
    )
    # Link da imagem
    url_imagem = "https://tse2.mm.bing.net/th/id/OIP.MrZrjUgxYC8MNgEEDIKj5AHaHa?rs=1&pid=ImgDetMain&o=7&rm=3"

    # Mostrar a imagem com largura média
    st.image(url_imagem, caption="Descarte de lâmpadas Fluorescntes", width=400)
    st.markdown(
        "### Riscos das lâmpadas\n"
        "O descarte incorreto pode causar danos ambientais, como contaminação do solo e da água, "
        "além de riscos à saúde humana devido à toxicidade do mercúrio."
    )

    with st.expander("ℹ️ Créditos"):
            
        st.markdown("""    **Créditos do Projeto EcoTech**
        Projeto desenvolvido pela turma 3ºA da Escola Estadual Professor Alberto Conte, com contribuição coletiva
    
        Pesquisa
        - Samira
        - Ana Carolina
        
        **Entrevistas**
        - Ocativo (Entrevistador)
        - Matheus B (Operador de Câmera)
        - Emanuel (Editor)
        - Maria Clara
        - Evelyn Bea
        - (Todos desta lista contribuiram para as perguntas)
        
        **Ideias**
        - 3ºA
        
        **Desenvolvimento Técnico do Site**
        - Pedro Henrique  
        - Matheus Andrade 
        - Sania
        - Davi
        - Samuel Ribeiro
        - Possiveis manutenções e atualizações: Pedro Henrique
        """)

# ==================================================================== #
# =========================== ABA SOBRE ============================== #
elif selected == "Sobre e Entrevistas":
    st.header(f"ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ{selected}", divider="red")
    
    st.markdown("### EcoTech - O Início")

    st.markdown(
            "Nosso projeto começou em uma quarta-feira qualquer, quando recebemos um pedido "
            "para a criação de um site sobre o descarte consciente de lixo eletrônico. "
            "A proposta parecia simples no início, mas logo percebemos que seria um verdadeiro desafio.\n\n"
            "Decidimos seguir em frente, motivados pela ideia de contribuir com um tema tão relevante e atual. "
            "A partir desse momento, iniciou-se uma intensa discussão entre os membros da equipe — "
            "afinal, estávamos diante de um trabalho que exigiria organização, criatividade e comprometimento de todos.\n\n"
            "Nos primeiros dias, nosso foco foi definir o nome, a paleta de cores e o design inicial do site. "
            "Queríamos que o projeto transmitisse uma mensagem de responsabilidade ambiental, ao mesmo tempo em que fosse atrativo e fácil de navegar.\n\n"
            "Para aproveitar melhor as habilidades individuais, decidimos dividir o grupo em equipes específicas, "
            "responsáveis por diferentes áreas do desenvolvimento: divulgação, codificação, execução, pesquisa e desenvolvimento visual. "
            "Cada equipe recebeu prazos e metas, e as tarefas eram acompanhadas de perto durante as reuniões semanais, realizadas sempre às quartas-feiras.\n\n"
            "Esses encontros serviam não apenas para discutir o andamento do projeto, mas também para trocar ideias, revisar decisões e propor melhorias. "
            "Durante alguns meses, o processo foi marcado por muita pesquisa, debates e pequenos avanços. "
            "No entanto, com o tempo, nosso professor percebeu que o prazo inicial de um ano estava se tornando inviável, pois o progresso prático era lento e fragmentado.\n\n"
            "Foi então que recebemos uma nova orientação: simplificar o processo e migrar completamente para o Streamlit, uma ferramenta mais prática para o desenvolvimento do site. "
            "A decisão também trouxe uma mudança drástica na estrutura da equipe — as divisões por grupo foram eliminadas, e todos passaram a trabalhar de forma conjunta em todas as etapas do projeto. "
            "Além disso, o prazo foi reduzido para apenas quatro meses, o que exigiu uma reestruturação completa do cronograma e das prioridades.\n\n"
            "A partir desse ponto, deixamos de lado as discussões prolongadas sobre detalhes estéticos e passamos a agir de forma mais objetiva, priorizando entregas concretas e a funcionalidade do site. "
            "O ambiente de trabalho se tornou mais dinâmico e colaborativo, com cada integrante contribuindo diretamente para o avanço coletivo. "
            "Essa virada de abordagem não apenas acelerou o desenvolvimento, mas também fortaleceu o espírito de equipe — mostrando que, mesmo diante de imprevistos e prazos apertados, a união e a adaptação são fundamentais para transformar uma ideia inicial em um resultado real e funcional."
        )
        
    st.header("ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤEntrevistas - E-Lixo", divider="green")    

        # CSS para padronizar imagens quadradas
    st.markdown("""
            <style>
            .fixed-img {
                width: 250px;
                height: 250px;
                object-fit: cover;
                border-radius: 12px;
            }
            .caption {
                text-align: center;
                font-size: 15px;
                margin-top: 6px;
            }
            </style>
            """, unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align:center;">
            <iframe 
                width="700" 
                height="394"
                src="https://www.youtube.com/embed/NklcpkNMhSE?controls=0&modestbranding=1&rel=0&showinfo=0&fs=0"
                style="border-radius: 12px; border: none;"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
            </iframe>
        </div>
        """,
        unsafe_allow_html=True
    )

            # 5 colunas
    col1, col2, col3, col4, col5 = st.columns(5)

            # -------- COLUNA 1 (de onde a imagem estava saindo da grade)
    with col1:

                # PROCURA DE PESSOAS
                st.markdown(
                    "<img src='https://i.postimg.cc/bGMdpdt2/Whats-App-Image-2025-11-14-at-12-22-06-AM.jpg' class='fixed-img'>"
                    "<p class='caption'>A Procura de Pessoas</p>",
                    unsafe_allow_html=True
                )

                st.write("")

                # GRAVAÇÃO (esta era a que estava fora — agora corrigida)
                st.markdown(
                    "<img src='https://i.postimg.cc/cKj606n2/Whats-App-Image-2025-11-14-at-12-29-40-AM-2.jpg' class='fixed-img'>"
                    "<p class='caption'>Gravação</p>",
                    unsafe_allow_html=True
                )

            # -------- COLUNA 2
    with col2:

                st.markdown(
                    "<img src='https://i.postimg.cc/f3kkGYJf/Whats-App-Image-2025-11-14-at-12-23-15-AM.jpg' class='fixed-img'>"
                    "<p class='caption'>1° Entrevista</p>",
                    unsafe_allow_html=True
                )

                st.write("")

                # ENTREVISTA 1 – GRAVAÇÃO
                st.markdown(
                    "<img src='https://i.postimg.cc/R38q4qH3/Whats-App-Image-2025-11-14-at-12-22-57-AM.jpg' class='fixed-img'>"
                    "<p class='caption'>Entrevista 1 - Gravação</p>",
                    unsafe_allow_html=True
                )

            # -------- COLUNA 3
    with col3:
                st.markdown(
                    "<img src='https://i.postimg.cc/063rPrwt/Whats-App-Image-2025-11-14-at-12-29-39-AM.jpg' class='fixed-img'>"
                    "<p class='caption'>2° Entrevista</p>",
                    unsafe_allow_html=True
                )
                
                
                st.write("")

                # ENTREVISTA 2 – GRAVAÇÃO
                st.markdown(
                    "<img src='https://i.postimg.cc/fb69pRsN/Whats-App-Image-2025-11-13-at-10-10-31-AM.jpg' class='fixed-img'>"
                    "<p class='caption'>Entrevista 2 - Gravação</p>",
                    unsafe_allow_html=True
                )

            # -------- COLUNA 4
    with col4:
                st.markdown(
                    "<img src='https://i.postimg.cc/cKj606nP/Whats-App-Image-2025-11-14-at-12-29-40-AM.jpg' class='fixed-img'>"
                    "<p class='caption'>3° Entrevista</p>",
                    unsafe_allow_html=True
                )
                
                st.write("")

                # ENTREVISTA 3 – GRAVAÇÃO
                st.markdown(
                    "<img src='https://i.postimg.cc/vmt96zyr/Whats-App-Image-2025-11-14-at-12-21-37-AM.jpg' class='fixed-img'>"
                    "<p class='caption'>Entrevista 3 - Gravação</p>",
                    unsafe_allow_html=True
                )

            # -------- COLUNA 5
    with col5:
                st.markdown(
                    "<img src='https://i.postimg.cc/yJ5WsWZr/Whats-App-Image-2025-11-14-at-12-29-40-AM-1.jpg' class='fixed-img'>"
                    "<p class='caption'>4° Entrevista</p>",
                    unsafe_allow_html=True
                )
                st.write("")

                # ENTREVISTA 4 – GRAVAÇÃO
                st.markdown(
                    "<img src='https://i.postimg.cc/7ZjhYtWB/Whats-App-Image-2025-11-13-at-10-10-44-AM.jpg' class='fixed-img'>"
                    "<p class='caption'>Entrevista 4 - Gravação</p>",
                    unsafe_allow_html=True
                )


# ==================================================================== #
# =========================== ABA OPINIÕES =========================== #
elif selected == "Opiniões":
    st.header(f"ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ{selected}", divider="blue")
    st.markdown("#### Nuven de Palavras")
    logging.basicConfig(level=logging.DEBUG)
    
    st.markdown(
    """
    <style>
    /* Ajusta as margens do container principal */
    div.block-container {
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Oculta o menu principal, header e footer do Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Centraliza imagens e elementos gráficos */
    img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }

    /* Classe para centralizar conteúdo */
    .centered {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

    st_autorefresh(interval=5120000, key="data_refresh")

    try:
        # Carrega o modelo spaCy para o português
        nlp = spacy.load("pt_core_news_sm")
    except OSError:
        st.error("Modelo spaCy 'pt_core_news_sm' não encontrado. Por favor, execute 'python -m spacy download pt_core_news_sm' no seu terminal.")
        st.stop()

    @st.cache_data(ttl=30)
    def load_data(csv_url):
        df = pd.read_csv(csv_url)
        # FORÇA a renomeação da segunda coluna para um nome simples
        if len(df.columns) > 1:
            old_col_name = df.columns[1]
            df.rename(columns={old_col_name: "percepcao"}, inplace=True)
            logging.debug(f"Coluna '{old_col_name}' renomeada para 'percepcao'.")
        return df

    # ✅ URL corrigida para exportação CSV
    csv_url = "https://docs.google.com/spreadsheets/d/1dsAaDSCpLYts8Y9P6Jbd62yLaHTjvUN_B3H8XBH-JbQ/export?format=csv&id=1dsAaDSCpLYts8Y9P6Jbd62yLaHTjvUN_B3H8XBH-JbQ&gid=1585034273"

    try:
        data = load_data(csv_url)
        logging.debug("Dados carregados com sucesso.")
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        st.info("Verifique se o link 'csv_url' aponta para a **URL de exportação CSV** das respostas do Google Forms, não a URL do formulário.")
        st.stop()

    # Função para processar os textos da coluna
    def process_texts(texts):
        doc = nlp(" ".join(texts))
        
        # Inclui adjetivos ("ADJ") na análise
        tokens = [
            token.lemma_.lower() for token in doc
            if token.pos_ in ("VERB", "NOUN", "PROPN", "ADJ") and not token.is_stop and token.is_alpha
        ]
        logging.debug(f"Número de tokens extraídos: {len(tokens)}")
        return tokens

    # Lista de palavras irrelevantes adaptada para o tema
    exclude_words = ["ruim", "radiação", "cabos", "Poluição", "Acúmulo", "contaminavel", "Perigo", "sujeira","Sistentabily", "Reversão", "Utópico", "Se o mundo comessase q descartar corretamente, o meio ambiente vai ter a oportunidade de se regenerar"
    ]

    tokens = None
    wordcloud_image = None
    freq_fig = None

    # Bloco de processamento: busca a coluna de percepção pelo novo nome
    column_found = None
    if "percepcao" in data.columns:
        if not data["percepcao"].dropna().empty:
            column_found = "percepcao"

    if column_found:
        texts = data[column_found].dropna().tolist()
        logging.debug(f"Número de textos encontrados na coluna '{column_found}': {len(texts)}")
        if texts:
            tokens = process_texts(texts)
            # Filtra tokens irrelevantes
            tokens = [token for token in tokens if token not in exclude_words]
        else:
            st.write("A coluna com as percepções está vazia. Por favor, adicione mais respostas no formulário.")
    else:
        st.write("Não foi possível encontrar a coluna 'percepcao' no DataFrame. Verifique se a segunda coluna da sua planilha existe e não está vazia.")


    # Função para gerar a nuvem de palavras
    def generate_wordcloud(tokens):
        frequencies = Counter(tokens)
        wc = WordCloud(
            width=600,
            height=600,
            background_color="white",
            colormap="viridis",
            max_words=100
        )
        wc.generate_from_frequencies(frequencies)
        return wc.to_array()

    # Cria DataFrame de frequência
    def create_frequency_data(tokens):
        frequencies = Counter(tokens)
        freq_df = pd.DataFrame(
            frequencies.items(), columns=["palavra", "frequencia"]
        ).sort_values(by="frequencia", ascending=False)
        freq_df = freq_df.head(10)
        return freq_df

    # Gráfico de frequência com Plotly
    def create_frequency_chart(tokens):
        freq_df = create_frequency_data(tokens)
        fig = px.bar(
            freq_df,
            x="palavra",
            y="frequencia",
            text="frequencia",
            labels={"palavra": "Percepção", "frequencia": "Frequência"},
            color="frequencia",
            color_continuous_scale=[
    "#003300",  # verde MUITO escuro
    "#006600",  # verde escuro
    "#009933",  # verde médio vibrante
    "#33cc33",  # verde claro
    "#99ff99"   # verde bem claro
]
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, margin=dict(t=40, b=40))
        return fig

    # Geração e exibição
    if tokens and len(tokens) > 0:
        wordcloud_image = generate_wordcloud(tokens)
        freq_fig = create_frequency_chart(tokens)

    # Exibição centralizada
    with st.container(border=True):
        col1, col2 = st.columns(spec=2)
        
        with col1:
            st.markdown("<div class='centered'>", unsafe_allow_html=True)
            st.markdown("###### :bust_in_silhouette: Opinioes Descarte de E-lixo")
            if wordcloud_image is not None:
                st.image(wordcloud_image, use_container_width=True)
            else:
                st.write("Sem dados para gerar a nuvem de palavras.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='centered'>", unsafe_allow_html=True)
            st.markdown("###### :bust_in_silhouette: Contagem de respostas")
            if freq_fig is not None:
                st.plotly_chart(freq_fig, use_container_width=True)
            else:
                st.write("Sem dados para gerar o gráfico.")
            st.markdown("</div>", unsafe_allow_html=True)

    # --- Seção de depuração
    st.markdown("---")
    with st.expander("Informações de Depuração"):
        st.markdown("###### Colunas do DataFrame:")
        st.write(data.columns.tolist())
        
        st.markdown("###### Primeiras 5 linhas do DataFrame:")
        st.dataframe(data.head())

        st.markdown("###### Análise de Texto:")
        if column_found:
            st.write(f"Coluna encontrada: **'{column_found}'**")
            st.write(f"Número de respostas na coluna: **{len(texts)}**")
            if tokens:
                st.write(f"Número de tokens (palavras) extraídos: **{len(tokens)}**")
                st.write("Exemplos de tokens:")
                st.write(tokens[:10])
            else:
                st.write("Nenhum token foi extraído. A lista de `tokens` está vazia.")
        else:
            st.write("Não foi possível encontrar a coluna de percepções. Verifique a seção 'Primeiras 5 linhas' para confirmar o nome da segunda coluna.")


# =================================================================== #
# ======================== Pontos de Coleta ========================= #
elif selected == "Pontos de Coleta":
    st.header(f"ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ{selected}", divider="green")
    st.markdown("Pontos de Coleta do Brasil")

    st.title("♻️ Pontos de Coleta de Lixo Eletrônico no Brasil")

    st.markdown("""
    Este mapa mostra pontos de coleta de lixo eletrônico em diferentes regiões do Brasil.  
    Você pode ampliar, arrastar e visualizar todos os locais cadastrados.
    """)

    # 🔹 Exemplo com alguns pontos reais — substitua/adicione conforme precisar
    data = {
        "nome": [
                "SENAI",
                "Droga Raia 1",
                "KLR Comercial",
                "Sam'S Club - Santo Amaro",
                "C&A - Shopping Boavista",
                "RAIA / DROGASIL - Vila Cruzeiro",
                "Raia - Jardim Santo Amaro",
                "RAIA / DROGASIL - Santo Amaro",
                "Assaí Atacadista",
                "Parque Burle Marx",
                "Pão De Açúcar - Vila Sofia",
                "RAIA / DROGASIL - Chácara Santo Antônio (Zona Sul)",
                "Senac Santo Amaro",
                "Raia - Santo Amaro",
                "Carrefour - Spp - Pinheiros",
                "Carrefour - Spg - Giovani Gronchi",
                "Pão De Açúcar - Panamby",
                "Raia - Chácara Santo Antônio (Zona Sul)",
                "Droga Raia 2",
                "Droga Raia 3",
                "Raia - Vila Andrade",
                "Raia - Santo Amaro",
                "Atacadão Santo Amaro",
                "C&A Shopping Jardim Sul",
                "Pão De Açúcar - Borba Gato",
                "Vivo- Shopping SP Market",
                "Droga Raia 4",
                "Droga Raia 5",
                "RAIA / DROGASIL - 1",
                "RAIA / DROGASIL - 2",
                "C&A - Shopping Morumbi",
                "Droga Raia 6",
                "Assaí - Nações Unidas",
                "Assaí - Interlagos",
                "Raia - Jardim Londrina",
                "RAIA / DROGASIL - Jardim das Acácias",
                "Raia - Jardim Petrópolis",
                "Droga Raia 7"

                                                            
        ],
        "latitude": [
                -23.652254,
                -23.651935,
                -23.678624,
                -23.660990,
                -23.654716,
                -23.638702,
                -23.649145,
                -23.644094,
                -23.647029,
                -23.633298,
                -23.655671,
                -23.631401,
                -23.670898,
                -23.653114,
                -23.629325,
                -23.641981,
                -23.633971,
                -23.636550,
                -23.633270,
                -23.627236,
                -23.633477,
                -23.629175,
                -23.668748,
                -23.631175,
                -23.630455,
                -23.679594,
                -23.677809,
                -23.630984,
                -23.662978,
                -23.622684,
                -23.622772,
                -23.623087,
                -23.677859,
                -23.662512,
                -23.625727,
                -23.622064,
                -23.633093,
                -23.617437




        ],
        "longitude": [
                -46.712653,
                -46.707097,
                -46.698675,
                -46.709342,
                -46.700985,
                -46.711948,
                -46.698876,
                -46.701105,
                -46.729072,
                -46.722187,
                -46.691897,
                -46.710498,
                -46.699282,
                -46.689223,
                -46.711517,
                -46.734659,
                -46.728947,
                -46.693645,
                -46.730673,
                -46.716777,
                -46.735245,
                -46.695190,
                -46.736683,
                -46.735928,
                -46.690856,
                -46.699739,
                -46.698803,
                -46.735952,
                -46.681876,
                -46.698564,
                -46.698878,
                -46.698878,
                -46.695300,
                -46.680043,
                -46.736358,
                -46.699050,
                -46.679999,
                -46.705690

        ]
    }

    df = pd.DataFrame(data)

    # 🔹 Mostra o DataFrame na tela (opcional)
    with st.expander("📄 Ver tabela de pontos"):
        st.dataframe(df)

    # 🔹 Mapa com st.map()
    st.map(df, latitude="latitude", longitude="longitude", size=120, color="#32CD32")

    st.success(f"Total de pontos de coleta exibidos: {len(df)}")

# ==================================================================== #
# =========================== ABA CHATBOT ============================ #

elif selected == "ChatBot":
    chatbot_name = "EcoBot"
    st.header(f"ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ🤖 EcoBot", divider="green")
    st.markdown("Fale com nosso assistente virtual especializado **apenas sobre descarte eletrônico e reciclagem tecnológica.**")
    
    # --- CONSTANTES DE TEMPO ---
    TIMEOUT_MINUTES = 15
    TIMEOUT_SECONDS = TIMEOUT_MINUTES * 60 
    
    # --- 1. INICIALIZAÇÃO DE TODAS AS VARIÁVEIS DE ESTADO ---
    
    if 'historico' not in st.session_state:
        st.session_state.historico = []
    
    if 'chat_initialized' not in st.session_state:
        st.session_state.chat_initialized = False

    # Inicializa 'last_activity_time'
    if 'last_activity_time' not in st.session_state:
        st.session_state.last_activity_time = time.time()


    # --- 2. GESTÃO DE TEMPO E LIMPEZA AUTOMÁTICA (INVISÍVEL) ---
    
    current_time = time.time()
    
    elapsed_time = current_time - st.session_state.last_activity_time
    time_remaining = max(0, TIMEOUT_SECONDS - elapsed_time)

    # Verifica se o tempo limite foi atingido (Limpeza)
    if time_remaining == 0:
        # AQUI O HISTÓRICO É LIMPO
        st.session_state.historico = []
        st.session_state.chat_initialized = False 
        st.session_state.last_activity_time = current_time # Reseta o timer para o momento da limpeza
        st.warning(f"Sessão expirada após {TIMEOUT_MINUTES} minutos de inatividade. A conversa foi limpa.")
        st.rerun() 
    
    # --- 3. INICIALIZAÇÃO DO CHAT (Injetando o System Instruction) ---

    # 3.1. Cria o objeto de configuração com a instrução de sistema
    # Este é o caminho canônico atual: GenerateContentConfig.
    chat_config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION
    )

    # Se o histórico não existe ou o chat não foi inicializado, criamos a sessão
    if not st.session_state.chat_initialized:
        
        try:
            # 3.2. Cria o chat passando o objeto de configuração no argumento 'config'
            chat = modelo.chats.create(
                model=MODEL_NAME, 
                config=chat_config, # Passa a instrução aqui
                history=[]
            )
            # O histórico real inicia vazio, mas a instrução já está aplicada
            st.session_state.historico = chat.get_history()
            st.session_state.chat_initialized = True 
            
        except Exception as e:
            st.error(f"Erro ao iniciar a sessão de chat: {e}")
            st.stop()
    else:
        # Se já inicializado, apenas recria o objeto chat com o histórico existente
        try:
            # Ao recriar, re-incluímos o objeto de configuração
            chat = modelo.chats.create(
                model=MODEL_NAME, 
                config=chat_config, # Re-inclui a instrução
                history=st.session_state.historico
            )
        except Exception as e:
            st.error(f"Erro ao recriar a sessão de chat: {e}")
            st.stop()


    # --- 4. MOSTRA HISTÓRICO ---
    
    historico_completo = chat.get_history()
    historico_visivel = historico_completo 

    
    for mensagem in historico_visivel:
        # Ignora a mensagem se ela não tiver conteúdo de texto
        if not hasattr(mensagem.parts[0], 'text'):
            continue
            
        # Ajusta o role para a exibição no Streamlit
        role = 'assistant' if mensagem.role == 'model' else mensagem.role
        with st.chat_message(role):
            st.markdown(mensagem.parts[0].text)


    # --- 5. CAMPO DE ENTRADA E GERAÇÃO DE RESPOSTA ---
    
    prompt = st.chat_input("Envie sua pergunta sobre descarte eletrônico...")
    
    if prompt:
        # ATUALIZA O TEMPO DE ATIVIDADE APENAS NA INTERAÇÃO
        st.session_state.last_activity_time = time.time()
        
        with st.chat_message("user"):
            st.markdown(f"{prompt}")

        with st.chat_message("assistant"):
            msg_placeholder = st.empty()
            msg_placeholder.markdown("Pensando...")
            time.sleep(0.5)
            msg_placeholder.markdown("Gerando resposta...")
            time.sleep(0.2)
            
            resposta = ""
            try:
                # Usa o método correto para streaming
                for chunk in chat.send_message_stream(prompt):
                    if chunk.text:
                        resposta += chunk.text
                        msg_placeholder.markdown(resposta + "▌")

                msg_placeholder.markdown(resposta)
                
                # Atualiza o histórico de sessão com a nova conversa
                st.session_state.historico = chat.get_history()
                
            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar a resposta: {e}")

    # --- 6. BOTÃO DE LIMPEZA MANUAL ---
    if st.button("🧹 Limpar conversa"):
        # Limpa o histórico completamente, forçando a re-inicialização do chat na próxima vez.
        st.session_state.historico = [] 
        st.session_state.chat_initialized = False 
        st.session_state.last_activity_time = time.time() 
        st.rerun()
