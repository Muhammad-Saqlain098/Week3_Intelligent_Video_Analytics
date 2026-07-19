# Intelligent Video Analytics — Week 3 Project

A real-time video analytics system built with **YOLOv8** and **ByteTrack**, featuring
object detection, multi-object tracking, virtual line counting, Region of Interest
(ROI) monitoring, trajectory & direction analysis, a live analytics dashboard,
detection logging, and a bonus heatmap.

## Features

| Feature | Description |
|---|---|
| YOLOv8 Detection | Real-time object detection on video, webcam, mobile camera, or RTSP |
| ByteTrack / BoT-SORT Tracking | Assigns a persistent unique ID to every object; switch trackers via config or `--tracker` flag |
| Multiple Video Sources | Laptop webcam, **Iriun mobile camera**, **uploaded video file**, or RTSP network stream |
| Virtual Line Counter | Counts IN / OUT crossings across a user-defined line (any angle) |
| Multi-ROI Monitoring | Counts objects inside one or more named zones |
| Trajectory Drawing | Draws each object's movement path over time |
| Direction Detection | Reports UP / DOWN / LEFT / RIGHT / diagonal movement |
| Analytics Dashboard | Live FPS, object count, IN/OUT, ROI count, confidence, CPU/RAM |
| Detection Logging | Every detection saved to `outputs/detections.csv` |
| Video Recording | Saves the fully annotated run to `outputs/output.mp4` |
| Heatmap (Bonus) | Visualizes where objects spend the most time |
| Web GUI (Streamlit) | Browser control panel: pick a source (including upload), pick a tracker, watch live, download results |
| Tracking Experiments | Script comparing ByteTrack vs BoT-SORT, confidence thresholds, and resolutions |

## Video Source Options

This project supports four ways to feed it video, both from the
command line (`app.py`) and the web GUI (`streamlit_app.py`):

1. **Laptop Webcam** — your built-in camera (usually index 0)
2. **Iriun Mobile Camera** — use your phone as the camera via the
   [Iriun Webcam](https://iriun.com) app + desktop client
3. **Upload Video File** — pick any local `.mp4`/`.avi`/`.mov`/`.mkv` file
   (via the Streamlit GUI's file uploader, or `--video path/to/file.mp4`
   on the command line)
4. **RTSP Stream** — a network/IP camera URL

See `docs/installation_guide.md` for full setup steps for each, and run
`python find_camera_index.py` if you're not sure which index your
laptop's camera vs. Iriun uses on your machine.

## Project Structure

```
Week3_Intelligent_Video_Analytics/
│
├── app.py                       # Main CLI application (entry point)
├── streamlit_app.py             # Web GUI: source picker, video upload, live view
├── tracker.py                   # YOLO + ByteTrack/BoT-SORT wrapper (ultralytics native)
├── tracker_supervision.py        # Reference/comparison tracker (supervision-based ByteTrack)
├── video_source.py               # Resolves webcam/iriun/file/rtsp into a VideoCapture
├── find_camera_index.py          # Helper: identify laptop vs Iriun camera index
├── tracking_experiments.py       # Assignment 2: ByteTrack vs BoT-SORT, conf, resolution
├── dashboard.py                  # Analytics dashboard overlay
├── counter.py                    # Virtual line IN/OUT counter
├── roi.py                        # Region of Interest monitoring
├── trajectory.py                 # Movement history, trajectory, direction
├── performance.py                # FPS / CPU / RAM / inference time
├── logger.py                     # CSV detection logging
├── heatmap.py                    # Bonus heatmap generator
│
├── utils/
│   ├── drawing.py                # All OpenCV drawing helpers
│   ├── colors.py                 # Color palette
│   ├── config.py                 # All tunable settings (incl. camera source, tracker choice)
│   └── helpers.py                # Small shared utilities
│
├── model/
│   └── best.pt                   # Your trained YOLO weights (add your own)
│
├── videos/
│   └── input.mp4                 # Your source video (add your own)
│
├── outputs/
│   ├── output.mp4                 # Annotated output video (generated)
│   ├── detections.csv              # Detection log (generated)
│   ├── tracking_experiments_results.csv  # Assignment 2 results (generated)
│   └── screenshots/                # Saved screenshots (press "s" while running)
│
├── requirements.txt
├── README.md
├── docs/
│   ├── architecture.md            # + Architecture Diagram.docx
│   ├── research_report.md         # + Research Report.docx
│   ├── performance_report.md      # + Performance Report.docx
│   ├── builder_journal.md         # + Builder Journal.docx
│   ├── tracking_experiments.md
│   ├── installation_guide.md
│   ├── demo_script.md
│   └── viva_questions.md
```

## Installation

```bash
git clone <your-repo-url>
cd Week3_Intelligent_Video_Analytics
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Setup

1. Place your trained YOLO weights at `model/best.pt`
   (or edit `utils/config.py` → `MODEL_PATH` to point elsewhere).
2. Choose a video source — laptop webcam, Iriun mobile camera, an
   uploaded/local video file, or RTSP — see "Video Source Options"
   above and `docs/installation_guide.md` for full setup steps.
3. Adjust the counting line, ROI zones, thresholds, tracker choice, and
   dashboard options in `utils/config.py` — every tunable value lives there.

## Run

### Command line
```bash
python app.py                                      # uses utils/config.py defaults
python app.py --source webcam                        # laptop camera
python app.py --source iriun                          # phone via Iriun Webcam
python app.py --source file --video videos/input.mp4
python app.py --source rtsp --rtsp-url rtsp://...
python app.py --tracker botsort                        # switch tracker
```

- Press **`q`** to quit.
- Press **`s`** to save a screenshot of the current frame to `outputs/screenshots/`.

### Web GUI (source picker + video upload in the browser)
```bash
streamlit run streamlit_app.py
```
Pick a source in the sidebar — including **Upload Video File** for
drag-and-drop video analysis — choose a tracker, click **Start
Analytics**, and download the annotated video / CSV log when done.

## Output

After a run you'll have:
- `outputs/output.mp4` — the full annotated video
- `outputs/detections.csv` — a row-per-detection log with tracker ID, class,
  confidence, bounding box, ROI zone membership, and direction
- Console summary of total frames, total IN/OUT counts

## Configuration Reference

All settings are centralized in `utils/config.py`, including:
- Detection confidence / IoU thresholds
- ByteTrack tracking parameters
- Line counter coordinates
- One or more ROI zones (name, coordinates, color)
- Trajectory history length
- Dashboard appearance
- Heatmap radius / decay
- Output toggles (save video, save logs, show window)

## Documentation

See the `docs/` folder for:
- `architecture.md` — system architecture and pipeline diagram
- `research_report.md` — 4-page style research report
- `performance_report.md` — performance benchmarking and analysis
- `builder_journal.md` — development journal
- `demo_script.md` — 8–10 minute demo video script
- `viva_questions.md` — complete viva preparation Q&A

## Real-World Applications

- **Smart City** — vehicle counting, traffic monitoring, congestion detection
- **Retail** — customer counting, occupancy analysis, queue monitoring
- **Airports** — passenger flow, security analytics
- **Factories** — worker tracking, restricted-area monitoring
- **Parking** — free space counting, vehicle tracking

## License

For educational / internship use.
