#!/bin/bash
# Ep. 2 look-check renders: 960x540, 8 samples, every 2nd frame (interpolated in the reel).
cd "$(dirname "$0")"
export PILOT_ROOT="$PWD"; mkdir -p renders
for s in m1_card m2_busstop m3_room m6_bench m9_cards m10_bar; do
  n=$(echo $s | cut -d_ -f1 | tr a-z A-Z)
  echo "START $s $(date +%T)"
  RES=960x540 SAMPLES=8 GLARE=0 STEP=2 python3 blender/$s.py anim > renders/log_$s.txt 2>&1
  echo "DONE $s $(date +%T) exit=$? frames=$(ls renders/$n/*.png 2>/dev/null | wc -l)"
done
echo ALLDONE
