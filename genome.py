# genome.py

NUM_GENES = 10

GENE_NAMES = [
    # --- Body ---
    "carWidth",       # genome[0]
    "carHeight",      # genome[1]
    "carLength",      # genome[2]
    "carMass",        # genome[3]

    # --- Wheel & Suspension ---
    "wheelWidth",         # genome[4]
    "wheelRadius",        # genome[5]
    "wheelMass",          # genome[6]
    "suspensionTravel",   # genome[7]
    "suspensionHardness", # genome[8]
    "suspensionDamping"   # genome[9]
]

GENE_SPACE = [
    # --- Body ranges ---
    {"low": 0.5, "high": 3.0},   # carWidth
    {"low": 0.2, "high": 2.0},   # carHeight
    {"low": 0.4, "high": 2.0},   # carLength
    {"low": 400, "high": 3000},  # carMass

    # --- Wheel & Suspension ranges ---
    {"low": 0.20, "high": 1},     # wheelWidth
    {"low": 0.10, "high": 1},     # wheelRadius
    {"low": 10, "high": 80.0},     # wheelMass
    {"low": 0.01, "high": 0.8},     # suspensionTravel
    {"low": 2000, "high": 120000},  # suspensionHardness
    {"low": 200, "high": 30000}     # suspensionDamping
]
