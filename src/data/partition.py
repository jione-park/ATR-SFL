import random
from typing import List, Sequence

from torch.utils.data import DataLoader, Dataset, Subset


def build_iid_partitions(dataset_size: int, num_clients: int, seed: int) -> List[List[int]]:
    if num_clients <= 0:
        raise ValueError("num_clients must be positive")

    indices = list(range(dataset_size))
    rng = random.Random(seed)
    rng.shuffle(indices)

    partitions: List[List[int]] = [[] for _ in range(num_clients)]
    for idx, sample_index in enumerate(indices):
        partitions[idx % num_clients].append(sample_index)

    return partitions


def build_client_dataloaders(
    dataset: Dataset,
    partitions: Sequence[Sequence[int]],
    batch_size: int,
    num_workers: int,
) -> List[DataLoader]:
    dataloaders: List[DataLoader] = []
    for partition in partitions:
        subset = Subset(dataset, list(partition))
        dataloaders.append(
            DataLoader(
                subset,
                batch_size=batch_size,
                shuffle=True,
                num_workers=num_workers,
                pin_memory=False,
            )
        )
    return dataloaders
