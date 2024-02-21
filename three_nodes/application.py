import logging
from utils.utils import apply_gate, get_correction_operator
from squidasm.util import get_qubit_state

from netqasm.sdk import Qubit

from squidasm.sim.stack.common import LogManager
from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta


class LeftProgram(Program):
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
        #epr2 = epr_socket.create_keep()[0]

        yield from connection.flush()
        
        self.logger.info("Initializing two input qubits...")
        input = Qubit(connection)
        
        for gate in self.gates:
            apply_gate(input, gate)
        
        yield from connection.flush()
        yield from csocket.recv()

        self.logger.info("Prepare Bell measurement...")
        
        input.cnot(epr)
        #epr2.cnot(input2)
        input.H()
        #epr2.H()
        
        self.logger.info("Measure...")
        
        epr_meas = epr.measure()
        #epr2_meas = epr2.measure()
        input_meas = input.measure()
        
        yield from connection.flush()

        result = str((int(epr_meas), int(input_meas)))
        csocket.send(result)

        yield from connection.flush()

        csocket.send("ACK")
        
        
class RightProgram(Program):
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
        #epr = epr_socket.create_keep()[0]
        epr2 = epr_socket.create_keep()[0]

        yield from connection.flush()
        
        self.logger.info("Initializing two input qubits...")
        input = Qubit(connection)
        
        for gate in self.gates:
            apply_gate(input, gate)
        
        yield from connection.flush()
        yield from csocket.recv()

        self.logger.info("Prepare Bell measurement...")
        
        #input1.cnot(epr)
        epr2.cnot(input)
        epr2.H()
        
        self.logger.info("Measure...")
        
        #epr_meas = epr.measure()
        epr2_meas = epr2.measure()
        input_meas = input.measure()
        
        yield from connection.flush()

        result = str((int(epr2_meas), int(input_meas)))
        csocket.send(result)

        yield from connection.flush()

        csocket.send("ACK")


class GateProgram(Program):
    PEER_NAME1 = "Left"
    PEER_NAME2 = "Right"

    def __init__(self, gate_name):
        self.logger = LogManager.get_stack_logger(self.__class__.__name__)
        self.gate_name = gate_name.lower()
        self.correction_operator = get_correction_operator(gate_name)
        

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name = "circuit_knitting",
            csockets = [self.PEER_NAME1, self.PEER_NAME2],
            epr_sockets = [self.PEER_NAME1, self.PEER_NAME2],
            max_qubits = 2,
        )

    def run(self, context: ProgramContext):
        csocket_left = context.csockets[self.PEER_NAME1]
        csocket_right = context.csockets[self.PEER_NAME2]
        epr_socket_left = context.epr_sockets[self.PEER_NAME1]
        epr_socket_right = context.epr_sockets[self.PEER_NAME2]
        connection = context.connection

        self.logger.info("Receiving EPR pairs from input circuits...")
        epr = epr_socket_left.recv_keep()[0]
        epr2 = epr_socket_right.recv_keep()[0]
        
        match self.gate_name:
            case "cnot" | "cx" | "xor":
                self.logger.info("Doing CNOT gate...")
                epr2.cnot(epr)
            case "cz":
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

        csocket_left.send("")
        csocket_right.send("")

        pauli_string_left = yield from csocket_left.recv()
        pauli_string_right = yield from csocket_right.recv()
        self.logger.info(f"Pauli string left = {pauli_string_left}")
        self.logger.info(f"Pauli string right = {pauli_string_right}")
        self.logger.info(f"Correction operator = {self.correction_operator}")
        
        epr1_meas, input1_meas = eval(pauli_string_left)
        epr2_meas, input2_meas = eval(pauli_string_right)
        
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

        msg = yield from csocket_left.recv()
        assert msg == "ACK"
        self.logger.info("Received ACK")

        final_dm = get_qubit_state(epr, "Gate", full_state=True)

        return final_dm
        