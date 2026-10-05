#!/bin/bash
# Assemble the six Blender previews into one labeled review reel (12 fps renders -> 24 fps, 1280x720).
cd "$(dirname "$0")"
mkdir -p out/ep1
FONT=${FONT:-/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf}  # any monospace TTF
i=0; list=out/ep1/list.txt; : > $list
for pair in "E1|Cold open: cup on the dashboard" "E2|Parked hatchback, dawn" "E3|Spill reconstruction" "E4|Skin cross-section, full-thickness burn" "E7|700+ burn reports, 1 folder = 10" "E9|Two days of coffee sales"; do
  n=${pair%%|*}; label=${pair#*|}
  ffmpeg -v error -y -framerate 12 -pattern_type glob -i "renders/$n/*.png" \
    -vf "minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale=1280:720:flags=lanczos,drawtext=fontfile=$FONT:text='$n  ·  $label  ·  PREVIEW':x=32:y=28:fontsize=22:fontcolor=white@0.85:box=1:boxcolor=black@0.45:boxborderw=8" \
    -c:v libx264 -crf 22 -preset medium -pix_fmt yuv420p out/ep1/$n.mp4
  echo "file '$n.mp4'" >> $list
done
ffmpeg -v error -y -f concat -safe 0 -i $list -c copy out/ep1/ep1_reconstructions_preview.mp4
ls -la out/ep1/ep1_reconstructions_preview.mp4
