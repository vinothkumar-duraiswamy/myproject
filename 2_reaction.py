import os
import random
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, ImageClip, vfx
from PIL import Image, ImageDraw, ImageFont

# --- Input / Output directories ---
input_videos_folder = r"C:\Users\User\vinoth\myproject\downloads"
reaction_videos_folder = r"C:\Users\User\vinoth\myproject\reaction"
background_music_folder = r"C:\Users\User\vinoth\myproject\background"
output_folder = r"C:\Users\User\vinoth\myproject\output"

# --- Font settings ---
font = ImageFont.truetype("arialbd.ttf", 40)

# --- Target output resolution (Vertical 1080p for Shorts) ---
TARGET_W, TARGET_H = 1080, 1920

# --- Helper function: Fit video with blurred background ---
def make_fit_with_blur(clip, target_w, target_h):
    """
    Fits video into target size while keeping aspect ratio.
    Adds a blurred background (TikTok style) using OpenCV GaussianBlur.
    """
    # Foreground: scale to fit inside
    if clip.w / clip.h > target_w / target_h:
        fg = clip.resize(width=target_w)
    else:
        fg = clip.resize(height=target_h)

    # Background: stretched, then blurred with OpenCV
    def blur_frame(frame):
        return cv2.GaussianBlur(frame, (55, 55), 0)

    bg = clip.resize((target_w, target_h)).fl_image(blur_frame).volumex(0)  # mute background
    fg = fg.set_position("center")
    return CompositeVideoClip([bg, fg], size=(target_w, target_h))

# --- Get all videos and music files ---
video_files = [f for f in os.listdir(input_videos_folder) if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))]
reaction_files = [f for f in os.listdir(reaction_videos_folder) if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))]
music_files = [f for f in os.listdir(background_music_folder) if f.lower().endswith((".mp3", ".wav", ".aac"))]

if not video_files:
    print("⚠️ No video files found in", input_videos_folder)
    exit()
if not reaction_files:
    print("⚠️ No reaction videos found in", reaction_videos_folder)
    exit()
if not music_files:
    print("⚠️ No music files found in", background_music_folder)
    exit()

# --- Process each video ---
for idx, video_file in enumerate(video_files, start=1):
    video_path = os.path.join(input_videos_folder, video_file)
    reaction_path = os.path.join(reaction_videos_folder, random.choice(reaction_files))
    print(f"🎬 Processing: {video_file} + {os.path.basename(reaction_path)}")

    # Load main video
    main_clip = VideoFileClip(video_path)

    # --- Top (main) video with blurred background ---
    top_clip = make_fit_with_blur(main_clip, TARGET_W, TARGET_H // 2).set_position(("center", "top"))

    # --- Reaction video: LOOP first, then fit with blur ---
    raw_reaction = VideoFileClip(reaction_path)
    reaction_looped = raw_reaction.fx(vfx.loop, duration=main_clip.duration)
    reaction_final = make_fit_with_blur(reaction_looped, TARGET_W, TARGET_H // 2).set_position(("center", "bottom"))

    # --- Create "Subscribe & Like" text with white border ---
    txt = "SUBSCRIBE & Like"
    txt_img = Image.new("RGBA", (TARGET_W, 120), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_img)
    bbox = draw.textbbox((0, 0), txt, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    text_x = (TARGET_W - w) // 2
    text_y = (120 - h) // 2

    # Stroke (white border)
    for dx in [-2, -1, 0, 1, 2]:
        for dy in [-2, -1, 0, 1, 2]:
            if dx != 0 or dy != 0:
                draw.text((text_x + dx, text_y + dy), txt, font=font, fill="white")

    # Main red text
    draw.text((text_x, text_y), txt, font=font, fill="red")

    txt_path = "subscribe.png"
    txt_img.save(txt_path)

    subscribe_text = (
        ImageClip(txt_path, transparent=True)
        .set_duration(main_clip.duration)
        .set_position(("center", TARGET_H - 150))
        .fadein(1)
        .fadeout(1)
    )

    # --- Background music ---
    music_file = random.choice(music_files)
    music_path = os.path.join(background_music_folder, music_file)
    music = AudioFileClip(music_path).volumex(0.5)
    if music.duration < main_clip.duration:
        music = music.fx(vfx.loop, duration=main_clip.duration)
    else:
        music = music.set_duration(main_clip.duration)

    # --- Combine ---
    final = CompositeVideoClip([top_clip, reaction_final, subscribe_text], size=(TARGET_W, TARGET_H))
    final = final.set_audio(music).set_duration(main_clip.duration)

    # --- Export (High Quality YouTube Shorts 1080x1920) ---
    output_path = os.path.join(output_folder, f"output_{idx}_{os.path.splitext(video_file)[0]}_shorts.mp4")
    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        ffmpeg_params=[
            "-crf", "18",          # High quality
            "-pix_fmt", "yuv420p", # YouTube compatible
            "-movflags", "+faststart",
            "-b:a", "320k"         # Boost audio quality
        ],
        fps=main_clip.fps,
        threads=4
    )

    print(f"✅ Saved: {output_path}")

print("🎉 All videos processed successfully in 1080x1920 (Shorts format)!")
