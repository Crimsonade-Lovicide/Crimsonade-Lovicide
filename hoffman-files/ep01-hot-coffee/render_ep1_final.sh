#!/bin/bash
# Final reconstructions: 1280x720 Cycles, upscaled to 1080p in the conform.
# Fast-motion scenes render every frame; slow ones render every 2nd frame and are motion-interpolated.
cd "$(dirname "$0")"
export PILOT_ROOT="$PWD"; mkdir -p renders
for spec in ${@:-e3_spill:1 e7_folders:1 e1_cup:2 e2_car:2 e4_skin:2 e9_clock:2}; do
  s=${spec%%:*}; step=${spec##*:}; n=$(echo $s | cut -c1-2 | tr a-z A-Z)
  if [ -f renders/$n/.done ]; then echo "SKIP $s"; continue; fi
  echo "START $s step=$step $(date +%T)"
  RES=1280x720 SAMPLES=${SAMPLES:-11} STEP=$step python3 blender/$s.py anim > renders/log_final_$s.txt 2>&1
  rc=$?; [ $rc -eq 0 ] && touch renders/$n/.done
  echo "DONE $s $(date +%T) exit=$rc frames=$(ls renders/$n/*.png 2>/dev/null | wc -l)"
done
echo ALLDONE
