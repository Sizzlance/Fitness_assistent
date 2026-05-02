import streamlit as st
from PIL import Image
from body_analysis import get_body_type, mp_pose
from interface.sidebar import show_sidebar
from interface.upload_tab import show_upload_tabs
from interface.results_tab import show_results_tab
from interface.workout_tab import show_workout_tab
from utils import process_image

st.title("📏 Фитнес-ассистент: анализ тела и рекомендации")


def main():
    # Показать боковую панель и получить данные пользователя
    user_data = show_sidebar()

    # Показать вкладки загрузки
    uploaded_files, workout_tab = show_upload_tabs()

    # Основная обработка
    if any(uploaded_files.values()):
        with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.7) as pose:
            results = {}
            metrics = None

            for view, uploaded_file in uploaded_files.items():
                if uploaded_file:
                    image = Image.open(uploaded_file)
                    result = process_image(image, pose, user_data["use_reference"])
                    if result:
                        results[view] = result
                        if view == "front":
                            metrics = result["metrics"]
                        st.session_state[f'{view}_uploaded'] = True
                    else:
                        st.error(f"Не удалось проанализировать позу на фото {view}")

            if results:
                a4_sizes = [v["a4_size"] for v in results.values() if v["a4_size"]]
                ref_a4_size = a4_sizes[0] if a4_sizes else None

                if not ref_a4_size and user_data["use_reference"]:
                    st.warning("Лист А4 не обнаружен, используется расчет по росту")

                with st.form("user_data_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        real_height = st.number_input("Введите ваш реальный рост (см):",
                                                      min_value=140, max_value=230, value=175)
                    with col2:
                        weight = st.number_input("Введите ваш вес (кг):",
                                                 min_value=30, max_value=200, value=75)

                    submitted = st.form_submit_button("Обновить измерения")

                    if submitted or 'last_submit' not in st.session_state:
                        st.session_state.last_submit = True

                        if not metrics:
                            st.error("Для анализа требуется фото анфас")
                            st.stop()

                        bmi = weight / ((real_height / 100) ** 2)
                        conversion_factor = 21.0 / ref_a4_size[0] if ref_a4_size and ref_a4_size[
                            0] > 0 else real_height / \
                                        metrics[
                                            'height_px']

                        height_cm = metrics['height_px'] * conversion_factor
                        shoulder_cm = metrics['shoulder_circumference'] * conversion_factor
                        waist_cm = metrics['waist_circumference'] * conversion_factor
                        hip_cm = metrics['hip_circumference'] * conversion_factor

                        st.session_state.results = {
                            "height_cm": height_cm,
                            "shoulder_cm": shoulder_cm,
                            "waist_cm": waist_cm,
                            "hip_cm": hip_cm,
                            "bmi": bmi,
                            "ref_a4_size": ref_a4_size,
                            "metrics": {
                                "height_px": metrics["height_px"],
                                "shoulder_circumference": shoulder_cm,
                                "waist_circumference": waist_cm,
                                "hip_circumference": hip_cm
                            }
                        }

                if 'results' in st.session_state:
                    results_data = st.session_state.results
                    body_type = get_body_type(results_data['metrics'], user_data["gender"])

                    # Показать результаты анализа
                    show_results_tab(
                        results,
                        results_data['height_cm'],
                        user_data["gender"],
                        results_data["metrics"],
                        results_data["bmi"],
                        user_data["age"],
                        user_data["fitness_level"],
                        user_data["goal"]
                    )

                    # Показать вкладку тренировок
                    with workout_tab:
                        show_workout_tab(
                            results_data['bmi'],
                            user_data["age"],
                            user_data["gender"],
                            user_data["goal"],
                            body_type,
                            user_data["fitness_level"]
                        )


if __name__ == "__main__":
    main()
