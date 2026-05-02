import streamlit as st
from body_analysis import posture_analysis, estimate_body_fat, get_body_type


def show_results_tab(results, real_height, gender, metrics, bmi, age, fitness_level, goal):
    st.subheader("📊 Результаты анализа")
    cols = st.columns(len(results))
    for idx, (view, data) in enumerate(results.items()):
        with cols[idx]:
            st.image(data["annotated"], caption=f"Анализ: {view}", use_container_width=True)
            if data.get("detection_confidence"):
                st.progress(data["detection_confidence"],
                            text=f"Точность: {data['detection_confidence'] * 100:.1f}%")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Рост", f"{real_height:.1f} см")
        st.metric("ИМТ", f"{bmi:.1f}",
                  "Норма" if 18.5 <= bmi < 25 else "Внимание!")
    with col2:
        body_fat = estimate_body_fat(bmi, age, gender)
        st.metric("% жира", f"{body_fat:.1f}%")
        st.metric("Тип фигуры", get_body_type(metrics, gender))
    with col3:
        st.metric("Обхват плеч", f"{metrics['shoulder_circumference']:.1f} см")
        st.metric("Обхват бедер", f"{metrics['hip_circumference']:.1f} см")

    posture_analysis(results, real_height)
