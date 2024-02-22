import logging
from two_nodes.application import GateProgram, InputProgram
from netsquid_netbuilder.util.network_generation import create_simple_network

from squidasm.run.stack.run import run
from utils.utils import calculate_reference_state, get_info

def run_simulation(input, gate, num_times = 1, device = "generic", link_fidelity: float = 1.0, qdevice_noise: float = 0.0, log = False):

    node_names = ["Gate", "Input"]
    cfg = create_simple_network(node_names=node_names, 
                                link_noise= 1 - link_fidelity*4 / 3, 
                                qdevice_noise=qdevice_noise)

    gate_program = GateProgram(gate)
    input_program = InputProgram(input)

    if log:
        gate_program.logger.setLevel(logging.INFO)
        input_program.logger.setLevel(logging.INFO)
    
    results = {"fidelity": 0,
               "trace_distance": 0 }

    for _ in range(num_times):
        gate_result = run(
            config = cfg,
            programs = {"Input": input_program, "Gate": gate_program})
        #print(gate_result)

        reference_state = calculate_reference_state(input, gate)
        qinfo = get_info(gate_result[0], reference_state)
        results["fidelity"] += qinfo["fidelity"]
        results["trace_distance"] += qinfo["trace_distance"]
        #results["relative_entropy"] += qinfo["relative_entropy"]
    
    results["fidelity"] /= num_times
    results["trace_distance"] /= num_times
    #results["relative_entropy"] /= num_times
    
    return results