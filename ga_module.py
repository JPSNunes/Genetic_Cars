import numpy as np
from genome import NUM_GENES, GENE_SPACE
from ga_config import GA_PARAMS

class SimpleGA:
    def __init__(self, params):
        if params.get("random_seed") is not None:
            np.random.seed(params["random_seed"])
        self.params = params
        self.pop_size = params["sol_per_pop"]
        self.num_genes = NUM_GENES
        self.gene_space = GENE_SPACE
        self.population = None            # shape (pop_size, num_genes)
        self.fitness = None               # last injected fitness (length pop_size)
        self.generation = 0
        self.best_solution = None
        self.best_fitness = -np.inf

    def _random_individual(self):
        ind = np.zeros(self.num_genes, dtype=float)
        for i, gs in enumerate(self.gene_space):
            low = gs["low"]
            high = gs["high"]
            ind[i] = np.random.uniform(low, high)
        return ind

    def create_initial_population(self):
        self.population = np.array([self._random_individual() for _ in range(self.pop_size)])
        self.fitness = None
        self.generation = 0

    def _tournament_select(self):
        k = self.params.get("tournament_k", 3)
        idxs = np.random.choice(self.pop_size, size=k, replace=False)
        best = idxs[0]
        for idx in idxs:
            if self.fitness is None:
                # if no fitness yet, pick random
                best = idxs[0]
                break
            if self.fitness[idx] > self.fitness[best]:
                best = idx
        return self.population[best].copy()

    def _uniform_crossover(self, p1, p2):
        mask = np.random.rand(self.num_genes) < 0.5
        child = np.where(mask, p1, p2)
        return child

    def _mutate(self, individual):
        pct = self.params.get("mutation_percent_genes", 20) / 100.0
        num_to_mutate = max(1, int(np.ceil(self.num_genes * pct)))
        idxs = np.random.choice(self.num_genes, size=num_to_mutate, replace=False)
        for i in idxs:
            gs = self.gene_space[i]
            individual[i] = np.random.uniform(gs["low"], gs["high"])
        return individual

    def _elitism(self, new_pop):
        k = int(self.params.get("keep_parents", 0))
        if k <= 0 or self.fitness is None:
            return new_pop
        # get top k indices from current population by fitness
        top_idxs = np.argsort(self.fitness)[-k:][::-1]
        elites = self.population[top_idxs]
        # replace first k individuals in new_pop with elites
        new_pop[:k] = elites
        return new_pop

    def step_generation(self):
        """
        Advance one generation. Requires self.fitness to be set for the current population.
        If generation == 0 and population is None, create initial population and return (no evolution).
        """
        if self.population is None:
            self.create_initial_population()
            return

        if self.fitness is None:
            # waiting for external fitness to be injected
            return

        # update best
        gen_best_idx = np.argmax(self.fitness)
        gen_best_fit = self.fitness[gen_best_idx]
        if gen_best_fit > self.best_fitness:
            self.best_fitness = gen_best_fit
            self.best_solution = self.population[gen_best_idx].copy()

        # produce new population
        new_pop = np.zeros_like(self.population)
        # elitism will be applied after creating children
        num_children = self.pop_size
        for i in range(num_children):
            # select parents
            p1 = self._tournament_select()
            p2 = self._tournament_select()
            # crossover
            child = self._uniform_crossover(p1, p2)
            # mutation
            child = self._mutate(child)
            new_pop[i] = child

        # apply elitism
        new_pop = self._elitism(new_pop)

        # set new population and advance generation
        self.population = new_pop
        self.generation += 1
        # clear fitness until next injection
        self.fitness = None

# Module-level API (keeps your previous function names)
def init_ga():
    ga = SimpleGA(GA_PARAMS)
    return ga

def run_single_generation(ga):
    """
    Behavior:
    - If ga.population is None -> create initial population (generation 0)
    - Else if ga.fitness is None -> do nothing (waiting for external fitness)
    - Else -> use injected fitness to create next generation and increment generation
    """
    ga.step_generation()

def get_population(ga):
    return ga.population

def inject_fitness(ga, fitness_list):
    arr = np.array(fitness_list, dtype=float)
    if ga.population is None:
        raise RuntimeError("Population not created yet. Call run_single_generation(ga) first to create initial population.")
    if arr.shape[0] != ga.population.shape[0]:
        raise ValueError(f"Fitness length {arr.shape[0]} does not match population size {ga.population.shape[0]}")
    ga.fitness = arr
