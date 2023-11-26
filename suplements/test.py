import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

# Define Page layout
st.set_page_config(page_title="Mikroklima-Visualisierung",
                   layout="centered",
                   initial_sidebar_state="collapsed")  # collapsed/expanded


class SessionState:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# Function to load language bundle
def load_language_bundle(locale):
    df = pd.read_csv(r"./i18n/text_bundle.csv")
    df = df.query(f"locale == '{locale}'")
    lang_dict = {df.key.to_list()[i]: df.value.to_list()[i] for i in range(len(df.key.to_list()))}
    return lang_dict


# Create or get session state
session_state = SessionState(selected_language="DE")
if hasattr(session_state, "lang_dict"):
    lang_dict = session_state.lang_dict
else:
    lang_dict = load_language_bundle(session_state.selected_language)
    session_state.lang_dict = lang_dict

# Inside the container, add the title and content
with st.container():
    columns_main = st.columns((3, 3, 0.5))
    with columns_main[2]:
        selected_language = st.selectbox(label="Language", options=["DE", "EN"],
                                         label_visibility="hidden", key="language_select")  # 🌐
        session_state.selected_language = selected_language

    st.markdown("<div class='fixed-header'/>", unsafe_allow_html=True)

# Import CSS style
with open('./css/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

option_menu_styles = {
    "container": {
        "width": "100%",
        "max-width": "initial",
        "background": "white",
        "border-radius": "0rem",
    },
    "nav-link": {
        "width": "95%",
        "color": "black",
        "font-size": "1.0rem",
        "border": "1px solid #DD0065",
        "border-radius": "1rem",
    },
    "nav-link-selected": {
        "background-color": "#DD0065",
        "color": "white",
        "font-size": "1.1rem",
        "border-radius": "1rem",
    },
}

# Load language bundle based on the selected language
lang_dict = load_language_bundle(session_state.selected_language)

selected_menu = option_menu(
    menu_title=None,
    options=[f"{lang_dict['option_menu_0']}", f"{lang_dict['option_menu_1']}",
             f"{lang_dict['option_menu_2']}", f"{lang_dict['option_menu_3']}",
             f"{lang_dict['option_menu_4']}"],
    icons=["house", "globe2", "map", "palette", "info-circle"],
    default_index=0,
    orientation="horizontal",
    styles=option_menu_styles,
)

# Scenerio 0
if selected_menu == f"{lang_dict['option_menu_0']}":
    st.write(f"page1")
elif selected_menu == f"{lang_dict['option_menu_1']}":
    st.write(f"page2")
elif selected_menu == f"{lang_dict['option_menu_3']}":
    st.write(f"page3")
