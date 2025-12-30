import json

def save_population(population, filename="population.json"):
    data = {
        "individuals": [
            {
                "id": i,
                "genome": ind.tolist()
            }
            for i, ind in enumerate(population)
        ]
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
