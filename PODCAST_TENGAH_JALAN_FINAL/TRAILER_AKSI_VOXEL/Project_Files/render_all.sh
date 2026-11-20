#!/bin/bash
cd /home/user/work/t3d
node renderframes.js frames 0 300 > r0.log 2>&1 &
node renderframes.js frames 300 600 > r1.log 2>&1 &
node renderframes.js frames 600 897 > r2.log 2>&1 &
wait
ffmpeg -v error -y -framerate 30 -i frames/%05d.jpg -i action_mix.wav -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart Trailer_Aksi_Voxel.mp4 && echo ENCODED
