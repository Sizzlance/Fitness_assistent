import streamlit as st


def show_upload_tabs():
    tab1, tab2, tab3, tab4 = st.tabs(["Анфас", "Профиль", "Спина", "Программа тренировок"])

    uploaded_files = {
        "front": None,
        "side": None,
        "back": None
    }

    with tab1:
        uploaded_files["front"] = st.file_uploader("Фото анфас", type=["jpg", "png", "jpeg"], key="front")
    with tab2:
        uploaded_files["side"] = st.file_uploader("Фото профиль", type=["jpg", "png", "jpeg"], key="side")
    with tab3:
        uploaded_files["back"] = st.file_uploader("Фото сзади", type=["jpg", "png", "jpeg"], key="back")

    return uploaded_files, tab4
