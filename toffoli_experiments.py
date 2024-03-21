import json
import os
from toffoli.run_simulation import run_simulation
from utils.utils import NumpyArrayEncoder

left = ["H"]
middle = ["H"]
right = ["H"]

# Combinations for
# [1.0-1e-1, 1.0-1e-2, 1.0-1e-3, 1.0-1e-4, 1.0-1e-5, 1.0-1e-6, 1.0-1e-7, 1.0-1e-8, 1.0]

link_fidelity_list1 = [1.0]
link_fidelity_list2 = [1.0]
i = 1

if True:
    
    file_path = "results//link_fidelity_results_toffoli.json"

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
        
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        results = {}
    else:
        # Read existing data from the file
        with open(file_path, "r") as file:
            results = json.load(file)

    for fidelity in link_fidelity_list1:
        if str(fidelity) in results:
            fidelity_results = results[str(fidelity)]
        else:
            fidelity_results = {}
        for epr_prob in link_fidelity_list2:
            print(i / (len(link_fidelity_list1)*len(link_fidelity_list2)))
            i += 1
            if str(epr_prob) in fidelity_results:
                epr_results = fidelity_results[str(epr_prob)]
            else:
                epr_results = {}
            link_noises = {("Left", "Gate"): fidelity, ("Middle", "Gate"): fidelity, ("Right", "Gate"): epr_prob}
            prob_successes = {("Left", "Gate"): 1, ("Middle", "Gate"):1, ("Right", "Gate"): 1}
            qdevice_noises = {"Left": 0, "Middle": 0, "Right": 0, "Gate": 0}
            epr_results = run_simulation(left, right, middle, 
                                            link_noises = link_noises, 
                                            num_times = 100, 
                                            prob_successes = prob_successes, 
                                            qdevice_noises = qdevice_noises,
                                            log = True)
            fidelity_results[str(epr_prob)] = epr_results
        results[str(fidelity)] = fidelity_results

    open(file_path, "w").write(json.dumps(results, indent = 4, cls = NumpyArrayEncoder))

if False:
    file_path = "results//qdevice_noise_results_3.json"

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    
    results = {}
    
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        results = {}
    else:
        # Read existing data from the file
        with open(file_path, "r") as file:
            print("Reading existing data from the file")
            results = json.load(file)
            
    # Options
    # [0+1e-1, 0+1e-2, 0+1e-3, 0+1e-4, 0+1e-5, 0+1e-6, 0+1e-7, 0+1e-8, 0]
    
    qdevice_noise_list1 = [0+1e-1, 0+1e-2, 0+1e-3]
    qdevice_noise_list2 = [0+1e-1, 0+1e-2, 0+1e-3]
    i = 1
    
    for noise1 in qdevice_noise_list1:
        if str(noise1) in results:
            noise_results = results[str(noise1)]
        else:
            noise_results = {}
        for noise2 in qdevice_noise_list2:
            if str(noise2) in noise_results:
                gate_results = noise_results[str(noise2)]
            else:
                gate_results = {}
            print(i / (len(qdevice_noise_list1)*len(qdevice_noise_list2)))
            i += 1
            for gate in gates:
                print(gate)
                link_noises = {("Left", "Gate"): 1, ("Right", "Gate"): 1}
                prob_successes = {("Left", "Gate"): 1, ("Right", "Gate"): 1}
                qdevice_noises = {"Left": 0.0, "Right": noise2, "Gate": noise1}
                gate_results[gate] = run_simulation(left, right, gate,
                                                    link_noises = link_noises, 
                                                    num_times = 100, 
                                                    prob_successes = prob_successes, 
                                                    qdevice_noises = qdevice_noises)
            noise_results[str(noise2)] = gate_results
        results[str(noise1)] = noise_results
        
    open(file_path, "w").write(json.dumps(results, indent = 4, cls = NumpyArrayEncoder))