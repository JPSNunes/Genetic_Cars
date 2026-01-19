# evolution_controller.py
import time
import csv
import json
from pathlib import Path
import numpy as np
from ga_module import init_ga, run_single_generation, get_population, inject_fitness
from io_utils import save_outgoing_messages
from comm_unity import UnityComm

RESULTS_FOLDER = Path("results")
OUT_FOLDER = Path("outgoing")
INCOMING_FOLDER = Path("unity_incoming")
LOG_CSV = RESULTS_FOLDER / "metrics.csv"

def evaluate_population_with_unity(comm, generation, population, timeout_per_ind=10):
    pop_size = len(population)
    results = [None] * pop_size

    # save outgoing snapshot (overwrites out_gen_current.json)
    save_outgoing_messages(generation, population, folder=str(OUT_FOLDER))

    # build population payload: (id, genes)
    batch_population = [
        (i, ind.tolist())
        for i, ind in enumerate(population)
    ]

    # send whole batch in ONE message
    comm.send_evaluate_batch(generation, batch_population)

    received = 0
    start = time.time()
    INCOMING_FOLDER.mkdir(parents=True, exist_ok=True)

    while received < pop_size:
        data = comm.receive_result(timeout=timeout_per_ind)
        recv_time = time.time()

        gen_val = data.get("generation", generation)

        # --- batch result ---
        if data.get("type") == "results_batch":
            batch = data.get("results", [])

            fname_batch = INCOMING_FOLDER / f"gen{gen_val}_results_batch.json"
            with open(fname_batch, "w") as f:
                json.dump({"received_at": recv_time, "raw": data}, f, indent=2)

            for entry in batch:
                idx_val = int(entry.get("id", -1))
                fitness = entry.get("fitness", None)
                if fitness is None:
                    continue
                if results[idx_val] is None:
                    results[idx_val] = float(fitness)
                    received += 1
            continue

        # --- individual result ---
        if data.get("type") == "result":
            idx_val = int(data.get("id", -1))

            fname = INCOMING_FOLDER / f"gen{gen_val}_id{idx_val}.json"
            with open(fname, "w") as f:
                json.dump({"received_at": recv_time, "raw": data}, f, indent=2)

            if "generation" in data and data["generation"] != generation:
                print(
                    f"Ignoring result for gen {data['generation']} "
                    f"(expecting {generation}) id={idx_val}"
                )
                continue

            fitness = data.get("fitness", None)
            if fitness is not None and results[idx_val] is None:
                results[idx_val] = float(fitness)
                received += 1
            continue

        # --- unknown message ---
        fname_unknown = INCOMING_FOLDER / f"gen{gen_val}_unknown_{int(recv_time)}.json"
        with open(fname_unknown, "w") as f:
            json.dump({"received_at": recv_time, "raw": data}, f, indent=2)

        # safety timeout (optional but recommended)
        if time.time() - start > timeout_per_ind * pop_size:
            raise TimeoutError(
                f"Timeout waiting for Unity results "
                f"({received}/{pop_size} received)"
            )

    # save aggregated results
    RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FOLDER / f"gen_{generation}_results.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


def append_metrics_csv(generation, best, mean, std, duration):
    RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)
    header = ["generation", "best", "mean", "std", "duration_s"]
    write_header = not LOG_CSV.exists()
    with open(LOG_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        writer.writerow([generation, best, mean, std, round(duration, 4)])

def evolution_loop(unity_url="ws://localhost:8080", generations=10, timeout_per_ind=1000):
    ga = init_ga()
    comm = UnityComm(url=unity_url, timeout=timeout_per_ind, retries=2, retry_delay=1.0)
    comm.connect()
    try:
        for gen in range(generations):
            t0 = time.time()
            print(f"\n=== Generation {gen} ===")
            run_single_generation(ga)  # create or advance
            pop = get_population(ga)
            # evaluate via Unity (blocking until all results)
            fitness_list = evaluate_population_with_unity(comm, gen, pop, timeout_per_ind=timeout_per_ind)
            inject_fitness(ga, fitness_list)
            # compute metrics
            best = float(np.max(fitness_list))
            mean = float(np.mean(fitness_list))
            std = float(np.std(fitness_list))
            duration = time.time() - t0
            append_metrics_csv(gen, best, mean, std, duration)
            print(f"Gen {gen} metrics best {best:.4f} mean {mean:.4f} std {std:.4f} time {duration:.2f}s")
        # final best
        print("Best solution fitness:", ga.best_fitness)
        print("Best solution genome:", ga.best_solution)
    finally:
        comm.close()

if __name__ == "__main__":
    evolution_loop(generations=10, timeout_per_ind=1000)
