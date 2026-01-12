def fitness_func(ga_instance, solution, solution_idx):
    """
    solution: array com os genes (ex: wheel_size, density, etc.)
    solution_idx: índice na população (ignorar)
    ga_instance: instância do GA (ignorar)
    """
    fitness = sum(solution)
    return fitness
