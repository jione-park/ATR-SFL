# 계획: 외부 공개 코드 역할 분리 기반 병렬 round SFL 구현 계획

## 목표

Hermes의 `parallel_round_server_tail` 구현을 진행할 때, 여러 공개 코드를 역할별 레퍼런스로 분리해서 참고하고, 각 코드에서 무엇을 가져오고 무엇은 가져오지 않을지 명확히 고정한다.

## 범위

- SplitFed 원본 V1/V2 repo를 SFL semantics 기준 레퍼런스로 사용
- `split-learning-demo`를 split forward/backward 구현 감각 기준 레퍼런스로 사용
- FL PyTorch repo 하나를 FedAvg, non-IID, config, logging 유틸 기준 레퍼런스로 사용
- FeSViBS를 ViT split model 아이디어 기준 레퍼런스로 사용
- 위 기준을 현재 Hermes 아키텍처에 매핑하는 구현 계획 정리

## 입력 자료

- SplitFed 원본 repo: `chandra2thapa/SplitFed-When-Federated-Learning-Meets-Split-Learning`
- split-learning-demo repo: `evanwrm/split-learning-demo`
- FL PyTorch repo: `vaseline555/Federated-Learning-in-PyTorch`
- ViT split 참고 repo: `faresmalik/FeSViBS`
- 현재 Hermes 코드
  - `src/train.py`
  - `src/engine/sfl_trainer.py`
  - `src/models/deit_split.py`
  - `src/utils/config.py`
  - `src/utils/experiment.py`
  - `src/utils/fedavg.py`

## 산출물

- 외부 레퍼런스별 역할 정의
- `parallel_round_server_tail` 구현을 위한 코드 수정 우선순위
- 참고 repo별로 실제로 벤치마크해야 할 파일/개념 목록
- 이후 구현 단계에서 혼선을 막기 위한 금지사항 목록

## 단계

1. 역할 분리 원칙을 먼저 고정한다.
   - 하나의 공개 코드를 전체 골격으로 포팅하지 않는다.
   - 각 repo는 아래 역할만 담당한다.
     - SplitFed: SFL semantics
     - split-learning-demo: split forward/backward 감각
     - FL PyTorch: FL utilities
     - FeSViBS: ViT split model idea
   - 즉 Hermes의 최종 구조는 이 네 소스를 조합해 직접 설계한다.

2. SplitFed 원본 V1/V2 repo에서 가져올 것을 고정한다.
   - 참고 목적: `sequential_server_bootstrap`와 `parallel_round_server_tail`의 semantics 구분 기준 확보
   - 가져올 것:
     - SFLV1과 SFLV2의 round semantics 차이
     - round 종료 시 aggregation이 언제 일어나는지에 대한 정의
     - client-side / server-side local replica의 존재 여부
   - 가져오지 않을 것:
     - ResNet18 + HAM10000 특화 구조
     - 오래된 스크립트형 구현 스타일
     - 현재 Hermes와 맞지 않는 monolithic file layout
   - Hermes 적용 방식:
     - vocabulary와 protocol naming을 이 repo 기준으로 정리
     - `sequential_server_bootstrap`는 현재 bootstrap 구조를 설명하는 이름으로 유지
     - `parallel_round_server_tail`는 SFLV1-like synchronous semantics를 반영하는 새 trainer로 구현

3. `split-learning-demo`에서 가져올 것을 고정한다.
   - 참고 목적: split boundary에서 forward/backward가 어떻게 깔끔하게 분리되는지에 대한 구현 감각 확보
   - 가져올 것:
     - cut layer 전후의 모듈 분리 감각
     - client/server 역할 분리 방식
     - split tensor를 경계 객체로 취급하는 인터페이스 아이디어
   - 가져오지 않을 것:
     - websocket, MPI, demo app 구조
     - inference/web UI 관련 부분
   - Hermes 적용 방식:
     - `ClientFront`와 `ServerBack` 사이의 인터페이스를 명시적 operator API로 고정
     - operator API는 다음처럼 유지
       - input: `split tokens, metadata`
       - output: `reduced tokens, interface stats`
     - full-token baseline도 같은 API의 identity operator를 사용

4. FL PyTorch repo에서 가져올 것을 고정한다.
   - 참고 repo는 `vaseline555/Federated-Learning-in-PyTorch`로 고정한다.
   - 참고 목적: FedAvg, non-IID partition, experiment config, logging utility 감각 확보
   - 가져올 것:
     - IID / Dirichlet / pathological non-IID partition 개념 정리
     - sample-weighted FedAvg 구현 원칙
     - config에서 dataset / heterogeneity / optimizer / rounds를 분리하는 방식
     - 실험 실행과 기록을 일관되게 남기는 구성 감각
   - 가져오지 않을 것:
     - 전체 framework 구조를 그대로 이식하는 것
     - Hermes의 split learning loop를 FL loop에 억지로 맞추는 것
   - Hermes 적용 방식:
     - `num_examples` 기준 sample-weighted averaging을 front/back 모두에 동일 적용
     - 추후 non-IID 확장 시 partition 유틸을 단계적으로 확장
     - config 필드 확장 시 FL-style naming discipline을 참고

