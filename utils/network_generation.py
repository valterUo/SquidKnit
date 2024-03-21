import itertools
from typing import List

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


def create_single_node_network(qdevice_typ: str, qdevice_cfg: IQDeviceConfig):
    network_config = StackNetworkConfig(stacks=[], links=[], clinks=[])
    stack = StackConfig(name="Alice", qdevice_typ=qdevice_typ, qdevice_cfg=qdevice_cfg)
    network_config.stacks.append(stack)
    return network_config


def create_2_node_network(
    link_typ: str,
    link_cfg: ILinkConfig,
    clink_typ: str = "instant",
    clink_cfg: ICLinkConfig = None,
    qdevice_typ: str = "generic",
    qdevice_cfg: IQDeviceConfig = None,
) -> StackNetworkConfig:
    node_names = ["Alice", "Bob"]
    return create_complete_graph_network(
        node_names, link_typ, link_cfg, clink_typ, clink_cfg, qdevice_typ, qdevice_cfg
    )


def create_complete_graph_network(
    node_names: List[str],
    link_typ: str,
    link_cfg_dict: dict,
    link_cfg_default: ILinkConfig,
    clink_typ: str = "instant",
    clink_cfg: ICLinkConfig = None,
    qdevice_typ: str = "generic",
    qdevice_cfg_dict: dict = {}
) -> StackNetworkConfig:
    
    network_config = StackNetworkConfig(stacks=[], links=[], clinks=[])

    assert len(node_names) > 0

    for node_name in node_names:
        if node_name not in qdevice_cfg_dict:
            qdevice_cfg = GenericQDeviceConfig.perfect_config()
        else:
            qdevice_cfg = qdevice_cfg_dict[node_name]
        
        stack = StackConfig(
            name=node_name, qdevice_typ=qdevice_typ, qdevice_cfg=qdevice_cfg
        )
        network_config.stacks.append(stack)

    for s1, s2 in itertools.combinations(node_names, 2):
        if (s1, s2) in link_cfg_dict:
            #print(link_cfg_dict[(s1, s2)])
            link_cfg = link_cfg_dict[(s1, s2)]
        elif (s2, s1) in link_cfg_dict:
            #print(link_cfg_dict[(s2, s1)])
            link_cfg = link_cfg_dict[(s2, s1)]
        else:
            link_cfg = link_cfg_default
        link = LinkConfig(stack1=s1, stack2=s2, typ=link_typ, cfg=link_cfg)
        network_config.links.append(link)

        clink = CLinkConfig(stack1=s1, stack2=s2, typ=clink_typ, cfg=clink_cfg)
        network_config.clinks.append(clink)

    return network_config


def create_simple_network(
    node_names: List[str],
    link_names: List[str],
    link_noises: dict,
    qdevice_noises: dict,
    qdevice_depolar_time: float = 0,
    qdevice_op_time: float = 0,
    clink_delay: float = 0.0,
    link_delay: float = 0.0,
    prob_successes: dict = {},
) -> StackNetworkConfig:
    
    qdevice_cfg_dict = {}
    for node_name in node_names:
        qdevice_cfg = GenericQDeviceConfig.perfect_config()
        qdevice_cfg.two_qubit_gate_depolar_prob = qdevice_noises[node_name]
        qdevice_cfg.single_qubit_gate_depolar_prob = qdevice_noises[node_name]
        qdevice_cfg.T1 = qdevice_depolar_time
        qdevice_cfg.T2 = qdevice_depolar_time
        qdevice_cfg.measure_time = qdevice_op_time
        qdevice_cfg.init_time = qdevice_op_time
        qdevice_cfg.single_qubit_gate_time = qdevice_op_time
        qdevice_cfg.two_qubit_gate_time = qdevice_op_time
        qdevice_cfg_dict[node_name] = qdevice_cfg
    
    link_cfg_dict = {}
    for link_name in link_names:
        #print(link_noises[link_name], prob_successes[link_name])
        link_cfg = DepolariseLinkConfig(fidelity = link_noises[link_name], 
                                        t_cycle=link_delay, 
                                        prob_success=prob_successes[link_name])
        link_cfg_dict[link_name] = link_cfg
    
    clink_cfg = DefaultCLinkConfig(delay=clink_delay)

    return create_complete_graph_network(
        node_names,
        link_typ="depolarise",
        link_cfg_dict=link_cfg_dict,
        link_cfg_default=DepolariseLinkConfig(fidelity=1, t_cycle=link_delay, prob_success=1),
        clink_typ="default",
        clink_cfg=clink_cfg,
        qdevice_typ="generic",
        qdevice_cfg_dict=qdevice_cfg_dict,
    )