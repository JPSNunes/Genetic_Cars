# io_utils.py
import json
import numpy as np
from pathlib import Path

def save_population(population, filename="population.json"):
    data = {
        "individuals": [
            {
                "id": i,
                "genome": np.array(ind).tolist()
            }
            for i, ind in enumerate(population)
        ]
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def save_outgoing_messages(generation, population, folder="outgoing", current_filename="out_gen_current.json"):
    Path(folder).mkdir(parents=True, exist_ok=True)
    msgs = []
    for i, ind in enumerate(population):
        msgs.append({
            "type": "evaluate",
            "generation": int(generation),
            "id": int(i),
            "genes": [float(x) for x in np.array(ind).tolist()]
        })
    filename = Path(folder) / current_filename
    # atomic write pattern: write tmp then rename
    tmp = filename.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(msgs, f, indent=2)
    tmp.replace(filename)
    return str(filename)
