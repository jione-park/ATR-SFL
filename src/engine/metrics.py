class RunningAverage:
    def __init__(self) -> None:
        self.total = 0.0
        self.count = 0

    def update(self, value: float, n: int = 1) -> None:
        self.total += float(value) * n
        self.count += int(n)

    @property
    def average(self) -> float:
        if self.count == 0:
            return 0.0
        return self.total / self.count


def top1_correct(logits, targets) -> int:
    predictions = logits.argmax(dim=1)
    return int((predictions == targets).sum().item())


def tensor_nbytes(tensor) -> int:
    return int(tensor.numel() * tensor.element_size())


def tensor_token_count(tensor) -> int:
    if tensor.ndim < 2:
        return 0
    return int(tensor.shape[1])
