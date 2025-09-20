import os
import random
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont

# --- Input / Output directories ---
input_videos_folder = r"C:\Users\User\vinoth\myproject\downloads"
background_music_folder = r"C:\Users\User\vinoth\myproject\background"
output_folder = r"C:\Users\User\vinoth\myproject\output"

# --- Font settings ---
font = ImageFont.truetype("arialbd.ttf", 30)  # Bold Arial font

# --- Get all videos and music files ---
video_files = [f for f in os.listdir(input_videos_folder) if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))]
music_files = [f for f in os.listdir(background_music_folder) if f.lower().endswith((".mp3", ".wav", ".aac"))]

if not video_files:
    print("⚠️ No video files found in", input_videos_folder)
    exit()
if not music_files:
    print("⚠️ No music files found in", background_music_folder)
    exit()

# --- Process each video ---
for idx, video_file in enumerate(video_files, start=1):
    video_path = os.path.join(input_videos_folder, video_file)
    print(f"🎬 Processing: {video_file}")

    # Load video
    clip = VideoFileClip(video_path)

    # Step 1: Crop bottom (remove 50px)
    cropped_clip = clip.crop(x1=0, y1=0, x2=clip.w, y2=clip.h - 50)

    # Step 2: Create "Subscribe" text image with Pillow
    txt = "SUBSCRIBE & Like"
    txt_img = Image.new("RGBA", (cropped_clip.w, 120), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_img)

    bbox = draw.textbbox((0, 0), txt, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((cropped_clip.w - w) / 2, (120 - h) / 2), txt, font=font, fill="red")

    txt_path = "subscribe.png"
    txt_img.save(txt_path)

    # Step 3: Load text as ImageClip
    subscribe_text = (
        ImageClip(txt_path, transparent=True)
        .set_duration(cropped_clip.duration)
        .set_position(("center", "bottom"))
        .fadein(1)
        .fadeout(1)
    )

    # Step 4: Remove original audio
    silent_clip = cropped_clip.without_audio()

    # Step 5: Pick a random background music
    music_file = random.choice(music_files)
    music_path = os.path.join(background_music_folder, music_file)
    music = AudioFileClip(music_path).volumex(0.5)
    music = music.set_duration(silent_clip.duration)

    # Combine video + text + new audio
    final = CompositeVideoClip([silent_clip, subscribe_text])
    final = final.set_audio(music)

    # --- Export with better quality ---
    output_path = os.path.join(output_folder, f"output_{idx}_{os.path.splitext(video_file)[0]}.mp4")
    final.write_videofile(
        output_path,
        codec="libx264",      # H.264 codec for compatibility
        audio_codec="aac",    # AAC audio
        bitrate="8000k",      # higher bitrate = better quality (adjust if needed)
        preset="slow",        # better compression efficiency
        fps=clip.fps,         # keep original FPS
        threads=4             # speed up encoding
    )

    print(f"✅ Saved: {output_path}")

print("🎉 All videos processed successfully!")
