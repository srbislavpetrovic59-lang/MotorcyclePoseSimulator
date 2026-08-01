# Algorithm Notes

## Purpose

This document records the reasoning behind the algorithms used in
Motorcycle Pose Simulator.

Its purpose is to explain why an algorithm exists,
what it measures,
what assumptions it makes,
and what conclusions were reached during experiments.

This document complements the source code.
The code explains *how* an algorithm works.
This document explains *why* it exists.

---

# Experiments

## 2026-08-01

### Thumb–Index Distance

**Hypothesis**

The distance between the thumb tip and the index finger tip
could represent clutch position.

**Implementation**

Measured the Euclidean distance between:

- HandLandmark.THUMB_TIP
- HandLandmark.INDEX_FINGER_TIP

using:

```python
distance = math.hypot(
    point2.x - point1.x,
    point2.y - point1.y,
)
```

**Observed values**

| Gesture | Approximate value |
|---------|------------------:|
| Thumb touching index finger | ~0.007 |
| Slightly open | ~0.18 |
| Fully open | ~0.53 |

**Conclusion**

The metric is stable and responds well to finger movement.

However, it measures **hand openness**, not clutch position.

The metric remains useful for future gesture recognition
and may later contribute to higher-level hand analysis.

**Status**

✅ Accepted as a general hand metric.

❌ Rejected as a direct clutch metric.

---

### Left Wrist Relative to Shoulder

**Hypothesis**

The vertical position of the left wrist relative to the left shoulder
could indicate clutch usage.

**Implementation**

Measured:

```
left_wrist_y - left_shoulder_y
```

**Conclusion**

The metric behaves consistently.

However, it is strongly influenced by camera position,
body posture,
and rider movement.

It is useful as a low-level measurement,
but insufficient on its own for clutch estimation.

**Status**

🟡 Experimental.
Further investigation required.

---

# Design Principle

The simulator never guesses.

Low-level analyzers measure objective facts.

Higher-level components combine those facts
to infer rider actions.

Example:

Measurements
↓
HandEvaluator
↓
Clutch estimation
↓
PoseCoach feedback