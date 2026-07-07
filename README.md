\# Motorcycle Pose Simulator



Computer vision based motorcycle riding posture simulator.



The goal of this project is to track rider body posture using a camera,

process pose landmarks with MediaPipe, and later send the data to Unreal Engine

for real-time visualization of motorcycle riding position.



\## Current status



\- IP Webcam camera stream works

\- OpenCV receives video stream

\- MediaPipe Pose detects body landmarks

\- Basic skeleton visualization works



\## Planned features



\- Calculate arm, shoulder and body angles

\- Detect throttle, clutch and brake-like movements

\- Send pose data to Unreal Engine via WebSocket

\- Animate a rider avatar on a motorcycle

\- Provide posture feedback for beginner motorcycle training



\## Project structure



```text

python\_tracker/   Python + OpenCV + MediaPipe tracking

unreal/           Unreal Engine project placeholder

docs/             Architecture and design notes

