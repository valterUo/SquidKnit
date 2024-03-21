import json
import numpy as np
import os
from two_nodes.run_simulation import run_simulation
from utils.utils import NumpyArrayEncoder

gates = ["cnot", "dcnot", "cz", "swap"]
input = {"first_qubit": ["H"], "second_qubit": ["H"]}

if False:
    results = {}
    file_path = "results//link_fidelity_results_2.json"

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        results = {}
    else:
        # Read existing data from the file
        with open(file_path, "r") as file:
            print("Reading existing data from the file")
            results = json.load(file)
            
    #0.9, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 1.0
    link_fidelity_list = np.linspace(0.99, 1.0, num=10)
    i = 1
    for fidelity in link_fidelity_list:
        print((i / len(link_fidelity_list))*100)
        fidelity_results = {}
        for gate in gates:
            fidelity_results[gate] = run_simulation(input, gate, link_fidelity = fidelity, num_times = 100)
        results[fidelity] = fidelity_results
        i += 1

    open(file_path, "w").write(json.dumps(results, indent = 4, cls = NumpyArrayEncoder))

if True:
    # 0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1
    qdevice_noise_list = np.linspace(0.06, 0.07, num=10)
    i = 1
    results = {}
    file_path = "results//qdevice_noise_results_2.json"

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        results = {}
    else:
        # Read existing data from the file
        with open(file_path, "r") as file:
            print("Reading existing data from the file")
            results = json.load(file)

    for noise in qdevice_noise_list:
        print((i / len(qdevice_noise_list))*100)
        noise_results = {}
        for gate in gates:
            noise_results[gate] = run_simulation(input, gate, qdevice_noise = noise, num_times = 100)
        results[noise] = noise_results
        i += 1
        
    open(file_path, "w").write(json.dumps(results, indent = 4, cls = NumpyArrayEncoder))