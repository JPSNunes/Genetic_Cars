import pygad
import numpy as np

from genome import NUM_GENES, GENE_SPACE, GENE_NAMES
from fitness import fitness_func
from ga_config import GA_PARAMS
from io_utils import save_population


def on_generation(ga):
    print(
        f"Gen {ga.generations_completed} | "
        f"Best fitness: {ga.best_solution()[1]:.2f}"
    )


ga = pygad.GA(
    num_genes=NUM_GENES,
    gene_space=GENE_SPACE,
    gene_type=float,
    fitness_func=fitness_func,
    on_generation=on_generation,
    **GA_PARAMS
)

ga.run()

#best solution
solution, fitness, _ = ga.best_solution()

print("\n=== BEST SOLUTION ===")
for name, value in zip(GENE_NAMES, solution):
    print(f"{name}: {value:.3f}")
print("Fitness:", fitness)

#save final populations
save_population(ga.population)
print("\nPopulation saved to population.json")
