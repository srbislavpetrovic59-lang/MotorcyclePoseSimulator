Design Decision 006

Left hand rotation is insufficient to detect the clutch friction zone.

Context

Experiments showed:

State	Left hand rotation
Clutch released	−100° … −130°
Friction zone	−2° … −15°
Fully pulled	−3° … −8°
Decision

left_hand_rotation is suitable for detecting that the rider is actively operating the clutch.

It is not sufficient to distinguish:

friction zone
fully pulled clutch

Additional finger geometry is required.

Consequences

The project will introduce an additional hand metric.

The first candidate is:

index_finger_bend