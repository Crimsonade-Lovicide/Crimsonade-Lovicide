#!/bin/bash
cd "$(dirname "$0")"
for s in b5_city b4_globe b3_hemicycle b2_chairs b1_towers; do
  echo "START $s $(date +%T)"
  RES=960x540 SAMPLES=6 GLARE=0 STEP=2 python3 blender/$s.py anim > renders/log_$s.txt 2>&1
  echo "DONE $s $(date +%T) exit=$? frames=$(ls renders/B${s:1:1}/*.png 2>/dev/null | wc -l)"
done
