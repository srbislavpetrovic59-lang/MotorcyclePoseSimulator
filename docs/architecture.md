\# Motorcycle Pose Simulator Architecture



\## Overview



The system is divided into independent modules.



```text

               Camera

                  │

                  ▼

            Camera Module

                  │

                  ▼

           Pose Detector

                  │
                  ▼

            Pose Analyzer

                   │

     ┌─────────────┼─────────────┐

     ▼             ▼             ▼

Hand Analyzer  Body Analyzer  Foot Analyzer

     │             │             │

     └─────────────┼─────────────┘

                   ▼

             RiderState

                   │

                   ▼

            WebSocket Client

                   │

                   ▼

            Unreal Engine 5

```



\---



\## Camera Module



Responsible for:



\- opening the camera

\- reading video frames

\- handling reconnects

\- hiding camera implementation details



Future camera sources:



\- IP Webcam

\- USB Webcam

\- DroidCam

\- Video file



\---



\## Pose Detector



Responsible for:



\- MediaPipe initialization

\- landmark detection

\- returning normalized pose data



\---



\## Pose Analyzer



Transforms landmarks into motorcycle-related information.



Examples:



\- elbow angle

\- shoulder angle

\- body lean

\- head direction

\- knee angle

\- foot position



\---



\## RiderState



Single data model exchanged between Python and Unreal Engine.



The Unreal project must not depend on MediaPipe.



\---



\## Unreal Engine



Receives RiderState through WebSocket.



Responsibilities:



\- rider animation

\- motorcycle controls visualization

\- UI

\- riding feedback


```text
PoseAnalyzer
    │
    ├── ArmAnalyzer
    ├── BodyAnalyzer
    ├── FootAnalyzer
    └── Geometry

    PoseAnalyzer
      │
      ▼
PoseMetrics
      │
      ▼
PoseEvaluator
```
