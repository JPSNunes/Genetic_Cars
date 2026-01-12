# genome.py

NUM_GENES = 13

GENE_NAMES = [
    "wheelRadius",
    "wheelMass",
    "wheelDamping",
    "suspensionDistance",
    "suspensionSpring",
    "suspensionDamper",
    "suspensionTargetPos",
    "forwardExtremumSlip",
    "forwardExtremumValue",
    "forwardAsymptoteSlip",
    "forwardAsymptoteValue",
    "forwardStiffness",
    "carMass"
]

GENE_SPACE = [
    {"low": 0.2, "high": 1.0},      # wheelRadius
    {"low": 10.0, "high": 80.0},    # wheelMass
    {"low": 0.0, "high": 2.0},      # wheelDamping
    {"low": 0.05, "high": 0.5},     # suspensionDistance
    {"low": 5000, "high": 50000},   # suspensionSpring
    {"low": 500, "high": 5000},     # suspensionDamper
    {"low": 0.0, "high": 1.0},      # suspensionTargetPos
    {"low": 0.1, "high": 1.0},      # forwardExtremumSlip
    {"low": 0.5, "high": 2.0},      # forwardExtremumValue
    {"low": 0.5, "high": 2.0},      # forwardAsymptoteSlip
    {"low": 0.3, "high": 1.5},      # forwardAsymptoteValue
    {"low": 0.5, "high": 3.0},      # forwardStiffness
    {"low": 400, "high": 2000}      # carMass
]
