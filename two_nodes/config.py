from squidasm.run.stack.config import (
    GenericQDeviceConfig,
    NVQDeviceConfig,
    StackConfig
)
from netsquid_magic.models.depolarise import DepolariseLinkConfig
from netsquid_netbuilder.base_configs import LinkConfig, StackNetworkConfig

def create_two_node_network(
    node_names, device = "generic", fidelity: float = 0, qdevice_noise: float = 0
) -> StackNetworkConfig:
    
    qdevice_cfg = None
    if device == "generic":
        qdevice_cfg = GenericQDeviceConfig.perfect_config()
    elif device == "nv":
        qdevice_cfg = NVQDeviceConfig.perfect_config()
        
    qdevice_cfg.two_qubit_gate_depolar_prob = qdevice_noise
    qdevice_cfg.single_qubit_gate_depolar_prob = qdevice_noise
    qdevice_cfg.num_qubits = 6
    stacks = [
        StackConfig(name = name, 
                    qdevice_typ = device, 
                    qdevice_cfg = qdevice_cfg)
        for name in node_names
    ]

    #fidelity = 1 - link_noise * 3 / 4
    link_cfg = DepolariseLinkConfig(fidelity = fidelity, 
                                    t_cycle = 1000, 
                                    prob_success = 1)
    link = LinkConfig(stack1 = node_names[0], 
                      stack2 = node_names[1], 
                      typ = "depolarise", 
                      cfg = link_cfg)
    
    return StackNetworkConfig(stacks=stacks, links=[link])