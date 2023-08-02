#!/bin/bash

# Get the fps using command substitution and round it to the nearest integer
url="https://storage.googleapis.com/glide-prod.appspot.com/uploads-v2/5dhsSuUFnyR2lKOccs1r/pub/QxlMNmM32RCGSyCUjynU.mp4"

# Stream the video to ffprobe and get fps
fps=$(wget -qO - $url | ffprobe -i pipe:0 -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate)

# Clean up the fps value to get a clean decimal number
fps=${fps%/*}
fps=$(bc <<< "scale=2; $fps")

# Extract 100 frames using the rounded fps value
ffmpeg -i "https://storage.googleapis.com/glide-prod.appspot.com/uploads-v2/5dhsSuUFnyR2lKOccs1r/pub/QxlMNmM32RCGSyCUjynU.mp4" -vf "fps=$fps" -vframes 100 "./frames/frame-%03d.jpg"
