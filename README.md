# Motorcycle Pose Simulator

Real-time motorcycle riding posture simulator using computer vision, MediaPipe, WebSocket communication and Unreal Engine 5.

## Goal

The goal of this project is to track rider body posture using a camera, analyze riding-related body movements, and visualize the rider on a motorcycle in Unreal Engine.

The project is intended both as a technical portfolio project and as a foundation for a future motorcycle riding coach.

## Current status

- [x] IP Webcam camera stream works
- [x] OpenCV receives video stream
- [x] MediaPipe Pose detects body landmarks
- [x] Basic skeleton visualization works
- [x] Initial GitHub repository created

## Planned features

- [ ] Modular Python tracker
- [ ] Arm angle detection
- [ ] Body lean detection
- [ ] Foot position detection for gear shifting and rear brake
- [ ] RiderState data model
- [ ] WebSocket data publishing
- [ ] Unreal Engine rider visualization
- [ ] Riding coach feedback

## Architecture

```text
Camera / IP Webcam
        |
        v
Camera Module
        |
        v
Pose Detector
        |
        v
Pose Analyzer
        |
        +--> Hand Analyzer
        +--> Body Analyzer
        +--> Foot Analyzer
        |
        v
RiderState
        |
        v
JSON / WebSocket
        |
        v
Unreal Engine 5
        |
        v
Motorcycle Rider Avatar