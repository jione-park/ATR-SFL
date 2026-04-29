# CIFAR-10 Full-Token ViT-SFL Sanity Run

## 목적

이 문서는 2026년 4월 28일에 성공한 첫 `CIFAR-10 + IID + full-token + DeiT-Tiny + training-time SFL` 실행이
정확히 무엇을 했는지 설명한다.

중요한 점은, 이 run은 **논문용 baseline 실험이 아니라 코드 경로 검증용 sanity run**이라는 것이다.

이 run의 역할은 다음 두 가지다.

1. local conda 환경에서 Hermes 코드가 실제로 돈다는 것을 확인
2. `dataset -> partition -> split model -> train loop -> metric logging -> artifacts` 경로가 연결돼 있음을 확인

증거 수준으로는 `Preliminary`보다도 더 보수적으로, **bootstrap sanity evidence**로 보는 것이 맞다.

## 실행 환경

이 run은 Docker가 아니라 **workspace-local Miniconda**에서 실행했다.

- Miniconda 설치 경로: `/home/jiwon/research/hermes/.local/miniconda3`
- conda env 경로: `/home/jiwon/research/hermes/.local/conda-envs/hermes`
- 환경 생성 스크립트: [setup_local_miniconda.sh](/home/jiwon/research/hermes/scripts/setup_local_miniconda.sh#L1), [create_local_conda_env.sh](/home/jiwon/research/hermes/scripts/create_local_conda_env.sh#L1)
- 실행 스크립트: [run_local_experiment.sh](/home/jiwon/research/hermes/scripts/run_local_experiment.sh#L1)
- 최소 runtime requirements: [requirements.runtime.txt](/home/jiwon/research/hermes/conda/requirements.runtime.txt#L1)

실행 명령은 사실상 아래와 같다.

```bash
bash scripts/run_local_experiment.sh cpu configs/experiment/cifar10_iid_full_token_sfl_sanity.json
```

이 스크립트는 내부적으로 아래 명령을 호출한다.

```bash
conda run -p /home/jiwon/research/hermes/.local/conda-envs/hermes \
  python -m src.train --config configs/experiment/cifar10_iid_full_token_sfl_sanity.json
```

## 정확히 어떤 config를 실행했는가

실행 config는 [cifar10_iid_full_token_sfl_sanity.json](/home/jiwon/research/hermes/configs/experiment/cifar10_iid_full_token_sfl_sanity.json#L1)이다.

핵심 값은 아래와 같다.

- dataset:
  - `CIFAR-10`
  - root: `data/`
  - input size: `224`
  - `download=true`
- model:
  - `deit_tiny_patch16_224`
  - `num_classes=10`
  - `pretrained=false`
  - `split_block=6`
- federation:
  - `num_clients=10`
  - `participation_rate=0.5`
  - `partition=iid`
- training:
  - `seed=105`
  - `rounds=1`
  - `local_epochs=1`
  - `batch_size=8`
  - `eval_batch_size=16`
  - `num_workers=0`
  - `max_train_batches_per_client=1`
  - `max_eval_batches=1`

여기서 `max_train_batches_per_client=1`, `max_eval_batches=1`이 매우 중요하다.  
이 값들 때문에 이번 run은 **정확한 성능 비교**가 아니라 **빠른 실행 검증**이다.

## 데이터 구조

데이터셋 생성은 [cifar.py](/home/jiwon/research/hermes/src/data/cifar.py#L11)에서 한다.

- train:
  - `RandomCrop(32, padding=4)`
  - `RandomHorizontalFlip()`
  - `Resize(224,224)`
  - `Normalize(CIFAR10_MEAN, CIFAR10_STD)`
- test:
  - `Resize(224,224)`
  - `Normalize(CIFAR10_MEAN, CIFAR10_STD)`

IID partition은 [partition.py](/home/jiwon/research/hermes/src/data/partition.py#L7)에서 만든다.

- 전체 train index를 seed로 shuffle
- `10`개 client에 round-robin으로 index 분배
- 각 client는 자기 subset으로 DataLoader 생성

즉, 현재는 Dirichlet non-IID가 아니라 **단순 IID 분할**이다.

## 모델 분할 구조

모델 분할은 [deit_split.py](/home/jiwon/research/hermes/src/models/deit_split.py#L75)에서 만든다.

이번 run의 backbone은 `deit_tiny_patch16_224`이고, `split_block=6`이다.  
DeiT-Tiny는 총 `12`개 transformer block을 가지므로 현재 분할은 다음과 같다.

- `ClientFront`
  - `patch_embed`
  - `cls_token`
  - `pos_embed`
  - `pos_drop`
  - `patch_drop`
  - `norm_pre`
  - transformer blocks `0 ~ 5`
- `ServerBack`
  - transformer blocks `6 ~ 11`
  - `norm`
  - `fc_norm`
  - `pre_logits`
  - `head_drop`
  - `head`

즉, split interface는 **block 6 앞의 token sequence**다.

이번 run에서 출력된 `model_info`는 아래였다.

- `num_blocks=12`
- `split_block=6`
- `num_tokens=197`
- `embed_dim=192`

`197`은 `14x14=196` patch token과 `cls token 1개`를 합친 값이다.

## split interface에서 실제로 전송되는 것

현재는 `full-token` run이므로 token reduction이 전혀 없다.  
client front가 만든 **모든 197개 token**이 server back으로 넘어간다고 가정한다.

한 sample의 split activation shape는 실질적으로 아래와 같다.

```text
[197 tokens, 192 dim]
```

float32 기준 sample당 activation byte 수는 대략 아래다.

```text
197 * 192 * 4 = 151,296 bytes
```

실제 eval artifact에서도 `avg_interface_bytes = 151296.0`으로 기록됐다.

## round 내부에서 무슨 일이 일어나는가

실제 trainer는 [sfl_trainer.py](/home/jiwon/research/hermes/src/engine/sfl_trainer.py#L18)에 있다.

현재 round 구조는 아래 순서다.

1. trainer가 global front와 shared server back을 초기화
2. 매 round마다 `participation_rate=0.5`를 적용해 `10`명 중 `5`명을 sampling
3. 선택된 각 client마다:
   - global front를 deep copy해서 local front 생성
   - local front와 shared server back을 train mode로 둠
   - client dataloader에서 batch를 읽음
   - local front가 `smashed activation` 생성
   - server back이 logits 생성
   - loss 계산 후 backward
   - local front optimizer step
   - shared server optimizer step
   - uplink/downlink byte 누적
4. 선택된 client들의 local front state_dict를 평균내서 global front로 반영
5. global front + shared server back으로 global eval 수행
6. round summary를 `metrics_history.json`에 저장

이번 run에서 선택된 client는 아래였다.

```text
[1, 3, 5, 8, 9]
```

## 중요한 구현 해석 포인트

현재 구현은 “훈련 가능한 split/federated 경로 검증”에는 적합하지만, 아직 논문용 정식 protocol은 아니다.

특히 아래를 명확히 알아야 한다.

### 1. server는 round 내에서 shared로 순차 업데이트된다

선택된 client들이 병렬로 server에 접속하는 모델이 아니라,
**하나의 shared server back을 client 순서대로 업데이트하는 구조**다.

### 2. local front만 client별로 복사되고 평균된다

각 client는 round 시작 시 global front를 복사받고, local update 후 다시 평균된다.

### 3. downlink bytes는 근사값이다

현재는 backward signal이 split activation과 같은 shape라고 보고,
`downlink_bytes = uplink_bytes`로 계산한다.

즉, 이 값은 실제 wireless stack을 반영한 값이 아니라 **bootstrap accounting proxy**다.

### 4. token reduction은 아직 없다

이 run은 `B1 full-token baseline`의 **아주 초기 bootstrap 형태**에 가깝다.

- `top-k pruning` 없음
- `residual fusion` 없음
- `channel adaptation` 없음
- `wireless latency model` 없음

## 이번 run에서 남은 artifact

이번 성공 run의 artifact 경로는 아래다.

- run dir: [20260428_153552_cifar10_iid_full_token_sfl_sanity](/home/jiwon/research/hermes/artifacts/runs/20260428_153552_cifar10_iid_full_token_sfl_sanity)
- config dump: [config.json](/home/jiwon/research/hermes/artifacts/runs/20260428_153552_cifar10_iid_full_token_sfl_sanity/config.json)
- metadata: [metadata.json](/home/jiwon/research/hermes/artifacts/runs/20260428_153552_cifar10_iid_full_token_sfl_sanity/metadata.json)
- round metrics: [metrics_history.json](/home/jiwon/research/hermes/artifacts/runs/20260428_153552_cifar10_iid_full_token_sfl_sanity/metrics_history.json)
- summary: [summary.json](/home/jiwon/research/hermes/artifacts/runs/20260428_153552_cifar10_iid_full_token_sfl_sanity/summary.json)

metadata에서 `repo_commit`이 `unknown`인 이유는 현재 Hermes 작업 디렉터리가 git repository가 아니기 때문이다.

## 이번 run의 수치 결과

이 수치는 성능 평가가 아니라 **코드 경로가 제대로 돈다는 증거**로만 해석해야 한다.

- train:
  - loss: `2.329865026473999`
  - accuracy: `0.15`
  - examples: `40`
  - avg interface tokens: `197.0`
  - uplink bytes: `6,051,840`
  - downlink bytes: `6,051,840`
  - roundtrip bytes: `12,103,680`
- eval:
  - loss: `2.170395851135254`
  - accuracy: `0.1875`
  - examples: `16`
  - avg interface bytes: `151,296.0`
  - avg interface tokens: `197.0`
- round wall-clock:
  - `0.7643 sec`

## 왜 이 결과를 논문용 실험으로 보면 안 되는가

이 run은 아래 이유로 claim-ready baseline이 아니다.

1. `rounds=1`이다.
2. 선택된 client당 train batch가 `1`개뿐이다.
3. eval batch도 `1`개뿐이다.
4. wireless latency model이 없다.
5. token reduction operator가 없다.
6. seed 평균이 없다.
7. non-IID 조건이 없다.

따라서 이 run은 이렇게 불러야 한다.

```text
Local conda bootstrap sanity run for CIFAR-10 IID full-token ViT-SFL
```

## 지금 이 문서를 보고 무엇을 이어가면 되는가

다음 단계는 세 가지다.

1. `sanity config`의 batch cap을 풀고 `CIFAR-10 IID full-token` 실제 baseline으로 확장
2. wireless metric을 `latency-aware` 형태로 업그레이드
3. 현재 split interface 위치에 `EViT-inspired top-k + residual fusion` operator 삽입

즉, 이번 run은 **연구 결과**가 아니라 **연구를 시작할 수 있는 실행 바닥면**을 확인한 것이다.
