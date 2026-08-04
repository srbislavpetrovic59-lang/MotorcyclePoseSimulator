assert is_head_forward(
    head_roll=0.02,
    head_yaw_ratio=0.01,
)

assert not is_head_forward(
    head_roll=0.30,
    head_yaw_ratio=0.60,
)