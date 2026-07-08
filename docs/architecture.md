\# Motorcycle Pose Simulator Architecture



\## Overview



The system is divided into independent modules.



```text

&#x20;                Camera

&#x20;                   │

&#x20;                   ▼

&#x20;            Camera Module

&#x20;                   │

&#x20;                   ▼

&#x20;            Pose Detector

&#x20;                   │

&#x20;                   ▼

&#x20;            Pose Analyzer

&#x20;                   │

&#x20;     ┌─────────────┼─────────────┐

&#x20;     ▼             ▼             ▼

&#x20;Hand Analyzer  Body Analyzer  Foot Analyzer

&#x20;     │             │             │

&#x20;     └─────────────┼─────────────┘

&#x20;                   ▼

&#x20;              RiderState

&#x20;                   │

&#x20;                   ▼

&#x20;            WebSocket Client

&#x20;                   │

&#x20;                   ▼

&#x20;            Unreal Engine 5

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

