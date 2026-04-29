from collections import OrderedDict

import torch


def state_dict_to_cpu(state_dict):
    cpu_state = OrderedDict()
    for key, value in state_dict.items():
        cpu_state[key] = value.detach().cpu().clone()
    return cpu_state


def average_state_dicts(state_dicts):
    if not state_dicts:
        raise ValueError("state_dicts must not be empty")

    averaged = OrderedDict()
    reference = state_dicts[0]
    for key, value in reference.items():
        values = [state[key].detach().cpu() for state in state_dicts]
        if torch.is_floating_point(value):
            averaged[key] = torch.stack(values, dim=0).mean(dim=0)
        else:
            averaged[key] = values[0].clone()
    return averaged


def average_state_dicts_weighted(state_dicts, weights):
    if not state_dicts:
        raise ValueError("state_dicts must not be empty")
    if len(state_dicts) != len(weights):
        raise ValueError("state_dicts and weights must have the same length")

    total_weight = float(sum(float(weight) for weight in weights))
    if total_weight <= 0.0:
        raise ValueError("weights must sum to a positive value")

    averaged = OrderedDict()
    reference = state_dicts[0]
    normalized_weights = [float(weight) / total_weight for weight in weights]
    for key, value in reference.items():
        values = [state[key].detach().cpu() for state in state_dicts]
        if torch.is_floating_point(value):
            weighted = [tensor * weight for tensor, weight in zip(values, normalized_weights)]
            averaged[key] = torch.stack(weighted, dim=0).sum(dim=0)
        else:
            averaged[key] = values[0].clone()
    return averaged
