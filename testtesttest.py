import cv2
import numpy as np
from rembg import remove

# --- Input & Output ---
input_video = r"C:\Users\User\vinoth\myproject\reaction\Video.mp4"
output_video = r"C:\Users\User\vinoth\myproject\reaction\Video_green.mp4"

# Open input video
cap = cv2.VideoCapture(input_video)

# Video info
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

# --- Background color (green) ---
green_bg = np.array([0, 255, 0], dtype=np.uint8)  # BGR

frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"🎬 Processing {frame_count} frames...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to RGBA with rembg (person isolated, transparent bg)
    result = remove(frame)

    # rembg returns RGBA, separate channels
    if result.shape[2] == 4:
        rgb, alpha = result[:, :, :3], result[:, :, 3]

        # Create green background
        bg = np.full_like(rgb, green_bg, dtype=np.uint8)

        # Blend person + green background using alpha mask
        alpha = alpha.astype(float) / 255.0
        alpha = np.expand_dims(alpha, axis=2)

        composite = (rgb * alpha + bg * (1 - alpha)).astype(np.uint8)
    else:
        composite = frame  # fallback

    out.write(composite)

cap.release()
out.release()
print(f"✅ Saved with green background: {output_video}")
