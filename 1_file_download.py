import yt_dlp
import pandas as pd
import os

# Path to your Excel file (update with actual file name)
excel_file = r"C:\Users\User\vinoth\myproject\urls.xlsx"

# Read the Excel file - assuming URLs are in the first column
df = pd.read_excel(excel_file)

# Extract URL column (change column name if needed, e.g., 'URL')
urls = df.iloc[:, 0].dropna().tolist()

# Output folder
output_folder = r"C:\Users\User\vinoth\myproject\downloads"

# Loop through each URL and download
for i, url in enumerate(urls, start=1):
    outtmpl = os.path.join(output_folder, f"video_{i}.%(ext)s")

    ydl_opts = {
        "outtmpl": outtmpl,  # unique filename
        "format": "mp4",  # best video+audio
    }

    print(f"Downloading {url} as video_{i}.mp4 ...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

print("All downloads complete!")
