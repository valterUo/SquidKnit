import logging

from three_nodes.application import LeftProgram, RightProgram, GateProgram
from utils.network_generation import create_simple_network

from squidasm.run.stack.run import run
from utils.utils import calculate_reference_state, get_info

def run_simulation(left, right, gate, num_times = 1, prob_successes = {}, link_noises = {}, qdevice_noises = {}, log = False):
    
    cfg = create_simple_network(node_names = ["Left", "Right", "Gate"],
                                link_names = [("Left", "Gate"), ("Right", "Gate")],
                                link_noises = link_noises,
                                qdevice_noises = qdevice_noises,
                                prob_successes = prob_successes)

    gate_program = GateProgram(gate)
    left_program = LeftProgram(left)
    right_program = RightProgram(right)

    if log:
        gate_program.logger.setLevel(logging.INFO)
        left_program.logger.setLevel(logging.INFO)
        right_program.logger.setLevel(logging.INFO)
        
    results = {"fidelity": 0,
               "trace_distance": 0 }
    
    input_gates = {"first_qubit": left, "second_qubit": right}
    reference_state = calculate_reference_state(input_gates, gate)

    #gc.collect()
    for _ in range(num_times):
        gate_result = run(
            config = cfg,
            programs = {"Left": left_program, "Right": right_program, "Gate": gate_program})

        qinfo = get_info(gate_result[-1], reference_state)
        results["fidelity"] += qinfo["fidelity"]
        results["trace_distance"] += qinfo["trace_distance"]
        #results["relative_entropy"] += qinfo["relative_entropy"]
    
    results["fidelity"] /= num_times
    results["trace_distance"] /= num_times
    #results["relative_entropy"] /= num_times
    
    return results