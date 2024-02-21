import pennylane as qml
import numpy as np

def get_correction_operator(gate_name):
    
    match gate_name:
        case "cnot" | "cx" | "xor":
            gate = qml.CNOT
            U_matrix = np.array(gate.compute_matrix())
            U_adjoint = np.array(qml.adjoint(gate).compute_matrix())
        case "CZ" | "cz":
            gate = qml.CZ
            U_matrix = np.array(gate.compute_matrix())
            U_adjoint = np.array(qml.adjoint(gate).compute_matrix())
        case "dcnot":
            U_matrix = np.array([[1, 0, 0, 0],
                              [0, 0, 1, 0],
                              [0, 0, 0, 1],
                              [0, 1, 0, 0]])
            U_adjoint = np.transpose(U_matrix)
        case "swap":
            gate = qml.SWAP
            U_matrix = np.array(gate.compute_matrix())
            U_adjoint = np.array(qml.adjoint(gate).compute_matrix())

    Z = np.array(qml.PauliZ.compute_matrix())
    X = np.array(qml.PauliX.compute_matrix())
    I = np.identity(2)
    basis = [np.kron(X, I), np.kron(Z, I), np.kron(I, X), np.kron(I, Z)]
    correction_operator = []

    for base in basis:
        result = np.matmul(U_matrix, base)
        result = np.matmul(result, U_adjoint)
        result = qml.pauli.pauli_decompose(result, wire_order=[0,1])
        
        for r in result.ops:
            r1, r2 = r.obs[0].name, r.obs[1].name
            correction_operator.append((r1, r2))

    return correction_operator

def apply_gate(input, gate):
    match gate:
        case "H":
            input.H()
        case "X":
            input.X()
        case "Y":
            input.Y()
        case "Z":
            input.Z()
        case "S":
            input.S()
        case "T":
            input.T()
            
def apply_pennylane_gate(input, gate):
    match gate:
        case "H":
            qml.Hadamard(wires = input)
        case "X":
            qml.PauliX(wires = input)
        case "Y":
            qml.PauliY(wires = input)
        case "Z":
            qml.PauliZ(wires = input)
        case "S":
            qml.S(wires = input)
        case "T":
            qml.T(wires = input)
    
    
@qml.qnode(qml.device("default.qubit", wires = 2))       
def calculate_reference_state(input, gate):
        
    for input_gate in input["first_qubit"]:
        apply_pennylane_gate([0], input_gate)
    
    for input_gate in input["second_qubit"]:
        apply_pennylane_gate([1], input_gate)
    
    match gate.lower():
        case "cnot" | "cx" | "xor":
            qml.CNOT(wires = [1, 0])
        case "cz":
            qml.CZ(wires = [1, 0])
        case "dcnot":
            qml.CNOT(wires = [1, 0])
            qml.CNOT(wires = [0, 1])
        case "swap":
            qml.SWAP(wires = [1, 0])
    return qml.density_matrix(wires = [1, 0])


def get_info(density_matrix1, density_matrix2):
    info = {}
    
    dev = qml.device("default.mixed", wires = 2)
    @qml.qnode(dev)
    def circuit1():
        qml.QubitDensityMatrix(density_matrix1, wires=[0, 1])
        return qml.density_matrix(wires=[0, 1])
    
    @qml.qnode(dev)
    def circuit2():
        qml.QubitDensityMatrix(density_matrix2, wires=[0, 1])
        return qml.density_matrix(wires=[0, 1])
    
    input = (circuit1, circuit2, [0, 1], [0, 1])
    info["fidelity"] = qml.qinfo.fidelity(*input)()
    info["trace_distance"] = qml.qinfo.trace_distance(*input)()
    #info["relative_entropy"] = qml.qinfo.relative_entropy(*input)()
    
    return info