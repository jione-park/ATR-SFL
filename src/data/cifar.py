from pathlib import Path
from typing import Tuple

from torchvision import datasets, transforms


CIFAR10_MEAN = (0.4914, 0.4822, 0.4465)
CIFAR10_STD = (0.2470, 0.2435, 0.2616)
CIFAR100_MEAN = (0.5071, 0.4867, 0.4408)
CIFAR100_STD = (0.2675, 0.2565, 0.2761)


def build_cifar10_datasets(root: str, image_size: int, download: bool) -> Tuple[datasets.CIFAR10, datasets.CIFAR10]:
    dataset_root = Path(root) / "cifar10"

    train_transform = transforms.Compose(
        [
            transforms.RandomCrop(32, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(CIFAR10_MEAN, CIFAR10_STD),
        ]
    )
    test_transform = transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(CIFAR10_MEAN, CIFAR10_STD),
        ]
    )

    train_dataset = datasets.CIFAR10(
        root=str(dataset_root),
        train=True,
        transform=train_transform,
        download=download,
    )
    test_dataset = datasets.CIFAR10(
        root=str(dataset_root),
        train=False,
        transform=test_transform,
        download=download,
    )
    return train_dataset, test_dataset


def build_cifar100_datasets(
    root: str, image_size: int, download: bool
) -> Tuple[datasets.CIFAR100, datasets.CIFAR100]:
    dataset_root = Path(root) / "cifar100"

    train_transform = transforms.Compose(
        [
            transforms.RandomCrop(32, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(CIFAR100_MEAN, CIFAR100_STD),
        ]
    )
    test_transform = transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(CIFAR100_MEAN, CIFAR100_STD),
        ]
    )

    train_dataset = datasets.CIFAR100(
        root=str(dataset_root),
        train=True,
        transform=train_transform,
        download=download,
    )
    test_dataset = datasets.CIFAR100(
        root=str(dataset_root),
        train=False,
        transform=test_transform,
        download=download,
    )
    return train_dataset, test_dataset
