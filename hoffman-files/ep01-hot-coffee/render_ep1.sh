#!/bin/bash
cd "$(dirname "$0")"
export PILOT_ROOT="$PWD"; mkdir -p renders
for s in e3_spill e1_cup e2_car e4_skin e7_folders e9_clock; do
  n=$(echo $s | cut -c1-2 | tr a-z A-Z)
  rm -rf renders/$n
  echo "START $s $(date +%T)"
  RES=960x540 SAMPLES=8 GLARE=0 STEP=2 python3 blender/$s.py anim > renders/log_$s.txt 2>&1
  echo "DONE $s $(date +%T) exit=$? frames=$(ls renders/$n/*.png 2>/dev/null | wc -l)"
done
