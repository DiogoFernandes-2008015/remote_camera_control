# remote_camera_control
Python code based on a flask server to remotly control a camera mounted on a pan-tilt plataform using servo motors and a raspberry pi4.
# 📷 Wi-Fi Remote-Controlled Pan-Tilt Inspection Camera System

A remote control system for a camera mounted on a 2-axis pan-tilt platform, accessible via web browser from any device connected to the same Wi-Fi network. Built and tested on a **Raspberry Pi 4** with a **RaspCam (Camera Module)**.

The project exposes a responsive web interface (optimized for tablets/smartphones) that lets you view a live video feed, move the camera on the pan and tilt axes, and capture inspection snapshots with the current angle automatically embedded in the filename.

---

## ✨ Features

- **Real-time video streaming** via MJPEG (`OpenCV` + `Flask Response`), viewable directly in the browser.
- **Smooth pan-tilt control**, with continuous movement while a button is held down (touch and mouse), running on a separate thread so the server never blocks.
- **Real-time telemetry**: current pan and tilt angles displayed in the UI (`/status`), refreshed every 200ms.
- **Center/Reset button**, instantly zeroing both axes.
- **Snapshot capture (📸)**, saving the image locally to `~/projeto00/capturas` with a filename containing a timestamp and the current angles (`snap_YYYYMMDD_HHMMSS_P<pan>_T<tilt>.jpg`).
- **Mobile-first web interface**, dark theme, no external dependencies (plain HTML/CSS/JS).

---

## 🛠️ Hardware Used

| Component               | Specification                                    |
|---------------------------|----------------------------------------------------|
| Board                    | Raspberry Pi 4                                     |
| Camera                   | RaspCam (Camera Module, CSI interface)             |
| Pan servo                | Micro servo connected to GPIO 12                   |
| Tilt servo               | Micro servo connected to GPIO 13                   |
| Servo control            | `pigpio` (via the `pigpiod` daemon)                |
| Power supply             | External power supply recommended for the servos   |

> ⚠️ The servos use `gpiozero.Servo` with pulse widths between `0.6ms` and `2.4ms`. Adjust these values as needed depending on your servo model.

---

## 📦 Software Requirements

- Raspberry Pi OS (tested on a Raspberry Pi 4 setup)
- Python 3
- `pigpiod` daemon running
- Python libraries:
  - `flask`
  - `opencv-python`
  - `gpiozero`
  - `pigpio`

### Installing dependencies

```bash
sudo apt update
sudo apt install -y python3-pip pigpio python3-opencv
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

pip3 install flask gpiozero
```

---

## 📁 Project Structure

```
.
├── robo_app.py           # Flask server: streaming, servo control and snapshots
├── templates/
│   └── index.html        # Web control interface (inspection panel)
└── README.md
```

> ⚠️ Flask expects the `index.html` file to be inside the `templates/` folder. Make sure to keep this directory structure.

---

## 🚀 Usage

1. Make sure `pigpiod` is running:
   ```bash
   sudo systemctl status pigpiod
   ```

2. Run the server:
   ```bash
   python3 robo_app.py
   ```

3. From any device on the **same Wi-Fi network**, open in a browser:
   ```
   http://<RASPBERRY_PI_IP>:5000
   ```

4. Use the directional buttons to move the camera, the **RESET** button to re-center it, and **CAPTURE IMAGE** to save a snapshot.

---

## 🔧 Adjustable Settings

| Parameter                    | Location in code            | Description                                              |
|--------------------------------|--------------------------------|--------------------------------------------------------------|
| `passo_suave`                  | `robo_app.py`                  | Movement sensitivity/speed (default `0.02`)                 |
| `min_pulse_width` / `max_pulse_width` | `robo_app.py`         | Servo PWM pulse range                                        |
| `CAPTURAS_PATH`                 | `robo_app.py`                  | Directory where snapshots are saved                          |
| Server port                     | `app.run(...)`                 | Default `5000`                                                |

---

## 🗺️ API Endpoints

| Route            | Method | Description                                                          |
|--------------------|--------|--------------------------------------------------------------------------|
| `/`                 | GET    | Main web interface                                                     |
| `/video_feed`       | GET    | MJPEG video stream                                                      |
| `/control`          | GET    | Sends a movement command (`?direction=up/down/left/right/center/stop`) |
| `/status`           | GET    | Returns the current pan and tilt angles as JSON                        |
| `/snapshot`         | GET    | Captures and saves an image, returns the filename as JSON              |

---

## 📌 Notes & Limitations

- Specifically tested on a Raspberry Pi 4 with a RaspCam; other USB cameras may require adjusting the `cv2.VideoCapture()` index.
- Access is intended for the local network (LAN/Wi-Fi); no authentication is implemented — do not expose port `5000` directly to the internet without adding a security layer.
- The server runs with `debug=False` by default, recommended for field/production use.

---

## ✍️ Author

Developed by **Diogo Lopes Fernandes**.
