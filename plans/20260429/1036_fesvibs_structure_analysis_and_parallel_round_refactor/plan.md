# 계획: FeSViBS 구조 분석과 병렬 round server-tail 전환 계획

## 목표

현재 Hermes 코드가 FeSViBS 원본과 어떤 점에서 같고 다른지 구조적으로 분석하고, 논문 메인 모델인 병렬 round형 server-tail SFL로 전환하기 위한 구체적 수정 계획을 정리한다.

## 범위

- 현재 Hermes 구현 구조 분석
- FeSViBS 원본 코드 구조와의 차이 정리
- 병렬 round형 server-tail full-token baseline으로 가기 위한 리팩토링 계획 수립
- 이후 token reduction operator를 얹기 위한 준비 단계 정의

## 입력 자료

- `src/train.py`
- `src/engine/sfl_trainer.py`
- `src/models/deit_split.py`
- `src/data/partition.py`
- `src/utils/config.py`
- `third_party/FeSViBS/FeSViBS.py`
- `third_party/FeSViBS/models.py`
- 기존 병렬 round 관련 plan 문서

## 산출물

- 현재 구현 구조 요약
- FeSViBS 원본 대비 차이점 요약
- 병렬 round server-tail 구조로 가기 위한 단계별 수정 계획
- 구현 순서와 검증 순서가 정리된 실행 plan

## 단계

1. 현재 Hermes 구조를 기준선으로 고정한다.
   - entrypoint는 `src/train.py`에서 config를 읽고 `SFLTrainer` 하나를 실행한다.
   - `SFLTrainer`는 global client front 1개와 server back 1개를 만든다.
   - 각 round에서 참여 client를 고른 뒤, client마다 `global_front`만 복사한다.
   - 각 client 학습 동안 `server_back`은 복사되지 않고 같은 인스턴스가 순차적으로 업데이트된다.
   - round 종료 후에는 client front state만 FedAvg 하고, server back은 round 내 순차 update 결과를 그대로 유지한다.
   - 따라서 현재 구현은 병렬 round형이 아니라 `V2-style sequential server update + front-only aggregation` 구조다.

2. FeSViBS 원본 구조를 현재 코드와 분리해서 해석한다.
   - 원본 FeSViBS는 client별 patch embed와 client별 tail head를 따로 들고 있다.
   - 동시에 ViT body의 일부 공통 파라미터를 client 순회 중 업데이트한 뒤, client별 round 종료 시 특정 weight vector만 평균한다.
   - 즉 원본도 우리가 원하는 깔끔한 server-tail 병렬 round simulator와는 다르다.
   - Hermes는 FeSViBS에서 `ViT 기반 split/federated 학습을 한다`는 큰 아이디어만 참고했고, 실제 구조는 단순화해서 다시 쓴 상태라고 보는 편이 정확하다.

3. 목표 구조를 명시한다.
   - 논문 메인 baseline은 `parallel-round + server-tail + synchronous aggregation`이다.
   - client는 `patch_embed + early blocks`를 가진다.
   - server는 `remaining blocks + cls head + loss`를 가진다.
   - 각 round의 참여 client는 자기 `local_front`와 자기 `local_back` 복사본 쌍으로 split learning local step을 수행한다.
   - 각 client는 round당 `local_epochs = E`, batch loop `B`를 자기 `local_front`/`local_back` 쌍으로 수행한다.
   - server는 per-client local back replica를 round 내에서 사용하고, round 종료 시에만 global back으로 동기 집계한다.
   - round 종료 시 client front와 server back 둘 다 `num_examples` 기준 sample-weighted aggregation을 수행한다.
   - 평가 시에는 aggregated global front와 aggregated global server back을 사용한다.

4. config 계층 수정 계획을 정리한다.
   - 학습 프로토콜 이름은 아래 두 개로 최종 고정한다.
     - `sequential_server_bootstrap`
     - `parallel_round_server_tail`
   - 이 vocabulary를 config, stdout log, summary, 문서에서 공용으로 그대로 사용한다.
   - `system` 또는 `training` 아래에 학습 프로토콜 필드를 추가한다.
   - 예시:
     - `system.training_protocol = parallel_round_server_tail`
     - `system.server_aggregation = fedavg`
     - `system.client_aggregation = fedavg`
   - 지금의 bootstrap 설정은 명시적으로 `sequential_server_bootstrap`로 남겨 구분한다.
   - 이렇게 해야 기존 run 기록과 새 병렬 round형 baseline이 섞이지 않는다.

5. trainer 리팩토링 계획을 정리한다.
   - 현재 `SFLTrainer`는 하나의 trainer가 단일 프로토콜만 가진다.
   - 이를 그대로 억지로 확장하지 말고 아래 중 하나로 정리한다.
     - 옵션 A: `BaseTrainer` + `SequentialBootstrapTrainer` + `ParallelRoundTrainer`
     - 옵션 B: `SFLTrainer` 내부에서 protocol 분기
   - 권장안은 옵션 A다.
   - 이유:
     - 현재 bootstrap 코드와 새 코드의 학습 의미가 다르다.
     - 이후 결과 해석도 프로토콜 단위로 나뉜다.
     - token operator 추가 시 병렬 round trainer에만 안정적으로 얹기 쉽다.

