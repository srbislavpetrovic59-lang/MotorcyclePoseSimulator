The original RiderState concept was replaced during the architecture refactoring.
Explicit measurements and specialized analyzers provide a simpler
and more maintainable design than a centralized mutable RiderState object.





struct RiderState

{

&#x20;   //------------------------

&#x20;   // Tracking quality

&#x20;   //------------------------



&#x20;   float PoseConfidence;



&#x20;   //------------------------

&#x20;   // Head

&#x20;   //------------------------



&#x20;   float HeadYaw;

&#x20;   float HeadPitch;



&#x20;   //------------------------

&#x20;   // Arms

&#x20;   //------------------------



&#x20;   float LeftShoulder;

&#x20;   float RightShoulder;



&#x20;   float LeftElbow;

&#x20;   float RightElbow;



&#x20;   //------------------------

&#x20;   // Controls

&#x20;   //------------------------



&#x20;   float Throttle;

&#x20;   float Clutch;

&#x20;   float FrontBrake;



&#x20;   //------------------------

&#x20;   // Body

&#x20;   //------------------------



&#x20;   float BodyLean;

&#x20;   float HipRotation;



&#x20;   //------------------------

&#x20;   // Legs

&#x20;   //------------------------



&#x20;   float LeftKnee;

&#x20;   float RightKnee;



&#x20;   float LeftFoot;

&#x20;   float RightFoot;



&#x20;   float RearBrake;



&#x20;   int Gear;

};

