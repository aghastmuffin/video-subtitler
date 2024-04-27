from moviepy.editor import *
from moviepy.video.compositing.concatenate import concatenate_videoclips

# Load the video
video = VideoFileClip("pvideo.mp4")

# Define the text and its timings
text_clips = []

with open("timestamped.txt", "r") as file:
    f = file.read()
    lines = f.split("\n")
    for line in lines:
        print(line)
        lsplit = line.split(",")
        word = str(lsplit[0])
        stime = float(lsplit[1])
        etime = float(lsplit[2])
        text_clips.append({"text": word, "start": stime, "end": etime})

# Function to generate text clip
def generate_text_clip(text, duration):
    #return TextClip(text, fontsize=50, color='white', bg_color='black').set_duration(duration)
    return TextClip(text, fontsize=50, color='grey', font="8514OEM").set_duration(duration)

# Add text clips to the video
clips = []
last_end = 0

# Group the words into chunks of 4
for i in range(0, len(text_clips) - 3, 4):
    clip1 = text_clips[i]
    clip2 = text_clips[i + 1]
    clip3 = text_clips[i + 2]
    clip4 = text_clips[i + 3]

    # Combine the words and timings
    combined_text = " ".join([clip1["text"], clip2["text"], clip3["text"], clip4["text"]])
    combined_start = clip1["start"]
    combined_end = clip4["end"]

    # Cut the video into a small clip
    video_clip = video.subclip(last_end, combined_end)
    last_end = combined_end

    # Generate the text clip
    text_clip = generate_text_clip(combined_text, combined_end - combined_start)
    text_clip = text_clip.set_start(0).set_position('center')

    # Add the text to the video clip
    video_clip_with_text = CompositeVideoClip([video_clip, text_clip])

    clips.append(video_clip_with_text)

# Concatenate the clips back together
video_with_text = concatenate_videoclips(clips)

# Write the video to a file
video_with_text.write_videofile("finalvideo.mp4", codec='libx264', fps=24)