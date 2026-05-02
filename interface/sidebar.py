import streamlit as st


def show_sidebar():
    st.sidebar.header("Персональные данные")
    age = st.sidebar.number_input("Возраст", min_value=12, max_value=80, value=25)
    gender = st.sidebar.selectbox("Пол", ["Мужской", "Женский"])
    goal = st.sidebar.selectbox("Цель", ["Похудение", "Набор массы", "Поддержание формы"])
    fitness_level = st.sidebar.selectbox("Уровень подготовки", ["Начинающий", "Средний", "Продвинутый"])
    use_reference = st.sidebar.checkbox("Использовать лист А4 для точности", value=True)

    st.sidebar.markdown("""
    **Инструкция по съемке:**
    1. Расположите лист А4 на уровне груди
    2. Встаньте в 1-1.5 метрах от камеры
    3. Сделайте минимум 2 фото: анфас и профиль
    4. Убедитесь, что все тело в кадре
    """)

    return {
        "age": age,
        "gender": gender,
        "goal": goal,
        "fitness_level": fitness_level,
        "use_reference": use_reference
    }