6. 병렬 round trainer의 최소 기능을 정의한다.
   - `_sample_clients(round_idx)`는 그대로 재사용 가능
   - 새로운 round 루프는 아래 순서를 따른다.
     1. 참여 client 집합 선택
     2. 각 client에 대해 `local_front`, `local_server_back`를 global state에서 복사
     3. 각 client local step 수행
     4. client별 반환값 수집
        - front state dict
        - server back state dict
        - sample count
        - metric dict
     5. front와 server back을 sample-weighted aggregation
     6. global model 업데이트
     7. evaluation 및 metrics 저장
   - 핵심은 `server_back`도 각 client local replica를 가지며, round 끝에 동기 집계된다는 점이다.

7. local training 함수 수정 계획을 정리한다.
   - 현재 `_train_selected_client`는 `local_front`만 복사하고 `self.server_back`을 직접 사용한다.
   - 새 구조에서는 각 client가 round 내부에서 `local_epochs = E`, batch loop `B`를 자기 `local_front`/`local_back` 쌍으로 수행한다.
   - 이를 `train_one_client_round(client_id, global_front, global_back)` 형태로 바꾼다.
   - 함수 내부에서는:
     - `local_front = deepcopy(global_front)`
     - `local_back = deepcopy(global_back)`
     - optimizer도 front/back 각각 또는 합쳐서 local pair 기준으로 생성
     - split forward -> server tail -> loss -> backward를 local pair 안에서 완료
   - 반환값은 최소한 다음을 포함해야 한다.
     - `front_state`
     - `back_state`
     - `num_examples`
     - `train_loss`
     - `train_acc`
     - `avg_interface_tokens`
     - `uplink_bytes`
     - `downlink_bytes`
     - `client_latency_sec`

8. aggregation 유틸 확장 계획을 정리한다.
   - 현재 `average_state_dicts`는 단순 평균만 지원한다.
   - 병렬 round형에서는 `num_examples` 기준 sample-weighted averaging을 front/back 모두에 동일하게 적용한다.
   - 따라서 `average_state_dicts`를 확장하거나 새 함수로 아래를 추가한다.
     - `average_state_dicts_weighted(state_dicts, weights)`
   - front와 back 모두 같은 aggregation 규칙을 사용할 수 있게 만든다.

9. evaluation 구조 수정 계획을 정리한다.
   - 현재 평가는 global front + current server back으로 충분하다.
   - 병렬 round형에서는 aggregated global front + aggregated global back을 그대로 평가하면 된다.
   - 이 단계에서는 별도 구조 변화가 크지 않다.
   - 다만 이후 token operator 추가를 위해 evaluation도 interface metric을 재사용 가능한 형태로 유지한다.

10. metric/logging 확장 계획을 정리한다.
   - 현재는 `avg_server_latency`가 비어 있다.
   - 병렬 round형에서는 아래 필드 의미를 먼저 고정한다.
     - `client_latency_sec`: client local compute + uplink + optional wait surrogate
     - `server_latency_sec`: server tail compute
     - `round_latency`: `max_k(client_path_latency_k) + aggregation_overhead`
   - 저장 시에는 아래 집계 필드를 유지하거나 확장한다.
     - `avg_client_latency`
     - `avg_server_latency`
     - `max_client_latency`
     - `round_latency`
   - 첫 구현에서는 실제 서버 연산 시간을 정교하게 재지 못해도, 최소한 placeholder가 아니라 추적 가능한 구조를 만든다.
   - 이후 wireless/token scheduler 실험 시 위 의미를 그대로 유지한다.

11. token operator 삽입 위치와 API를 미리 고정한다.
   - operator는 `local_front(images)` 직후, `local_back(...)` 직전에 들어간다.
   - 즉 split interface abstraction은 trainer가 아니라 model pair 사이에 위치한다.
   - full-token baseline 단계에서도 `identity operator`를 같은 인터페이스로 넣는다.
   - operator API 예시는 다음처럼 고정한다.
     - input: split tokens, metadata
     - output: reduced tokens, interface stats
   - 이후 EViT-inspired operator는 같은 인터페이스를 구현하도록 설계한다.

12. 구현 순서를 고정한다.
   - Phase 1: protocol/config 분리
   - Phase 2: 병렬 round trainer 추가
   - Phase 3: weighted aggregation 유틸 추가
   - Phase 4: full-token CIFAR-10 IID 2-round GPU sanity
   - Phase 5: full-token CIFAR-10 IID 20-round bootstrap
   - Phase 6: CIFAR-100 확장
   - Phase 7: token operator integration

## 검증

- 새 trainer가 현재 bootstrap trainer와 명확히 다른 프로토콜을 구현하는지 확인
- server back이 client별 local replica를 거친 뒤 round 종료 시 동기 집계되는지 확인
- full-token 병렬 round baseline이 CIFAR-10에서 정상 학습되는지 확인
- 기존 run 기록 규칙에 맞게 config, metrics, summary가 모두 저장되는지 확인
- 이후 operator 추가 시 trainer 구조를 다시 뜯어고치지 않아도 되는지 확인

## 메모

- 현재 Hermes 구현은 FeSViBS 원본을 직접 포팅한 것이 아니라, ViT split 학습 구조를 단순화해 재구성한 버전으로 이해하는 것이 맞다.
- 따라서 앞으로의 리팩토링은 `FeSViBS를 더 충실히 복제`하는 방향이 아니라 `논문용 병렬 round server-tail baseline을 정확히 구현`하는 방향으로 가야 한다.
- 첫 구현에서 실제 병렬 실행은 필요 없다. 중요한 것은 round semantics가 병렬 동기 집계를 반영하느냐이다.
