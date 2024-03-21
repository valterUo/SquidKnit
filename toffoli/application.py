import logging
from utils.utils import apply_gate, get_correction_operator
from squidasm.util import get_qubit_state
from toffoli.corrections import *

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

        yield from connection.flush()
        
        self.logger.info("Initializing input qubit...")
        input = Qubit(connection)
        
        input.H()
        self.logger.info("H gate applied to input in LeftProgram")
        #for gate in self.gates:
        #    apply_gate(input, gate)
        
        yield from connection.flush()
        yield from csocket.recv()

        self.logger.info("Prepare Bell measurement...")
        
        input.cnot(epr)
        input.H()
        
        self.logger.info("Measure...")
        
        epr_meas = epr.measure()
        input_meas = input.measure()
        
        yield from connection.flush()

        result = str((int(epr_meas), int(input_meas)))
        csocket.send(result)

        yield from connection.flush()

        csocket.send("ACK")


class MiddleProgram(Program):
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

        yield from connection.flush()
        
        self.logger.info("Initializing input qubit...")
        input = Qubit(connection)
        
        input.H()
        self.logger.info("H gate applied to input in MiddleProgram")
        #for gate in self.gates:
        #    apply_gate(input, gate)
        
        yield from connection.flush()
        yield from csocket.recv()

        self.logger.info("Prepare Bell measurement...")
        
        input.cnot(epr)
        input.H()
        
        self.logger.info("Measure...")
        
        epr_meas = epr.measure()
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
        epr = epr_socket.create_keep()[0]

        yield from connection.flush()
        
        self.logger.info("Initializing two input qubits...")
        input = Qubit(connection)
        
        input.H()
        self.logger.info("H gate applied to input in RightProgram")
        #for gate in self.gates:
        #    apply_gate(input, gate)
        
        yield from connection.flush()
        yield from csocket.recv()

        self.logger.info("Prepare Bell measurement...")
        
        #input1.cnot(epr)
        input.cnot(epr)
        input.H()
        
        self.logger.info("Measure...")
        
        #epr_meas = epr.measure()
        epr_meas = epr.measure()
        input_meas = input.measure()
        
        yield from connection.flush()

        result = str((int(epr_meas), int(input_meas)))
        csocket.send(result)

        yield from connection.flush()

        csocket.send("ACK")


class GateProgram(Program):
    PEER_NAME1 = "Left"
    PEER_NAME2 = "Right"
    PEER_NAME3 = "Middle"

    def __init__(self):
        self.logger = LogManager.get_stack_logger(self.__class__.__name__)
        

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name = "circuit_knitting",
            csockets = [self.PEER_NAME1, self.PEER_NAME2, self.PEER_NAME3],
            epr_sockets = [self.PEER_NAME1, self.PEER_NAME2, self.PEER_NAME3],
            max_qubits = 4,
        )

    def run(self, context: ProgramContext):
        csocket_left = context.csockets[self.PEER_NAME1]
        csocket_middle = context.csockets[self.PEER_NAME3]
        csocket_right = context.csockets[self.PEER_NAME2]
        
        epr_socket_left = context.epr_sockets[self.PEER_NAME1]
        epr_socket_middle = context.epr_sockets[self.PEER_NAME3]
        epr_socket_right = context.epr_sockets[self.PEER_NAME2]
        
        connection = context.connection

        self.logger.info("Receiving EPR pairs from input circuits...")
        epr1 = epr_socket_left.recv_keep()[0]
        epr2 = epr_socket_middle.recv_keep()[0]
        epr3 = epr_socket_right.recv_keep()[0]
        
        # Apply Toffoli gate to the epr qubits
        self.logger.info("Apply Toffoli gate")
        toffoli(epr1, epr2, epr3)
        self.logger.info("Toffoli gate applied to epr qubits")

        yield from connection.flush()
        self.logger.info("Initialized target qubits")

        csocket_left.send("")
        csocket_middle.send("")
        csocket_right.send("")

        pauli_string_left = yield from csocket_left.recv()
        pauli_string_middle = yield from csocket_middle.recv()
        pauli_string_right = yield from csocket_right.recv()
        
        self.logger.info(f"Pauli string left = {pauli_string_left}")
        self.logger.info(f"Pauli string middle = {pauli_string_middle}")
        self.logger.info(f"Pauli string right = {pauli_string_right}")
        
        
        epr1_meas, input1_meas = eval(pauli_string_left)
        epr2_meas, input2_meas = eval(pauli_string_middle)
        epr3_meas, input3_meas = eval(pauli_string_right)
        
        if input1_meas == 1:
            correction1(epr1, epr2, epr3)
        if input2_meas == 1:
            correction2(epr1, epr2, epr3)
        if input3_meas == 1:
            correction3(epr1, epr2, epr3)
        if epr1_meas == 1:
            correction4(epr1, epr2, epr3)
        if epr2_meas == 1:
            correction5(epr1, epr2, epr3)
        if epr3_meas == 1:
            correction6(epr1, epr2, epr3)
        
                    
        self.logger.info("Correction operators applied")

        yield from connection.flush()

        msg = yield from csocket_left.recv()
        assert msg == "ACK"
        self.logger.info("Received ACK")

        final_dm = get_qubit_state(epr1, "Gate", full_state=True)

        return final_dm