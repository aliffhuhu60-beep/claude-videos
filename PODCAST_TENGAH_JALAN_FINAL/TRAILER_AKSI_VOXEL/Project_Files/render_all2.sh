#!/bin/bash
cd /home/user/work/t3d
node renderframes2.js frames2 0 390 > q0.log 2>&1 &
node renderframes2.js frames2 390 780 > q1.log 2>&1 &
node renderframes2.js frames2 780 1170 > q2.log 2>&1 &
wait
N=$(ls frames2/*.jpg | wc -l); echo "frames $N"
ffmpeg -v error -y -framerate 30 -i frames2/%05d.jpg -i action2_mix.wav -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart Trailer_Aksi_Voxel_v2.mp4 && echo ENCODED
