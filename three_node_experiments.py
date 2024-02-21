from three_nodes.run_simulation import run_simulation

gates = ["cnot", "dcnot", "cz", "swap"]
left = ["H"]
right = ["H"]

gate = "cnot"
run_simulation(left, right, gate, log=True)