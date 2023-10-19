from netqasm.sdk import Qubit

from utils import apply_gate, get_correction_operator

from squidasm.sim.stack.common import LogManager
from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta
from squidasm.util import get_qubit_state


class InputProgram(Program):
    PEER_NAME = "Gate"

    def __init__(self, gates):
        self.logger = LogManager.get_stack_logger(self.__class__.__name__)
        self.gates = gates
        
    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name = "circuit_knitting",
            csockets = [self.PEER_NAME],
            epr_sockets = [self.PEER_NAME],
            max_qubits = 4,
        )

    def run(self, context: ProgramContext):
        csocket = context.csockets[self.PEER_NAME]
        epr_socket = context.epr_sockets[self.PEER_NAME]
        connection = context.connection

        self.logger.info("Creating EPR pairs...")
        epr = epr_socket.create_keep()[0]
        epr2 = epr_socket.create_keep()[0]

        yield from connection.flush()
        
        self.logger.info("Initializing two input qubits...")
        input1 = Qubit(connection)
        input2 = Qubit(connection)
        
        for gate in self.gates["first_qubit"]:
            apply_gate(input1, gate)
        for gate in self.gates["second_qubit"]:
            apply_gate(input2, gate)
        
        yield from connection.flush()
        yield from csocket.recv()

        self.logger.info("Prepare Bell measurement...")
        
        input1.cnot(epr)
        epr2.cnot(input2)
        input1.H()
        epr2.H()
        
        self.logger.info("Measure...")
        
        epr_meas = epr.measure()
        epr2_meas = epr2.measure()
        input1_meas = input1.measure()
        input2_meas = input2.measure()
        
        yield from connection.flush()

        result = str((int(epr_meas), int(epr2_meas), int(input2_meas), int(input1_meas)))
        csocket.send(result)

        yield from connection.flush()

        csocket.send("ACK")

        #return {
        #    "epr_meas": int(epr_meas),
        #    "epr2_meas": int(epr2_meas),
        #    "input1_meas": int(input1_meas),
        #    "input2_meas": int(input2_meas) }


class GateProgram(Program):
    PEER_NAME = "Input"

    def __init__(self, gate_name):
        self.logger = LogManager.get_stack_logger(self.__class__.__name__)
        self.gate_name = gate_name.lower()
        self.correction_operator = get_correction_operator(gate_name)
        

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name = "circuit_knitting",
            csockets = [self.PEER_NAME],
            epr_sockets = [self.PEER_NAME],
            max_qubits = 2,
        )

    def run(self, context: ProgramContext):
        csocket = context.csockets[self.PEER_NAME]
        epr_socket = context.epr_sockets[self.PEER_NAME]
        connection = context.connection

        self.logger.info("Receiving EPR pair from input circuit...")
        epr = epr_socket.recv_keep()[0]
        epr2 = epr_socket.recv_keep()[0]
        
        match self.gate_name:
            case "cnot" | "cx" | "xor":
                self.logger.info("Doing CNOT gate...")
                epr2.cnot(epr)
            case "CZ" | "cz":
                self.logger.info("Doing CZ gate...")
                epr2.cphase(epr)
            case "dcnot":
                self.logger.info("Doing DCNOT gate...")
                epr2.cnot(epr)
                epr.cnot(epr2)
            case "swap":
                self.logger.info("Doing SWAP gate...")
                epr2.cnot(epr)
                epr.cnot(epr2)
                epr2.cnot(epr)

        yield from connection.flush()
        self.logger.info("Initialized target qubit")

        csocket.send("")

        pauli_string = yield from csocket.recv()
        print(f"Pauli string = {pauli_string}")
        print(f"Correction operator = {self.correction_operator}")
        
        epr1_meas, epr2_meas, input2_meas, input1_meas = eval(pauli_string)
        
        for meas, operator in zip([input2_meas, epr2_meas, epr1_meas, input1_meas], self.correction_operator):
            if meas == 1:
                if operator[0] == "PauliX":
                    epr2.X()
                elif operator[0] == "PauliZ":
                    epr2.Z()
                if operator[1] == "PauliX":
                    epr.X()
                elif operator[1] == "PauliZ":
                    epr.Z()
                    
        self.logger.info("Correction operator applied")

        yield from connection.flush()

        msg = yield from csocket.recv()
        assert msg == "ACK"
        self.logger.info("Received ACK")

        final_dm = get_qubit_state(epr, "Gate", full_state=True)

        return final_dm