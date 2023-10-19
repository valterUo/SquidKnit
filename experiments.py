import json
import numpy as np
from run_simulation import run_simulation

class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, complex):
            return (obj.real, obj.imag)
        return json.JSONEncoder.default(self, obj)


gates = ["cnot", "dcnot", "cz", "swap"]
input = {"first_qubit": [], "second_qubit": ["H"]}
results = {}

link_fidelity_list = np.arange(0.5, 1.0, step=0.05)

for fidelity in link_fidelity_list:
    fidelity_results = {}
    for gate in gates:
        fidelity_results[gate] = run_simulation(input, gate, link_fidelity = fidelity, num_times = 100)
    results[fidelity] = fidelity_results

open("results.json", "w").write(json.dumps(results, indent = 4, cls=NumpyArrayEncoder))