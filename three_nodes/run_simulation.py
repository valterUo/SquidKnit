import logging

from networkx import DiGraph
from three_nodes.application import LeftProgram, RightProgram, GateProgram
from three_nodes.network_generation import create_network_from_graph
from two_nodes.config import create_two_node_network
from netsquid_netbuilder.util.network_generation import create_simple_network

from squidasm.run.stack.run import run
from utils.utils import calculate_reference_state, get_info

def run_simulation(left, right, gate, num_times = 1, device = "generic", link_fidelity: float = 1.0, qdevice_noise: float = 0.0, log = False):

    node_names = ["Gate", "Left", "Right"]
    
    graph = DiGraph()
    graph.add_nodes_from(node_names)
    graph.add_edges_from([("Gate", "Left"), ("Gate", "Right")])
    
    cfg = create_simple_network(["Left", "Right", "Gate"]) #create_network_from_graph(graph) #create_two_node_network(node_names, device, link_fidelity, qdevice_noise)

    gate_program = GateProgram(gate)
    left_program = LeftProgram(left)
    right_program = RightProgram(right)

    if log:
        gate_program.logger.setLevel(logging.INFO)
        left_program.logger.setLevel(logging.INFO)
        right_program.logger.setLevel(logging.INFO)

    gate_result = run(
        config = cfg,
        programs = {"Left": left_program, "Right": right_program, "Gate": gate_program})
    print(gate_result)
    
    input_gates = {"first_qubit": left, "second_qubit": right}
    reference_state = calculate_reference_state(input_gates, gate)
    print(reference_state)
    qinfo = get_info(gate_result[-1], reference_state)
    print(qinfo)
    return qinfo