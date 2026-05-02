import numpy as np
import streamlit as st
import cv2
from body_analysis import calculate_body_metrics
from mediapipe_config import mp_drawing
from config import mp_pose


def vertical_pixel_span(p1, p2, image_h):
    return abs(p1.y - p2.y) * image_h


def px_to_cm(value_px, ref_size_px=None, real_height_cm=None, a4_size_px=None):
    """Улучшенная конвертация пикселей в сантиметры"""
    if a4_size_px and a4_size_px[0] > 0:
        px_per_cm_width = a4_size_px[0] / 21.0
        px_per_cm_height = a4_size_px[1] / 29.7
        px_per_cm = (px_per_cm_width + px_per_cm_height) / 2
        return value_px / px_per_cm
    elif real_height_cm and ref_size_px and ref_size_px > 0:
        return (value_px / ref_size_px) * real_height_cm
    return value_px


def detect_a4_page(image):
    """Обнаружение листа А4 в руке с улучшенной обработкой для текстурированного фона"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    img_h, img_w = gray.shape
    blur_size = max(3, int(min(img_h, img_w) * 0.01))
    blur_size = blur_size if blur_size % 2 == 1 else blur_size + 1
    blurred = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)

    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    median_intensity = np.median(gray)
    lower_threshold = int(max(20, 0.5 * median_intensity))
    upper_threshold = int(min(200, 1.5 * median_intensity))
    edged = cv2.Canny(thresh, lower_threshold, upper_threshold)

    kernel = np.ones((3, 3), np.uint8)
    edged = cv2.dilate(edged, kernel, iterations=1)
    edged = cv2.erode(edged, kernel, iterations=1)

    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:20]

    a4_ratio = 297 / 210
    min_ratio, max_ratio = 1.2, 1.6
    min_area = 0.01 * img_h * img_w
    max_area = 0.5 * img_h * img_w

    expected_a4_width = img_w * 0.1
    max_a4_width = img_w * 0.2

    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w) / h
            area = w * h
            contour_area = cv2.contourArea(cnt)

            fill_ratio = contour_area / area if area > 0 else 0

            if w > max_a4_width:
                st.warning(
                    f"Обнаруженный лист A4 слишком широкий ({w} пикселей). Ожидаемая ширина: ~{expected_a4_width} пикселей.")
                continue

            if (min_ratio <= aspect_ratio <= max_ratio or
                1 / min_ratio >= aspect_ratio >= 1 / max_ratio) and \
                    min_area <= area <= max_area and \
                    fill_ratio > 0.8:

                mask = np.zeros(gray.shape, dtype=np.uint8)
                cnt_int = cnt.astype(np.int32)
                if cnt_int.shape[-1] != 2 or len(cnt_int.shape) != 3:
                    cnt_int = cnt_int.reshape(-1, 1, 2)

                cv2.drawContours(mask, [cnt_int], -1, 255, thickness=cv2.FILLED)
                mean_val = cv2.mean(gray, mask=mask)[0]

                if mean_val > median_intensity * 0.7:
                    roi = image[y:y + h, x:x + w]
                    mean_color = cv2.mean(roi, mask=mask[y:y + h, x:x + w])[:3]
                    if all(c > 120 for c in mean_color):
                        return w, h, approx
    return None


def process_image(image, pose, use_reference=False):
    """Обработка одного изображения"""
    image_np = np.array(image)
    image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    height, width = image_np.shape[:2]

    a4_size = detect_a4_page(image_np) if use_reference else None

    results = pose.process(image_rgb)

    if results.pose_landmarks:
        annotated_image = image_np.copy()
        mp_drawing.draw_landmarks(
            annotated_image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0)),
            mp_drawing.DrawingSpec(color=(255, 0, 0)))

        metrics = calculate_body_metrics(results.pose_landmarks, height, width)
        return {
            "image": image,
            "annotated": annotated_image,
            "metrics": metrics,
            "a4_size": a4_size[:2] if a4_size else None,
            "pose_landmarks": results.pose_landmarks,
            "detection_confidence": results.pose_landmarks.landmark[0].visibility
        }
    return None
