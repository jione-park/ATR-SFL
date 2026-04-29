# Problem Formulation

## Working title

Communication-efficient wireless federated split learning with ViT-family models via channel-adaptive token reduction under synchronous parallel rounds.

## Objective

병렬 round형 training-time federated split learning에서 wireless bottleneck을 고려한 token reduction 정책을 설계하고, 그 정책이 만드는 latency-accuracy-convergence trade-off를 이론과 실험으로 함께 설명한다.

## Core setting

- 모델 계열: ViT 또는 token-based vision backbone
- 학습 설정: training-time federated split learning
- 시스템 모델: synchronous parallel-round SFL
- round 참여 집합: 각 round `t`마다 참여 client 집합 `S_t`를 샘플링
- split interface: 각 client는 split point까지 forward를 수행한 뒤 smashed token sequence를 전송
- 제어 변수: client별 token budget `m_{k,t}`와 필요시 bandwidth allocation `b_{k,t}`
- round 종료 방식: 같은 round에 참여한 client들의 update를 동기적으로 집계
- latency surrogate: round latency는 기본적으로 참여 client latency의 `max` 또는 그 upper bound로 둠

## Primary research questions

1. 주어진 wireless state와 round 참여 구조에서 client별 token budget을 어떻게 정해야 cumulative latency 대비 정확도를 가장 잘 만들 수 있는가?
2. split interface token reduction이 만드는 distortion을 어떤 형태로 추상화하면 training-time SFL의 convergence penalty를 깔끔하게 bound할 수 있는가?
3. fixed-budget 또는 channel-only heuristic 대비 convergence-aware channel-adaptive policy가 실제로 time-to-accuracy를 개선하는가?

## Success criteria

A method is interesting only if it improves at least one of the following while keeping the others defensible:

- accuracy at fixed communication budget
- communication cost at fixed accuracy target
- convergence efficiency under realistic wireless constraints
- robustness across IID to non-IID extensions and multiple channel conditions

## Non-goals

- sequential service order, queueing, or server drift를 메인 novelty로 삼는 것
- tiny accuracy gain만 보고 communication interpretation을 놓치는 것
- 논문 시스템 모델과 실험 구현이 서로 다른 프로토콜을 가리키는데도 이를 명시하지 않는 것
- under-tuned baseline과 비교해서 과장된 결론을 내리는 것

## Open items

- strict한 per-client server replica aggregation으로 갈지, 동등한 병렬 round surrogate로 갈지에 대한 구현 선택
- distortion proxy를 어떤 측정량으로 둘지
- achievable rate와 payload accounting을 어느 수준까지 정교하게 둘지
- EViT-inspired operator에서 importance score를 어떤 규칙으로 둘지
- IID bootstrap 이후 non-IID 확장 순서를 어떻게 고정할지
