    
import logging
from application import GateProgram, InputProgram
from config import create_two_node_network

from squidasm.run.stack.run import run
from utils import calculate_reference_state, get_info

def run_simulation(input, gate, num_times = 1, device = "generic", link_fidelity: float = 1.0, qdevice_noise: float = 0.0):

    node_names = ["Gate", "Input"]
    cfg = create_two_node_network(node_names, device, link_fidelity, qdevice_noise)

    gate_program = GateProgram(gate)
    input_program = InputProgram(input)

    #gate_program.logger.setLevel(logging.INFO)
    #input_program.logger.setLevel(logging.INFO)
    
    results = {"fidelity": 0,
               "trace_distance": 0 }

    for _ in range(num_times):
        gate_result = run(
            config = cfg,
            programs = {"Input": input_program, "Gate": gate_program})

        reference_state = calculate_reference_state(input, gate)
        qinfo = get_info(gate_result[0], reference_state)
        results["fidelity"] += qinfo["fidelity"]
        results["trace_distance"] += qinfo["trace_distance"]
        #results["relative_entropy"] += qinfo["relative_entropy"]
    
    results["fidelity"] /= num_times
    results["trace_distance"] /= num_times
    #results["relative_entropy"] /= num_times
    
    return results