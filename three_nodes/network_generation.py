from netsquid_magic.models.depolarise import DepolariseLinkConfig
from netsquid_netbuilder.base_configs import (
    CLinkConfig,
    LinkConfig,
    StackConfig,
    StackNetworkConfig,
)
from netsquid_netbuilder.modules.clinks.default import DefaultCLinkConfig
from netsquid_netbuilder.modules.clinks.interface import ICLinkConfig
from netsquid_netbuilder.modules.links.interface import ILinkConfig
from netsquid_netbuilder.modules.qdevices.generic import GenericQDeviceConfig
from netsquid_netbuilder.modules.qdevices.interface import IQDeviceConfig

from networkx import DiGraph

def create_network_from_graph(
    graph: DiGraph,
    link_typ: str = "depolarise",
    link_cfg: ILinkConfig = None,
    clink_typ: str = "instant",
    clink_cfg: ICLinkConfig = None,
    qdevice_typ: str = "generic",
    qdevice_cfg: IQDeviceConfig = None,
    link_noise: float = 0,
    qdevice_noise: float = 0,
    qdevice_depolar_time: float = 0,
    qdevice_op_time: float = 0,
    clink_delay: float = 0.0,
    link_delay: float = 0.0,
) -> StackNetworkConfig:
    
    node_names = list(graph.nodes())
    
    assert len(node_names) > 0
    
    qdevice_cfg = GenericQDeviceConfig.perfect_config()

    qdevice_cfg.two_qubit_gate_depolar_prob = qdevice_noise
    qdevice_cfg.single_qubit_gate_depolar_prob = qdevice_noise

    qdevice_cfg.T1 = qdevice_depolar_time
    qdevice_cfg.T2 = qdevice_depolar_time

    qdevice_cfg.measure_time = qdevice_op_time
    qdevice_cfg.init_time = qdevice_op_time
    qdevice_cfg.single_qubit_gate_time = qdevice_op_time
    qdevice_cfg.two_qubit_gate_time = qdevice_op_time
    
    link_cfg = DepolariseLinkConfig(
        fidelity=1 - link_noise * 3 / 4, t_cycle=link_delay, prob_success=1
    )
    
    clink_cfg = DefaultCLinkConfig(delay=clink_delay)
    
    network_config = StackNetworkConfig(stacks=[], links=[], clinks=[])
    
    for node_name in node_names:
        qdevice_cfg = (
            GenericQDeviceConfig.perfect_config()
            if qdevice_cfg is None
            else qdevice_cfg
        )
        stack = StackConfig(
            name=node_name, qdevice_typ=qdevice_typ, qdevice_cfg=qdevice_cfg
        )
        network_config.stacks.append(stack)

    for s1, s2 in graph.edges():
        print(s1, s2)
        link = LinkConfig(stack1=s1, stack2=s2, typ=link_typ, cfg=link_cfg)
        network_config.links.append(link)

        clink = CLinkConfig(stack1=s1, stack2=s2, typ=clink_typ, cfg=clink_cfg)
        network_config.clinks.append(clink)

    return network_config