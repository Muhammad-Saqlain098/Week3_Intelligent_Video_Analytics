# Installation Guide

## 1. Prerequisites

- Python 3.9–3.11
- (Optional but recommended) an NVIDIA GPU with CUDA for real-time FPS
- A webcam, and/or the **Iriun Webcam** app installed on your phone +
  its desktop client installed on your computer, if you want to use a
  mobile camera as input

## 2. Clone / Download the Project

```bash
git clone <your-repo-url>
cd Week3_Intelligent_Video_Analytics
```

## 3. Create a Virtual Environment

```bash
python -m venv venv

# Activate it:
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: `ultralytics` (YOLOv8 + built-in ByteTrack/BoT-SORT
trackers), `opencv-python`, `numpy`, `psutil`, `streamlit` (for the web
GUI), plus optional `supervision`, `matplotlib`, and `plotly` used by
the reference tracker and reporting scripts.

## 5. Add Your Model and Video

- Copy your trained YOLO weights to `model/best.pt`
  (or point `MODEL_PATH` in `utils/config.py` at wherever you keep it).
- Copy a test video to `videos/input.mp4`
  (only needed if you plan to use the "file" source mode).

## 6. Set Up Your Camera Source

### Laptop Webcam
No setup needed — usually camera index 0. If it doesn't work, run:
```bash
python find_camera_index.py
```

### Mobile Camera via Iriun Webcam
1. Install the **Iriun Webcam** app on your phone (App Store / Play Store).
2. Install the **Iriun Webcam** desktop client on your computer from
   https://iriun.com and run it.
3. Open the app on your phone and the desktop client — they should
   connect automatically over the same Wi-Fi network (or via USB cable,
   depending on the client version).
4. Run `python find_camera_index.py` to see which camera index shows
   your phone's live feed (commonly index 1, but this varies by
   machine and by what other camera software you have installed).
5. Set `IRIUN_INDEX` in `utils/config.py` to that index, or pass
   `--source iriun` on the command line.

### Uploaded Video File (via the Web GUI)
No local setup needed — see Section 7, "Upload Video File" option.

### RTSP Network Camera
Set `RTSP_URL` in `utils/config.py`, or pass `--source rtsp --rtsp-url "rtsp://..."`.

## 7. Run the Application

### Command-Line App
```bash
python app.py                                    # uses utils/config.py defaults
python app.py --source webcam
python app.py --source iriun
python app.py --source file --video videos/input.mp4
python app.py --source rtsp --rtsp-url rtsp://user:pass@ip:554/stream
python app.py --tracker botsort
```
Press **q** to quit, **s** to save a screenshot.

### Web GUI (camera picker + video upload, in the browser)
```bash
streamlit run streamlit_app.py
```
Open the printed local URL, choose a source in the sidebar (Laptop
Webcam / Iriun Mobile Camera / Upload Video File / RTSP Stream), pick a
tracker, and click **Start Analytics**. Download buttons for the
output video and CSV log appear once the run finishes.

## 8. Run the Tracking Experiments (Assignment 2)

```bash
python tracking_experiments.py --video videos/input.mp4
```

Results are saved to `outputs/tracking_experiments_results.csv`.

## 9. Troubleshooting

| Problem | Likely Fix |
|---|---|
| "Could not open video source" for webcam/iriun | Wrong camera index — run `find_camera_index.py` |
| Iriun shows "Not Connected" | Make sure phone and PC are on the same Wi-Fi network, or use the USB option in the Iriun client |
| Very low FPS | Use a smaller YOLO model, enable GPU, or lower `CONFIDENCE_THRESHOLD`/resolution |
| `ultralytics` can't find `bytetrack.yaml`/`botsort.yaml` | Update ultralytics: `pip install -U ultralytics` (these ship built-in) |
| Streamlit page is blank | Make sure you ran `streamlit run streamlit_app.py`, not `python streamlit_app.py` |
