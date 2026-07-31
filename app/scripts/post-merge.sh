#!/bin/bash
set -e

pip install -r requirements.txt --quiet

# ultralytics pulls in opencv-python (non-headless) which requires libGL.
# Force the headless build after so cv2 works in Replit's display-free environment.
pip install opencv-python-headless --force-reinstall --quiet
