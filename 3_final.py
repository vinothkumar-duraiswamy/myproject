import os
import random
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip
from moviepy.audio.fx.all import audio_loop

# --- Input / Output directories ---
shorts_folder = r"C:\Users\User\vinoth\myproject\output"
background_music_folder = r"C:\Users\User\vinoth\myproject\background"
final_output = r"C:\Users\User\vinoth\myproject\final_long_video.mp4"

# --- Collect all short videos ---
short_files = [f for f in os.listdir(shorts_folder) if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))]

if not short_files:
    print("⚠️ No short videos found in", shorts_folder)
    exit()

short_files.sort()  # keep consistent order

# --- Load shorts and fit them into 1920x1080 with black bars ---
clips = []
for short in short_files:
    path = os.path.join(shorts_folder, short)
    print(f"📼 Adding: {short}")
    clip = VideoFileClip(path).without_audio()

    # Scale by height to fit into 1080
    clip = clip.resize(height=1080)

    # Create a black 1920x1080 background
    background = VideoFileClip(path).without_audio().resize((1920, 1080)).set_opacity(0).on_color(
        size=(1920, 1080), color=(0, 0, 0), pos=("center", "center")
    )

    # Place the vertical clip centered over black background
    clip = CompositeVideoClip([background, clip.set_position(("center", "center"))], size=(1920, 1080))

    clips.append(clip)

# Concatenate into one long video
final_video = concatenate_videoclips(clips, method="compose")

# --- Pick one random background music ---
music_files = [f for f in os.listdir(background_music_folder) if f.lower().endswith((".mp3", ".wav", ".aac"))]

if not music_files:
    print("⚠️ No music files found in", background_music_folder)
    exit()

music_file = random.choice(music_files)
music_path = os.path.join(background_music_folder, music_file)
print(f"🎵 Using background music: {music_file}")

# Load and adjust music
music = AudioFileClip(music_path).volumex(0.5)

# Loop music if it's shorter than video, or trim if longer
if music.duration < final_video.duration:
    music = audio_loop(music, duration=final_video.duration)
else:
    music = music.subclip(0, final_video.duration)

# Add audio to final video
final_video = final_video.set_audio(music)

# --- Export with high quality (1920x1080 for long video) ---
final_video.write_videofile(
    final_output,
    codec="libx264",
    audio_codec="aac",
    preset="medium",
    ffmpeg_params=[
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-b:a", "320k"
    ],
    fps=clips[0].fps,
    threads=4
)

print(f"✅ Final long video saved at: {final_output}")
