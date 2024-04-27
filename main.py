from moviepy.editor import *
from moviepy.video.compositing.concatenate import concatenate_videoclips
import wave
import json
import os
from vosk import Model, KaldiRecognizer, SetLogLevel
SetLogLevel(-1)
class Word:
    ''' A class representing a word from the JSON format for vosk speech recognition API '''

    def __init__(self, dict):
        '''
        Parameters:
          dict (dict) dictionary from JSON, containing:
            conf (float): degree of confidence, from 0 to 1
            end (float): end time of the pronouncing the word, in seconds
            start (float): start time of the pronouncing the word, in seconds
            word (str): recognized word
        '''

        self.conf = dict["conf"]
        self.end = dict["end"]
        self.start = dict["start"]
        self.word = dict["word"]

    def to_string(self):
        ''' Returns a string describing this instance '''
        return "{:20} from {:.2f} sec to {:.2f} sec, confidence is {:.2f}%".format(
            self.word, self.start, self.end, self.conf*100)
    def times(self):
        ''' Returns a tuple with start and end times '''
        return (self.start, self.end)
    def word(self):
        ''' Returns the recognized word '''
        return self.word
    def all(self):
        return self.word, self.start, self.end, self.conf*100
os.system("ffmpeg -i voiceover.mp3 -ac 1 -ar 22050 voiceover.wav")
audio_filename = "voiceover.wav"
custom_Word = Word
model = Model(lang="en-us")
wf = wave.open(audio_filename, "rb")
rec = KaldiRecognizer(model, wf.getframerate())
rec.SetWords(True)

# get the list of JSON dictionaries
results = []
# recognize speech using vosk model
while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        part_result = json.loads(rec.Result())
        results.append(part_result)
part_result = json.loads(rec.FinalResult())
results.append(part_result)

# convert list of JSON dictionaries to list of 'Word' objects
list_of_Words = []
for sentence in results:
    if len(sentence) == 1:
        # sometimes there are bugs in recognition 
        # and it returns an empty dictionary
        # {'text': ''}
        continue
    for obj in sentence['result']:
        w = custom_Word(obj)  # create custom Word object
        list_of_Words.append(w)  # and add it to list
maindict = {}
wf.close()  # close audiofile
from collections import OrderedDict
import json

# convert list of JSON dictionaries to list of 'Word' objects
list_of_Words = []
for sentence in results:
    if len(sentence) == 1:
        continue
    for obj in sentence['result']:
        w = custom_Word(obj)  # create custom Word object
        list_of_Words.append(w)  # and add it to list

wf.close()  # close audiofile
with open('timestamped.txt', 'w') as f:
    for word in list_of_Words:
        theword = word.all()
        #f.write(', '.join(map(str, theword)))
        f.write(f"{theword[0]},{theword[1]},{theword[2]}")
        f.write('\n')
    f.close()

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