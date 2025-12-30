NUM_GENES = 5

GENE_NAMES = [
    "wheel_size",
    "wheel_density",
    "suspension_hardness",
    "wheel_left_pos",
    "wheel_right_pos"
]

GENE_SPACE = [
    {"low": 0.5, "high": 2.0},    # wheel_size
    {"low": 0.2, "high": 1.0},    # wheel_density
    {"low": 0.0, "high": 1.0},    # suspension_hardness
    {"low": 0.0, "high": 1.0},    # wheel left (0 is centered, 1 is outside of the vehicle)
    {"low": 0.0, "high": 0.5}     # wheel_right (0 is centered, 1 is outside of the vehicle)
]