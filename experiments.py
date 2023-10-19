import numpy as np
from run_simulation import run_simulation


gates = ["cnot", "dcnot", "cz", "swap"]
input = {
        "first_qubit": [],
        "second_qubit": ["H"],
    }
results = {}

link_fidelity_list = np.arange(0.5, 1.0, step=0.05)

for fidelity in link_fidelity_list:
    fidelity_results = {}
    for gate in gates:
        fidelity_results[gate] = run_simulation(input, gate, fidelity = fidelity)
    results[fidelity] = fidelity_results
    
print(results)