5. FeSViBS에서 가져올 것을 고정한다.
   - 참고 목적: ViT 기반 split 학습을 실제로 어떻게 모델링하는지에 대한 아이디어 확보
   - 가져올 것:
     - ViT를 split point 기준으로 나누는 감각
     - block-level split에 대한 실험 감각
     - split learning과 federated setting을 결합할 때 필요한 최소 모델 분리 아이디어
   - 가져오지 않을 것:
     - 원본의 block sampling 구조 자체를 baseline semantics로 채택하는 것
     - client별 head/tail 복제를 그대로 따라가는 것
     - 현재 논문 메인 모델과 맞지 않는 mixed design
   - Hermes 적용 방식:
     - `src/models/deit_split.py`의 `ClientFront` / `ServerBack` 분리를 유지
     - server-tail 구조를 메인 baseline으로 고정
     - 이후 EViT-inspired token reduction operator를 split interface에 삽입

6. 최종 Hermes target 구조를 명시한다.
   - protocol name:
     - `sequential_server_bootstrap`
     - `parallel_round_server_tail`
   - main paper baseline:
     - `parallel_round_server_tail`
   - round 내부 semantics:
     - 각 client는 round당 `local_epochs = E`, batch loop `B`를 자기 `local_front`/`local_back` 쌍으로 수행한다.
   - aggregation:
     - front/back 모두 `num_examples` 기준 sample-weighted averaging
   - server semantics:
     - server는 per-client local back replica를 round 내에서 사용하고, round 종료 시에만 global back으로 동기 집계한다.
   - split interface:
     - operator는 `local_front(images)` 직후, `local_back(...)` 직전에 위치

7. 구현 작업을 repo 역할 기준으로 분해한다.
   - Phase 1: protocol naming과 config schema 정리
     - SplitFed semantics를 반영해 protocol field 추가
   - Phase 2: trainer 분리
     - `SequentialBootstrapTrainer`
     - `ParallelRoundTrainer`
   - Phase 3: operator API 도입
     - identity operator 먼저 구현
   - Phase 4: weighted FedAvg 유틸 정리
     - FL PyTorch 스타일의 sample-weighted aggregation 반영
   - Phase 5: full-token `parallel_round_server_tail` sanity
     - CIFAR-10 IID 2-round GPU
   - Phase 6: bootstrap run
     - CIFAR-10 IID 20-round
   - Phase 7: CIFAR-100 확장
   - Phase 8: EViT-inspired operator 추가

8. 코드 읽기 우선순위를 고정한다.
   - SplitFed repo
     - `SFLV1_*.py`
     - `SFLV2_*.py`
     - README의 version 설명
   - split-learning-demo
     - README
     - server/client split learning example code
   - FL PyTorch repo
     - dataset partition 관련 코드
     - aggregation utility
     - config / command / logging entrypoints
   - FeSViBS
     - `FeSViBS.py`
     - `models.py`
     - SLViT / FeSViBS 실행 경로

9. 금지사항을 명시한다.
   - SplitFed repo의 monolithic script를 그대로 복붙하지 않는다.
   - split-learning-demo의 networking layer를 Hermes trainer에 섞지 않는다.
   - FL PyTorch framework 전체를 vendor하지 않는다.
   - FeSViBS의 block sampling semantics를 baseline protocol semantics와 혼동하지 않는다.
   - 하나의 외부 repo가 Hermes의 최종 설계를 결정하게 두지 않는다.

## 검증

- 각 공개 코드의 역할이 서로 겹치지 않게 정의되었는지 확인
- `parallel_round_server_tail` 구현 계획이 SplitFed semantics와 일치하는지 확인
- operator API가 full-token과 token reduction 모두에서 재사용 가능한지 확인
- `num_examples` 기준 sample-weighted aggregation이 front/back 모두에 명시되었는지 확인
- 외부 repo를 참조하더라도 Hermes의 run/config/logging 규칙이 유지되는지 확인

## 메모

- 구현의 기준선은 Hermes 내부 plan과 vocabulary이며, 외부 repo는 역할별 레퍼런스일 뿐이다.
- 첫 구현 목표는 공개 코드 재현이 아니라 `parallel_round_server_tail` full-token baseline을 안정적으로 세우는 것이다.
- 논문 claim과 직접 연결되는 부분은 SplitFed semantics와 server-tail split interface 정의다.
