import streamlit as st
from workout_planner import generate_detailed_workout_plan
from datetime import datetime

def show_workout_tab(bmi, age, gender, goal, body_type, fitness_level):
    detailed_plan = generate_detailed_workout_plan(
        bmi, age, gender, goal, body_type, fitness_level
    )

    st.header("💪 Персональная программа тренировок")
    st.subheader(detailed_plan["description"])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏋️‍♂️ Тренировки")
        for item in detailed_plan["workouts"]:
            st.markdown(f"- {item}")

        st.markdown("### 📅 Расписание")
        for day, workout in detailed_plan["schedule"].items():
            st.markdown(f"- **{day}**: {workout}")

    with col2:
        st.markdown("### 🍎 Питание")
        st.markdown(detailed_plan["nutrition"])

        st.markdown("### 🔍 Советы")
        for tip in detailed_plan["tips"]:
            st.markdown(f"- {tip}")

        # Демонстрация упражнений
        if st.checkbox("Показать демонстрацию упражнений"):
            exercise = st.selectbox("Выберите упражнение", [
                "Приседания",
                "Отжимания",
                "Планка",
                "Становая тяга",
                "Жим лежа"
            ])

            if exercise == "Приседания":
                st.video("https://www.youtube.com/watch?v=bEv6CCg2BC8&list=PLp4G6oBUcv8yGQifkb4p_ZOoACPnYslx9&index=7")
                st.markdown("**Техника выполнения:**")
                st.markdown("- Спина прямая, грудь вперед")
                st.markdown("- Колени не выходят за носки")
                st.markdown("- Опускайтесь до параллели с полом")

            elif exercise == "Отжимания":
                st.video("https://www.youtube.com/watch?v=IODxDxX7oi4")
                st.markdown("**Техника выполнения:**")
                st.markdown("- Тело образует прямую линию")
                st.markdown("- Локти под углом 45 градусов")
                st.markdown("- Опускайтесь до угла 90 градусов в локтях")

            elif exercise == "Планка":
                st.video("https://www.youtube.com/watch?v=1G0y8D5rFDc&list=PLp4G6oBUcv8yGQifkb4p_ZOoACPnYslx9&index=23")
                st.markdown("**Техника выполнения:**")
                st.markdown("- Тело в прямой линии, как доска")
                st.markdown("- Локти под плечами, предплечья на полу")
                st.markdown("- Напрягите пресс, не прогибайтесь в пояснице")

            elif exercise == "Жим лежа":
                st.video("https://www.youtube.com/watch?v=vcBig73ojpE&list=PLp4G6oBUcv8yGQifkb4p_ZOoACPnYslx9")
                st.markdown("**Техника выполнения:**")
                st.markdown("- Лопатки сведены, спина слегка прогнута")
                st.markdown("- Штанга опускается до середины груди")
                st.markdown("- Локти под углом 45 градусов к корпусу")

            elif exercise == "Становая тяга":
                st.video("https://www.youtube.com/watch?v=VL5Ab0T07e4&list=PLp4G6oBUcv8yGQifkb4p_ZOoACPnYslx9&index=12")
                st.markdown("**Техника выполнения:**")
                st.markdown("- Спина прямая, грудь приподнята")
                st.markdown("- Штанга движется близко к ногам")
                st.markdown("- Бедра и колени разгибаются одновременно")

    # Трекер прогресса
    st.markdown("### 📈 Трекер прогресса")
    if 'completed_workouts' not in st.session_state:
        st.session_state.completed_workouts = 0

    workout_done = st.checkbox("Тренировка выполнена сегодня")
    today = str(datetime.today().date())
    if workout_done and ('last_workout_day' not in st.session_state or st.session_state.last_workout_day != today):
        st.session_state.completed_workouts += 1
        st.session_state.last_workout_day = today
        st.balloons()

    st.metric("Выполнено тренировок", st.session_state.completed_workouts)
    if 'last_workout_day' in st.session_state:
        st.write(f"Последняя тренировка: {st.session_state.last_workout_day}")

    if st.button("Сбросить прогресс"):
        st.session_state.completed_workouts = 0
        st.session_state.last_workout_day = None
        st.success("Прогресс сброшен!")