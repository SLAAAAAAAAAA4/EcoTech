import os
import time
import logging
import toml
import streamlit as st
import google.generativeai as genai
import plotly.express as px
from streamlit_option_menu import option_menu
import pandas as pd
import spacy
from wordcloud import WordCloud
from collections import Counter
from streamlit_autorefresh import st_autorefresh
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from streamlit_extras.switch_page_button import switch_page
from PIL import Image
import numpy as np

try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "pt_core_news_sm"])
    nlp = spacy.load("pt_core_news_sm")

# --- Agora você já pode usar o nlp normalmente ---
doc = nlp("Exemplo de texto em português")


# ====================== CONFIGURAÇÕES GERAIS ========================= #
st.set_page_config(
    page_title='EcoTech',
    page_icon='https://i.postimg.cc/SR0VrsJg/Favecon-removebg-preview.png',
    layout="wide"
)

# ====================== CHAVE API GEMINI ============================= #
# 1. LER OS SEGREDOS DO ST.SECRETS
SECRETS_FILE = os.path.join(".streamlit", "secrets.toml")

try:
    # Lê o arquivo TOML local
    with open(SECRETS_FILE, 'r', encoding='utf-8') as f:
        config = toml.load(f)

    # Pega as chaves
    API_KEY = config["gemini_api_key"]
    MODEL_NAME = config["modelo_gemini"]
    SYSTEM_INSTRUCTION = config["system_instruction"]

except FileNotFoundError:
    st.error(f"Erro: Arquivo de segredos não encontrado em '{SECRETS_FILE}'.")
    st.stop()

except KeyError as e:
    st.error(f"Erro: Chave {e} não encontrada em secrets.toml.")
    st.stop()


# ✅ FUNÇÃO CORRETA — sem Client(), que não existe
@st.cache_resource
def get_gemini_model():
    """
    Configura o Gemini usando google-generativeai
    e retorna o modelo já pronto para uso.
    """
    try:
        # Configura a API KEY
        genai.configure(api_key=API_KEY)

        # Cria o modelo Gemini correto
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=SYSTEM_INSTRUCTION
        )
        return model

    except Exception as e:
        st.error(f"Falha ao configurar o Gemini ('{MODEL_NAME}'): {e}")
        st.stop()


