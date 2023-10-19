import logging
from dataclasses import dataclass

import numpy
from netqasm.sdk import Qubit

from squidasm.sim.stack.common import LogManager
from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta


class LeftProgram(Program):
    PEER_NAME = "Middle"

    def __init__(self):
        self.logger = LogManager.get_stack_logger(self.__class__.__name__)

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name = "Left",
            csockets = [self.PEER_NAME],
            epr_sockets = [self.PEER_NAME],
            max_qubits = 2,
        )

    def run(self, context: ProgramContext):
        csocket = context.csockets[self.PEER_NAME]
        epr_socket = context.epr_sockets[self.PEER_NAME]
        connection = context.connection

        self.logger.info("Creating EPR pair with middle circuit...")
        epr = epr_socket.create_keep()[0]
        yield from connection.flush()
        self.logger.info("Initializing first input qubit...")
        input1_qubit = Qubit(connection)
        self.logger.info("Prepare Bell measurement...")
        input1_qubit.cnot(epr)
        input1_qubit.h()
        self.logger.info("Measure both...")
        epr_meas = epr.measure()
        input1_meas = input1_qubit.measure()
        yield from connection.flush()
        csocket.send((str(epr_meas), str(input1_meas)))
        
        return {
            "epr_measurement": int(epr_meas),
            "input_measurement": int(input1_meas)
        }
        
        
class RightProgram(Program):
    PEER_NAME = "Middle"

    def __init__(self):
        self.logger = LogManager.get_stack_logger(self.__class__.__name__)

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name = "Right",
            csockets = [self.PEER_NAME],
            epr_sockets = [self.PEER_NAME],
            max_qubits = 2,
        )

    def run(self, context: ProgramContext):
        csocket = context.csockets[self.PEER_NAME]
        epr_socket = context.epr_sockets[self.PEER_NAME]
        connection = context.connection

        self.logger.info("Creating EPR pair with middle circuit...")
        epr = epr_socket.create_keep()[0]
        yield from connection.flush()
        self.logger.info("Initializing second input qubit...")
        input2_qubit = Qubit(connection)
        self.logger.info("Prepare Bell measurement...")
        input2_qubit.cnot(epr)
        input2_qubit.h()
        self.logger.info("Measure both...")
        epr_meas = epr.measure()
        input2_meas = input2_qubit.measure()
        yield from connection.flush()
        csocket.send((str(epr_meas), str(input2_meas)))
        
        return {
            "epr_measurement": int(epr_meas),
            "input_measurement": int(input2_meas)
        }


class MiddleProgram(Program):
    PEER_NAME1 = "Left"
    PEER_NAME2 = "Right"

    def __init__(self):
        self.logger = LogManager.get_stack_logger(self.__class__.__name__)

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name = "Middle",
            csockets = [self.PEER_NAME1, self.PEER_NAME2],
            epr_sockets =[self.PEER_NAME1, self.PEER_NAME2],
            max_qubits = 2,
        )

    def run(self, context: ProgramContext):
        csocket_left = context.csockets[self.PEER_NAME1]
        csocket_right = context.csockets[self.PEER_NAME2]
        epr_socket_left = context.epr_sockets[self.PEER_NAME1]
        epr_socket_right = context.epr_sockets[self.PEER_NAME2]
        connection = context.connection
        yield from connection.flush()

        self.logger.info("Creating EPR pairs with left and right circuits...")
        epr_left = epr_socket_left.recv_keep()[0]
        epr_right = epr_socket_right.recv_keep()[0]
        
        self.logger.info("Apply Clifford gate U...")
        epr_right.cnot(epr_left)
        
        self.logger.info("Apply corrections on based on measurements from left and right circuits...")
        
        m_left = yield from csocket_left.recv()
        m_right = yield from csocket_right.recv()
        
        print(m_left)
        print(m_right)
        
        if m_left[0] == "1":
            epr_left.x()
        if m_left[1] == "1":
            epr_left.z()
        if m_right[0] == "1":
            epr_right.x()
        if m_right[1] == "1":
            epr_right.z()
        
        # Wait for an ack before exiting
        msg = yield from csocket_left.recv()
        assert msg == "ACK"
        msg = yield from csocket_right.recv()
        assert msg == "ACK"
        
        #final_state = get_qubit_state(target_qubit, "Target")
        #original_state = get_reference_state(self.phi, self.theta)

        #return {
        #    "epr_meas": int(epr_meas),
        #    "final_dm": final_dm,
        #    "original_dm": original_dm,
        #}
        