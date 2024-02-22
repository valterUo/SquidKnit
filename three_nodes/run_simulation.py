import logging

from networkx import DiGraph
from three_nodes.application import LeftProgram, RightProgram, GateProgram
from two_nodes.config import create_two_node_network
from netsquid_netbuilder.util.network_generation import create_simple_network

from squidasm.run.stack.run import run
from utils.utils import calculate_reference_state, get_info

def run_simulation(left, right, gate, num_times = 1, device = "generic", link_fidelity: float = 1.0, qdevice_noise: float = 0.0, log = False):

    node_names = ["Gate", "Left", "Right"]
    
    graph = DiGraph()
    graph.add_nodes_from(node_names)
    graph.add_edges_from([("Gate", "Left"), ("Gate", "Right")])
    
    cfg = create_simple_network(["Left", "Right", "Gate"], link_noise = 1 - link_fidelity*4 / 3, qdevice_noise = qdevice_noise) #create_network_from_graph(graph) #create_two_node_network(node_names, device, link_fidelity, qdevice_noise)

    gate_program = GateProgram(gate)
    left_program = LeftProgram(left)
    right_program = RightProgram(right)

    if log:
        gate_program.logger.setLevel(logging.INFO)
        left_program.logger.setLevel(logging.INFO)
        right_program.logger.setLevel(logging.INFO)
        
    results = {"fidelity": 0,
               "trace_distance": 0 }

    for _ in range(num_times):
        gate_result = run(
            config = cfg,
            programs = {"Left": left_program, "Right": right_program, "Gate": gate_program})
        #print(gate_result)

        input_gates = {"first_qubit": left, "second_qubit": right}
        reference_state = calculate_reference_state(input_gates, gate)
        qinfo = get_info(gate_result[-1], reference_state)
        results["fidelity"] += qinfo["fidelity"]
        results["trace_distance"] += qinfo["trace_distance"]
        #results["relative_entropy"] += qinfo["relative_entropy"]
    
    results["fidelity"] /= num_times
    results["trace_distance"] /= num_times
    #results["relative_entropy"] /= num_times
    
    return results