# ✅ Agora 'modelo' é o GenerativeModel correto
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

    st.header(f"{selected}", divider="blue")
    st.markdown("#### Nuvem de Palavras")
    logging.basicConfig(level=logging.DEBUG)

    st.markdown(
        """
        <style>
        div.block-container {
            padding-left: 2rem;
            padding-right: 2rem;
        }
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        img {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
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

    # ================================
    # 🔥 CARREGAMENTO SEGURO DO SPACY
    # ================================
    @st.cache_resource
    def load_spacy_pt():
        try:
            return spacy.load("pt_core_news_sm"), "pt_core_news_sm"
        except:
            try:
                return spacy.load("pt_core_news_md"), "pt_core_news_md"
            except:
                try:
                    return spacy.load("pt_core_news_lg"), "pt_core_news_lg"
                except:
                    from spacy.lang.pt import Portuguese
                    nlp_blank = Portuguese()
                    if "sentencizer" not in nlp_blank.pipe_names:
                        nlp_blank.add_pipe("sentencizer")
                    return nlp_blank, "blank_pt"

    nlp, MODEL_SPACY = load_spacy_pt()
    st.info(f"Modelo spaCy carregado: **{MODEL_SPACY}**")

    # ================================
    # 🔥 CARREGAR DADOS
    # ================================
    @st.cache_data(ttl=30)
    def load_data(csv_url):
        df = pd.read_csv(csv_url)
        if len(df.columns) > 1:
            original = df.columns[1]
            df.rename(columns={original: "percepcao"}, inplace=True)
            logging.debug(f"Coluna '{original}' renomeada para 'percepcao'.")
        return df

    csv_url = "https://docs.google.com/spreadsheets/d/1dsAaDSCpLYts8Y9P6Jbd62yLaHTjvUN_B3H8XBH-JbQ/export?format=csv&id=1dsAaDSCpLYts8Y9P6Jbd62yLaHTjvUN_B3H8XBH-JbQ&gid=1585034273"

    try:
        data = load_data(csv_url)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.stop()

    # ================================
    # 🔥 PROCESSAMENTO DE TEXTO
    # ================================
    def process_texts(texts):
        doc = nlp(" ".join(texts))
        tokens = []

        for token in doc:
            if not token.is_alpha:
                continue
            if getattr(token, "is_stop", False):
                continue

            lemma = token.lemma_.lower() if hasattr(token, "lemma_") else token.text.lower()

            if hasattr(token, "pos_") and token.pos_:
                if token.pos_ in ("VERB", "NOUN", "PROPN", "ADJ"):
                    tokens.append(lemma)
            else:
                if len(lemma) > 2:
                    tokens.append(lemma)

        return tokens

    exclude_words = [
        "ruim", "radiação", "cabos", "Poluição", "Acúmulo", "contaminavel",
        "Perigo", "sujeira", "Sistentabily", "Reversão", "Utópico",
        "Se o mundo comessase q descartar corretamente, o meio ambiente vai ter a oportunidade de se regenerar"
    ]

    tokens = []
    wordcloud_image = None
    freq_fig = None

    if "percepcao" in data.columns and not data["percepcao"].dropna().empty:
        texts = data["percepcao"].dropna().tolist()
        tokens = process_texts(texts)
        tokens = [t for t in tokens if t not in exclude_words]

        if tokens:
            # ================================
            # 🔥 NUVEM DE PALAVRAS
            # ================================
            def generate_wordcloud(tokens):
                freq = Counter(tokens)
                wc = WordCloud(
                    width=600,
                    height=600,
                    background_color="white",
                    colormap="viridis",
                    max_words=100
                )
                wc.generate_from_frequencies(freq)
                return wc.to_array()

            def create_frequency_data(tokens):
                freq = Counter(tokens)
                df_freq = pd.DataFrame(freq.items(), columns=["palavra", "frequencia"])
                return df_freq.sort_values(by="frequencia", ascending=False).head(10)

            # Seu dicionário de tokens
            tokens = {
                "pilha": 27,
                "celular": 16,
                "bateria": 16,
                "computador": 7,
                "pilhas": 7,
                "eletronicos": 4,
                "celulares": 4,
                "carregador": 3,
                "poluição": 3,
                "baterias": 3
            }

            def create_frequency_chart(tokens):
                # Criar DataFrame a partir do dicionário
                df_freq = pd.DataFrame({
                    "palavra": list(tokens.keys()),
                    "frequencia": list(tokens.values())
                })

                # Ordenar do maior para o menor
                df_freq = df_freq.sort_values(by="frequencia", ascending=False)

                # Cores verdes proporcionais à frequência
                df_freq["cor"] = df_freq["frequencia"].apply(
                    lambda x: f"rgb(0,{60 + int(195 * (x / df_freq['frequencia'].max()))},0)"
                )

                # Criar gráfico de barras
                fig = px.bar(
                    df_freq,
                    x="palavra",
                    y="frequencia",
                    text="frequencia",
                    labels={"palavra": "Percepção", "frequencia": "Frequência"},
                    color="cor",
                    color_discrete_map="identity"
                )

                fig.update_traces(texttemplate="%{y}", textposition="outside")
                
                # Ajustes de layout para Streamlit
                fig.update_layout(
                    xaxis_tickangle=-45,
                    margin=dict(t=40, b=40, l=20, r=20),
                    height=400,  # altura reduzida
                    width=700,   # largura ajustada
                    showlegend=False
                )

                return fig

            wordcloud_image = generate_wordcloud(tokens)
            freq_fig = create_frequency_chart(tokens)
        else:
            st.warning("Tokens processados estão vazios. Verifique os dados ou palavras excluídas.")
    else:
        st.warning("Coluna 'percepcao' não encontrada ou vazia.")

    # ================================
    # 🔥 EXIBIÇÃO
    # ================================
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='centered'>", unsafe_allow_html=True)
            st.markdown("###### :bust_in_silhouette: Opiniões — E-lixo")
            
            # Checagem segura da wordcloud
            if wordcloud_image is not None and isinstance(wordcloud_image, np.ndarray):
                img = Image.fromarray(wordcloud_image)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                st.image(img)  # sem use_container_width
            else:
                st.write("Sem nuvem de palavras disponível ou imagem inválida.")
            
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='centered'>", unsafe_allow_html=True)
            st.markdown("###### :bust_in_silhouette: Contagem de palavras")
            if freq_fig is not None:
                st.plotly_chart(freq_fig, use_container_width=True)  # Plotly continua funcionando
            else:
                st.write("Sem gráfico de frequência disponível.")
            st.markdown("</div>", unsafe_allow_html=True)


    # ================================
    # 🔥 DEPURAÇÃO
    # ================================
    st.markdown("---")
    with st.expander("Informações de Depuração"):
        st.write("##### Colunas do DataFrame:")
        st.write(data.columns.tolist())

        st.write("##### Primeiras 5 linhas:")
        st.dataframe(data.head())

        if tokens:
            st.write(f"Tokens extraídos: {len(tokens)}")
            st.write(tokens[:15])
        else:
            st.write("Nenhum token extraído.")

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
    
    TIMEOUT_MINUTES = 15
    TIMEOUT_SECONDS = TIMEOUT_MINUTES * 60

    # --- ESTADOS ---
    if "historico" not in st.session_state:
        st.session_state.historico = []  # lista de {"role":"user/model", "text":""}

    if "last_activity_time" not in st.session_state:
        st.session_state.last_activity_time = time.time()

    # --- TIMEOUT ---
    current_time = time.time()
    elapsed_time = current_time - st.session_state.last_activity_time

    if elapsed_time >= TIMEOUT_SECONDS:
        st.session_state.historico = []
        st.session_state.last_activity_time = current_time
        st.warning(f"Sessão expirada após {TIMEOUT_MINUTES} minutos. Conversa limpa.")
        st.rerun()

    # --- MODELO ---
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,  
        system_instruction=SYSTEM_INSTRUCTION
    )

    # --- EXIBIR HISTÓRICO ---
    for msg in st.session_state.historico:
        with st.chat_message("assistant" if msg["role"] == "model" else "user"):
            st.markdown(msg["text"])

    # --- INPUT ---
    prompt = st.chat_input("Envie sua pergunta sobre descarte eletrônico...")

    if prompt:
        st.session_state.last_activity_time = time.time()

        # registra user
        st.session_state.historico.append({"role": "user", "text": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # gera resposta com streaming
        with st.chat_message("assistant"):
            placeholder = st.empty()
            resposta = ""
            try:
                stream = model.generate_content(
                    prompt,
                    stream=True
                )

                for chunk in stream:
                    if chunk.text:
                        resposta += chunk.text
                        placeholder.markdown(resposta + "▌")

                placeholder.markdown(resposta)

                # registra modelo
                st.session_state.historico.append({"role": "model", "text": resposta})

            except Exception as e:
                st.error(f"Erro ao gerar resposta: {e}")

    # --- LIMPAR ---
    if st.button("🧹 Limpar conversa"):
        st.session_state.historico = []
        st.session_state.last_activity_time = time.time()
        st.rerun()