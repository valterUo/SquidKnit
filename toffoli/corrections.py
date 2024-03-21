def toffoli(qubit1, qubit2, qubit3):
    qubit3.H()
    qubit2.cnot(qubit3)
    # Adjoint to T
    # -pi/4 = 7pi/4 = 7pi/2^2 -> n = 7, d = 2
    qubit3.rot_Z(7, 2)
    qubit1.cnot(qubit3)
    qubit3.rot_Z(1, 2)
    qubit2.cnot(qubit3)
    # Adjoint to T
    qubit3.rot_Z(7, 2)
    qubit1.cnot(qubit3)
    qubit2.rot_Z(1, 2)
    qubit3.rot_Z(1, 2)
    qubit3.H()
    qubit1.cnot(qubit2)
    # Adjoint to T
    qubit2.rot_Z(7, 2)
    qubit1.rot_Z(1, 2)
    qubit1.cnot(qubit2)


def correction1(qubit1, qubit2, qubit3):
    qubit1.Z()


def correction2(qubit1, qubit2, qubit3):
    qubit2.Z()

    
def correction3(qubit1, qubit2, qubit3):
    
    #
    qubit3.rot_Z(1, 1)
    
    #
    qubit3.cnot(qubit2)
    qubit2.rot_Z(1, 1)
    qubit3.cnot(qubit2)
    
    #
    qubit3.cnot(qubit1)
    qubit1.rot_Z(1, 1)
    qubit3.cnot(qubit1)
    
    # 
    qubit3.cnot(qubit2)
    qubit2.cnot(qubit1)
    # Adjoint to S
    qubit1.rot_Z(3, 1)
    qubit2.cnot(qubit1)
    qubit3.cnot(qubit2)


def correction4(qubit1, qubit2, qubit3):
    qubit1.H()
    qubit3.H()
    
    #
    qubit1.rot_Z(1, 1)
    
    #
    qubit3.cnot(qubit1)
    qubit1.rot_Z(1, 1)
    qubit3.cnot(qubit1)
    
    #
    qubit2.cnot(qubit1)
    qubit1.rot_Z(1, 1)
    qubit2.cnot(qubit1)
    
    #
    qubit3.cnot(qubit2)
    qubit2.cnot(qubit1)
    # Adjoint to S
    qubit1.rot_Z(3, 1)
    qubit2.cnot(qubit1)
    qubit3.cnot(qubit2)
    
    qubit1.H()
    qubit3.H()

 
def correction5(qubit1, qubit2, qubit3):
    qubit2.H()
    qubit3.H()
    
    #
    qubit2.rot_Z(1, 1)
    
    #
    qubit3.cnot(qubit2)
    qubit2.rot_Z(1, 1)
    qubit3.cnot(qubit2)
    
    #
    qubit2.cnot(qubit1)
    qubit1.rot_Z(1, 1)
    qubit2.cnot(qubit1)
    
    #
    qubit3.cnot(qubit2)
    qubit2.cnot(qubit1)
    # Adjoint to S
    qubit1.rot_Z(3, 1)
    qubit2.cnot(qubit1)
    qubit3.cnot(qubit2)
    
    qubit2.H()
    qubit3.H()


def correction6(qubit1, qubit2, qubit3):
    qubit3.H()
    qubit3.Z()
    qubit3.H()