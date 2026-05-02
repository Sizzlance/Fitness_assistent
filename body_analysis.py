import streamlit as st
import numpy as np
from config import REFERENCE_POINTS
from mediapipe_config import mp_pose


def ellipse_circumference(width_px):
    """Оценка обхвата тела по ширине в пикселях"""
    a = width_px / 2
    b = (width_px * 0.6) / 2  # предполагаем глубину = 60% ширины
    circumference = np.pi * (3 * (a + b) - np.sqrt((3 * a + b) * (a + 3 * b)))
    return circumference


def calculate_height(landmarks, image_height):
    """Расчет роста в пикселях"""
    total_height = 0
    count = 0

    for top_point, bottom_point in REFERENCE_POINTS:
        y_top = landmarks.landmark[top_point].y * image_height
        y_bottom = landmarks.landmark[bottom_point].y * image_height
        total_height += abs(y_top - y_bottom)
        count += 1

    return total_height / count if count > 0 else 0


def calculate_body_metrics(landmarks, image_height, image_width):
    """Расчет антропометрических показателей"""
    height_px = calculate_height(landmarks, image_height)

    left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]

    shoulder_width = abs(left_shoulder.x - right_shoulder.x) * image_width
    shoulder_circumference = ellipse_circumference(shoulder_width)

    waist_y = left_hip.y - 0.15 * abs(left_shoulder.y - left_hip.y)
    waist_points = [
        (landmark.x, landmark.y)
        for landmark in landmarks.landmark
        if abs(landmark.y - waist_y) < 0.01
    ]
    waist_width = (max([pt[0] for pt in waist_points]) - min([pt[0] for pt in waist_points])) * image_width if len(
        waist_points) >= 2 else abs(left_hip.x - right_hip.x) * image_width
    waist_circumference = ellipse_circumference(waist_width)

    hip_y = left_hip.y + 0.07 * abs(left_shoulder.y - left_hip.y)
    hip_points = [
        (landmark.x, landmark.y)
        for landmark in landmarks.landmark
        if abs(landmark.y - hip_y) < 0.015
    ]
    hip_width = (max([pt[0] for pt in hip_points]) - min([pt[0] for pt in hip_points])) * image_width if len(
        hip_points) >= 2 else abs(left_hip.x - right_hip.x) * image_width
    hip_circumference = hip_width * 1.6
    back_width = abs(left_shoulder.x - right_shoulder.x) * image_width
    back_circumference = ellipse_circumference(back_width)

    return {
        "height_px": height_px,
        "shoulder_circumference": shoulder_circumference,
        "waist_circumference": waist_circumference,
        "hip_circumference": hip_circumference,
        "back_circumference": back_circumference
    }


def get_body_type(metrics, gender):
    """Определение типа фигуры"""
    whr = metrics['waist_circumference'] / metrics['hip_circumference']

    if gender == "Мужской":
        if whr > 0.9:
            return "Яблоко"
        elif metrics['hip_circumference'] > metrics['shoulder_circumference'] * 1.1:
            return "Груша"
        else:
            return "Прямоугольник"
    else:
        if whr > 0.85:
            return "Яблоко"
        elif metrics['hip_circumference'] > metrics['shoulder_circumference'] * 1.1:
            return "Груша"
        else:
            return "Песочные часы"


def estimate_body_fat(bmi, age, gender):
    """Оценка процента жира"""
    return (1.20 * bmi) + (0.23 * age) - (16.2 if gender == "Мужской" else 5.4)


def posture_analysis(results, real_height):
    """Анализ осанки"""
    st.subheader("🧍 Анализ осанки")
    warnings = []

    if "front" in results:
        front_data = results["front"]
        landmarks = front_data["pose_landmarks"]
        img_h, img_w = front_data["image"].size[::-1]

        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        shoulder_diff = abs(left_shoulder.y - right_shoulder.y) * img_h

        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
        hip_diff = abs(left_hip.y - right_hip.y) * img_h

        if shoulder_diff > 0.005 * img_h:
            warnings.append(f"🔴 Асимметрия плеч: разница {shoulder_diff:.1f} см ({shoulder_diff / img_h * 100:.1f}%)")
        if hip_diff > 0.02 * img_h:
            warnings.append(f"🔴 Перекос таза: разница {hip_diff:.1f} px")

    if "side" in results:
        side_data = results["side"]
        landmarks = side_data["pose_landmarks"]
        img_h, img_w = side_data["image"].size[::-1]

        ear = landmarks.landmark[mp_pose.PoseLandmark.LEFT_EAR]
        shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        head_forward = (ear.x - shoulder.x) * img_w

        if head_forward > 0.1 * img_w:
            warnings.append("🔴 Голова наклонена вперед (сутулость)")

    if "back" in results:
        back_data = results["back"]
        landmarks = back_data["pose_landmarks"]
        img_h, img_w = back_data["image"].size[::-1]

        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]

        shoulder_diff_px = abs(left_shoulder.y - right_shoulder.y) * img_h
        shoulder_diff_cm = shoulder_diff_px * (real_height / img_h)  # Конвертация в см

        angle = np.degrees(np.arctan2(
            right_shoulder.y - left_shoulder.y,
            right_shoulder.x - left_shoulder.x
        ))

        hip_diff_px = abs(left_hip.y - right_hip.y) * img_h

        if shoulder_diff_px > 0.003 * img_h:
            warnings.append(
                f"🔴 Асимметрия плеч: "
                f"разница {shoulder_diff_cm:.1f} см, "
                f"угол {abs(angle):.1f}°"
            )

        if hip_diff_px > 0.01 * img_h:
            warnings.append(f"🔴 Перекос таза: разница {hip_diff_px * (real_height / img_h):.1f} см")

    if warnings:
        for warning in warnings:
            st.warning(warning)
    else:
        st.success("✅ Осанка в норме по всем проверенным параметрам")

    with st.expander("🔍 Как улучшить осанку"):
        st.markdown("""
        - Упражнения для укрепления корпуса: планка, гиперэкстензия
        - Растяжка грудных мышц
        - Контроль положения головы при работе за компьютером
        - Использование ортопедического кресла
        """)
