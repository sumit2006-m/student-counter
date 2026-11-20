# Smart Student Counter

The Flask dashboard streams the webcam with YOLO person detection and shows the
current detected-person count.

## Setup

From the project directory, create and activate a virtual environment, then
install the dependencies:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the Flask dashboard

Start the app from the project directory:

```powershell
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. Keep the
terminal running while you use the dashboard. Do not run `detector.py` at the
same time; both programs use the webcam.

The standalone `python detector.py` command opens an OpenCV window instead of
the Flask dashboard.
