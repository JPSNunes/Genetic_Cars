# io_utils.py
import json
import numpy as np
from pathlib import Path

def save_population(population, filename="population.json"):
    """
    Generic population snapshot (not protocol-specific).
    """
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


def save_outgoing_messages(
    generation,
    population,
    folder="outgoing",
    current_filename="out_gen_current.json"
):
    """
    Saves the EXACT evaluate_batch message that is sent to Unity.
    """
    Path(folder).mkdir(parents=True, exist_ok=True)

    batch_msg = {
        "type": "evaluate_batch",
        "generation": int(generation),
        "population_size": len(population),
        "individuals": [
            {
                "id": int(i),
                "genes": [float(x) for x in np.array(ind).tolist()]
            }
            for i, ind in enumerate(population)
        ]
    }

    filename = Path(folder) / current_filename

    # atomic write pattern
    tmp = filename.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(batch_msg, f, indent=2)
    tmp.replace(filename)

    return str(filename)
