    
import logging
from application import GateProgram, InputProgram
from config import create_two_node_network

from squidasm.run.stack.run import run
from utils import calculate_reference_state, get_info

def run_simulation(input, gate, device = "generic", link_fidelity: float = 0, qdevice_noise: float = 0):

    node_names = ["Gate", "Input"]
    cfg = create_two_node_network(node_names, device, link_fidelity, qdevice_noise)

    gate_program = GateProgram(gate)
    input_program = InputProgram(input)

    gate_program.logger.setLevel(logging.INFO)
    input_program.logger.setLevel(logging.INFO)

    gate_result = run(
        config=cfg,
        programs={"Input": input_program, "Gate": gate_program},
        num_times = 1,
    )

    reference_state = calculate_reference_state(input, gate)
    qinfo = get_info(gate_result[0], reference_state)
    
    return {
        "result": gate_result[0],
        "reference_state": reference_state,
        "qinfo": qinfo,
    }