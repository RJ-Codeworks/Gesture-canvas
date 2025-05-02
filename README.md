# Gesture-canvas
A real-time hand gesture-controlled drawing application using MediaPipe and OpenCV. Draw, erase, select colors, and save your work using natural hand gestures—no touch or mouse required.
# ✨ Features
✍️ Pinch-to-draw with index and thumb

☝️ Point to select color from sidebar

✋ Open palm to clear canvas

✊ Fist to enable eraser (black)

🤘 Rock gesture to save drawing as PNG

🖼️ Overlay canvas on live webcam feed

💻 Works in real time on GPU && CPU
# 🛠️ Requirements
Python 3.9+

OpenCV

MediaPipe

NumPy
# 📦 Installation
git clone https://github.com/<your-username>/gesture-canvas.git
cd gesture-canvas

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
# 🚀 Run the App
python landmark_draw_app.py
# 🧠 Gesture Controls
Gesture	Action
🤏 Pinch	Draw
☝️ Index only	Select color
✋ Open palm	Clear canvas
✊ Fist	Switch to eraser
🤘 Rock (index + pinky)	Save drawing
# 📁 Output
Saved drawings go to the root directory:

php-template
Copy
Edit
drawing_<timestamp>.png
# 📚 Credits
MediaPipe Hands

OpenCV

# Developed by 
-Youssef Araby username: youssef-Araby

-Rodaina Hebishy username: RodainaMH
