#!/bin/bash
set -e
cd /home/user/work
NF=$(python3 -c "import json;print(round(json.load(open('out/plan.json'))['total']*30))")
A=$((NF/3)); B=$((2*NF/3))
echo "frames $NF split $A $B"
python3 compose.py 0 $A out/chunk_0.mp4 > out/c0.log 2>&1 &
python3 compose.py $A $B out/chunk_1.mp4 > out/c1.log 2>&1 &
python3 compose.py $B $NF out/chunk_2.mp4 > out/c2.log 2>&1 &
wait
printf "file '%s'\n" /home/user/work/out/chunk_0.mp4 /home/user/work/out/chunk_1.mp4 /home/user/work/out/chunk_2.mp4 > out/chunks.txt
ffmpeg -v error -y -f concat -safe 0 -i out/chunks.txt -i audio/mix_final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart out/Podcast_Final_10-11_Minutes.mp4
echo FINAL_DONE
