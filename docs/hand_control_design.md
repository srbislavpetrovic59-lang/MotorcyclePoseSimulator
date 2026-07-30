Hand Control Design
Purpose

HandControlAnalyzer analyzes rider hand controls.

Its responsibility is to measure objective hand-related
metrics.

It never determines riding quality or gives feedback.

Position in the Architecture
Camera
      │
      ├── Pose Detector
      └── Hands Detector
              │
              ▼
     HandControlAnalyzer
              │
              ▼
         RiderState
              │
              ▼
     RidingStateRecognizer
              │
              ▼
          PoseCoach
Responsibilities

HandControlAnalyzer measures hand geometry and hand
interaction with motorcycle controls.

It never performs coaching.

Input

Initially:

Pose landmarks

Later:

Pose landmarks
+
Hand landmarks
Output

Initially the analyzer may expose:

left_hand_position
right_hand_position

After MediaPipe Hands:

left_clutch_stage
front_brake_state
throttle_rotation
Future Metrics
Clutch

Possible stages

Stage 1
Hand on grip

Stage 2
Fingers covering clutch

Stage 3
Initial clutch movement

Stage 4
Friction zone

Stage 5
Clutch fully released
Front Brake
Not covering

Covering

Light braking

Heavy braking
Throttle
Closed

Slight opening

Moderate opening

Wide open
Design Principles
Measures only observable geometry.
Never performs coaching.
Never estimates rider intentions.
Designed to accept richer hand landmarks in future.
Notes

Motorcycle controls require much finer hand tracking than
MediaPipe Pose provides.

Therefore MediaPipe Hands is considered a future input source
for this analyzer.dataka.