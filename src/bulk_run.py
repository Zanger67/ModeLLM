from functools import partial

from simulation import Simulation
from multiprocessing import Pool

from itertools import permutations
from math import factorial
from random import shuffle

default_topic = "climate_change"
default_models = {
    "USA": "gpt-3.5-turbo",
    "China": "gpt-3.5-turbo",
    "EU": "gpt-3.5-turbo", 
    "India": "gpt-3.5-turbo",
}    

def run_sim(model, partial):
    partial(models=model).run()

def bulk_run(topic: str, models: dict[str, str], output_dir: str=None, sim_name: str="", k: int=-1):
    models_list = list(permutations(models.values(), len(models)))
    
    if k == -1:
        k = factorial(len(models))
        
    shuffle(models_list)
    models_list = models_list + models_list * (k // len(models_list))
    models_list = models_list[:k]
    
    models_dicts = [{k: v for k, v in zip(models.keys(), model)} for model in models_list]
    
    with Pool() as pool:
        partial_sim = partial(Simulation, topic=topic, output_dir=output_dir, sim_name=sim_name)
        pool.starmap(run_sim, zip(models_dicts, [partial_sim] * k))
        
if __name__ == "__main__":
    bulk_run(default_topic, default_models, sim_name="bulk_test")