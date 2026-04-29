# 아이디어: Wireless ViT-SFL을 위한 channel-adaptive token reduction

## 한줄 요약

Wireless ViT-based training-time split federated learning을 병렬 round형 synchronous system으로 정식화하고, split interface의 smashed-token reduction을 channel-adaptive bounded-distortion operator로 모델링하여 round latency와 convergence penalty를 함께 제어하는 token/bandwidth scheduler를 설계한다.

## 동기

### 문제 정식화 관점의 핵심

현재 Hermes가 겨냥하는 문제는 일반적인 ViT token pruning이 아니라 다음처럼 더 좁고 선명한 문제다.

- 모델 계열: ViT 또는 token-based vision backbone
- 학습 설정: training-time split federated learning
- 시스템 제약: round마다 달라지는 wireless communication bottleneck
- 시스템 추상화: synchronous parallel-round SFL
- 제어 변수: 각 round에서 client별 split-interface token budget

특히 이 연구의 초점은 **배포 단계가 아니라 training-time SFL**이며, 각 round `t`에서

1. 참여 client 집합 `S_t`가 정해지고
2. 각 client가 split point까지 forward를 수행하고
3. smashed token sequence를 server로 보내고
4. server가 동일 round 안에서 잔여 network와 loss를 계산한 뒤
5. client와 server update를 round 종료 시 동기적으로 집계하는

학습 루프 자체를 다룬다.

핵심 비효율은 `fixed token budget`이 무선 채널 변화와 training-time communication cost에 맞지 않는다는 점이다.

- 채널이 나쁠 때는 같은 token 수를 보내는 것이 uplink latency를 과도하게 키운다.
- compressed token representation 차원이 커지면 backward signal path도 함께 무거워진다.
- 채널이 좋을 때는 사용할 수 있는 자원을 충분히 쓰지 못한다.
- synchronous round 구조에서는 느린 client 하나가 전체 round latency를 지배할 수 있다.

따라서 이 문제는 `정적인 token reduction`이 아니라 `channel-adaptive token reduction`으로 다루는 것이 자연스럽다.

### 왜 메인 논문 모델은 병렬 round형이어야 하는가

첫 이론 논문에서는 V2-like sequential service보다 병렬 round형 추상화가 더 적합하다.

- 문제 정의가 간단하다.
  - 각 round마다 여러 client가 동시에 참여하고, 각 client별 token budget과 bandwidth를 정한다고 설명할 수 있다.
- latency 모델이 깔끔하다.
  - round latency를 `max_k tau_{k,t}` 또는 그 upper bound로 둘 수 있다.
- theorem이 정돈된다.
  - iterate를 round index `t` 하나로 추적하면 된다.
- novelty focus가 선명하다.
  - 핵심은 channel-adaptive token reduction이지, sequential order effect가 아니다.
- WCL 스타일의 짧은 논문 구조와 잘 맞는다.
  - 하나의 clear system model, 하나의 theorem, 하나의 optimization으로 정리하기 쉽다.

따라서 논문 메인 시스템 모델은 **strict한 의미의 원 논문 SFLV1 자체라기보다, SFLV1-like synchronous parallel-round abstraction**으로 두는 것이 좋다. 즉 핵심은 server-side replica를 꼭 그대로 복제하는 것이 아니라, 같은 round에 참여한 여러 client의 split-learning update를 동기적으로 결합하는 구조다.

### 왜 첫 operator는 EViT-inspired여야 하는가

첫 버전의 operator family는 learnable selector가 있는 DynamicViT-style보다 EViT-style keep-and-fuse가 더 적합하다.

- 별도의 learnable selector가 없어 이론 전개가 더 깔끔하다.
- 약한 token을 전부 hard drop하지 않고 residual summary token을 남긴다.
- split interface를 통과하는 training-time communication object로 해석하기 쉽다.
- pure pruning보다 distortion 관점에서 더 완만한 해석이 가능하다.
- kept token과 fused residual token을 통해 backward path를 정의하기도 상대적으로 쉽다.

### Related work / novelty framing

이 아이디어는 네 갈래 문헌의 교차점에 있다.

1. Centralized ViT token reduction
   - DynamicViT, EViT, Token Fusion / ToFu는 pruning, keep-and-fuse, prune-merge hybrid가 centralized ViT의 accuracy-efficiency trade-off를 개선한다는 것을 보였다.
   - 하지만 목적은 주로 compute efficiency이며, training-time wireless SFL의 convergence/latency analysis는 아니다.

2. ViT-based federated / split learning
   - FeSTA는 medical imaging에서 ViT 기반 federated split learning의 가능성을 보여주었다.
   - FeSViBS는 split ViT 위에 block sampling 메커니즘을 추가했다.
   - 그러나 channel-adaptive token budget과 병렬 round형 latency-convergence optimization을 직접 다루지는 않는다.

3. FL/SFL compression theory
   - FL 이론에는 gradient compression, clipping bias, partial participation, client heterogeneity에 대한 도구가 이미 있다.
   - 하지만 그 도구들은 gradient/model update를 중심으로 하며, tokenized split activation에는 바로 적용되지 않는다.

4. Wireless adaptive learning / semantic communication
   - adaptive compression이나 semantic communication을 채널 상태에 맞게 바꾸는 연구는 있다.
   - 그러나 대부분 추론 효율화 중심이거나 training-time tokenized split representation과 직접 연결되지 않는다.

따라서 novelty claim은 아래처럼 좁고 강하게 잡는 편이 낫다.

`이 연구는 ViT token reduction 자체의 최초성을 주장하지 않으며, ViT-based SFL 자체의 최초성도 주장하지 않는다. 대신 wireless training-time ViT-SFL의 병렬 round형 split interface에서 channel-adaptive token reduction을 latency-distortion trade-off 관점에서 정식화하고, 이로 인한 distortion 항이 convergence upper bound에 어떻게 들어가는지 이론적으로 분석하는 것을 핵심 novelty로 둔다.`

### 이번 정리에서 참고한 외부 기준점

- FeSTA paper: https://proceedings.neurips.cc/paper/2021/hash/ceb0595112db2513b9325a85761b7310-Abstract.html
- FeSViBS code: https://github.com/faresmalik/FeSViBS
- FedPerfix paper/code pointer: https://openreview.net/forum?id=KBqeKc0OzQ
- FLamby benchmark: https://github.com/owkin/FLamby
- FLAIR benchmark: https://github.com/apple/ml-flair
- MedMNIST v2: https://www.nature.com/articles/s41597-022-01721-8

2026-04-29 기준 이번 정리에서는 논문용 메인 모델을 sequential/V2-like가 아니라 병렬 round형으로 보는 것이 더 적절하다고 판단한다. 구현은 bootstrap 단계에서 V2-style 시뮬레이터를 참고할 수 있지만, 최종 claim-ready 실험은 논문 시스템 모델과 정렬되어야 한다.

## 방법 개요

### 1. Problem formulation

split point는 고정하고, 각 round `t`에서 참여 client 집합 `S_t`가 동시에 split interface까지 forward를 수행한 뒤 token sequence를 server로 전송한다고 두자. 이후 server는 동일 round 안에서 잔여 network와 loss를 계산하고, 각 client에 대한 backward signal을 생성한다. round 종료 시 client-side update와 server-side update를 동기적으로 집계한다. 표기는 다음처럼 잡는 것이 자연스럽다.

- `x ~ D_k`: client `k`의 sample
- `h_c(x; theta_c)`: split 이전 client-side encoder
- `Z_{k,t}(x; theta_{c,t}) in R^{N x d}`: round `t`에서의 split activation token sequence
- `C_{k,t}`: client/round/channel-dependent token reduction operator
- `R_{k,t}`: reduced representation을 decode하거나 정렬하거나 분석하기 위한 metadata
- `h_s(.; theta_s)`: split 이후 server-side model
- `G_{k,t}`: server가 reduced representation에 대해 반환하는 backward signal

reduced split representation은 다음처럼 쓴다.

```text
tilde{Z}_{k,t} = C_{k,t}(Z_{k,t}; H_{k,t}),
```

여기서 `H_{k,t}`는 channel quality, allocated bandwidth 같은 observable system state다.

병렬 round형 학습 objective는 전역 task objective를 유지하되, 분석의 기본 iterate는 round 단위로 둔다.

```text
F(theta) = sum_k p_k E_{(x,y) ~ D_k}[ ell(h_s(C_{k,t}(h_c(x; theta_c)); theta_s), y) ].
```

하지만 시스템 관점의 목적은 단순 loss minimization이 아니다. 첫 논문에서는 아래와 같은 round-level trade-off objective가 더 적절하다.

```text
min  AverageRoundLatency + lambda * AverageDistortionPenaltyUpperBound.
```

여기서 round latency는 synchronous parallel-round 구조를 반영해 정의한다.

```text
tau_t = max_{k in S_t} tau_{k,t}
```

첫 버전에서 고정할 것:

- split point
- backbone
- token scoring rule의 큰 형태
- synchronous parallel-round aggregation rule

첫 버전에서 최적화할 것:

- token budget
- bandwidth allocation
- 필요하면 round-level client scheduling surrogate

### 2. EViT-inspired split operator

split interface에서 사용할 첫 operator family는 다음과 같이 정의할 수 있다.

1. 각 token에 importance score `s_{k,t,n}`를 부여한다.
2. 상위 `m_{k,t}`개 token을 유지한다.
3. 나머지는 하나의 residual fused token으로 압축한다.
4. server로 다음을 전송한다.
   - kept token embeddings
   - positional indices
   - fused residual token
   - 필요한 경우 소량의 aggregation metadata
5. server는 reduced representation에 대해 backward를 계산하고, client는 kept token과 fused token 경로를 통해 gradient를 전달받는다.

`S_{k,t}`를 kept index set, `bar{S}_{k,t}`를 dropped set이라 하면

```text
tilde{Z}_{k,t} = { z_n : n in S_{k,t} } union { r_{k,t} },
```

이고 residual fused token은

```text
r_{k,t} = sum_{n in bar{S}_{k,t}} alpha_{k,t,n} z_n
```

처럼 둘 수 있다.

여기서 `alpha_{k,t,n}`는 normalized fusion weight다.

channel-adaptive token budget은 다음처럼 둘 수 있다.

```text
m_{k,t} = pi(H_{k,t})
```

또는 좀 더 명시적으로

```text
m_{k,t} = pi(g_{k,t}, b_{k,t})
```

로 둘 수 있다. `g_{k,t}`는 channel state, `b_{k,t}`는 allocated bandwidth다.

### 3. Distortion abstraction

이 논문은 token-level transformer 전체를 완전하게 이론화하려는 것이 아니다. 대신 **training-time split activation compressor**를 bounded-distortion operator로 추상화한다.

```text
E[ || D_{k,t}(C_{k,t}(Z_{k,t})) - Z_{k,t} ||^2 | F_t ] <= epsilon_{k,t},
```

여기서 `D_{k,t}`는 explicit reconstruction map일 수도 있고, reduced representation을 full token space로 되돌려 분석하기 위한 embedding operator일 수도 있다.

중요한 점은 `epsilon_{k,t}`가 다음에 모두 의존할 수 있다는 것이다.

- client `k`
- round `t`
- sample
- channel state
- chosen token budget

즉 distortion term이 sample/client/round/channel adaptive여도 theorem 안에 평균항으로 흡수되게 만드는 것이 목표다. 그리고 이 distortion은 최종 배포 표현 품질이 아니라 **training-time update quality**를 손상시키는 양으로 해석해야 한다.

### 4. Theorem skeleton

목표 theorem은 full transformer optimization theorem이 아니라 **병렬 round형 training-time SFL update dynamics**에 대한 nonconvex stationarity result여야 한다.

권장 proof structure는 다음과 같다.

1. token reduction이 없는 ideal parallel-round split-SFL update를 정의한다.
2. `C_{k,t}`가 들어간 practical round update를 정의한다.
3. token distortion이 split-interface gradient perturbation으로 어떻게 전파되는지 bound한다.
4. client aggregation과 round latency surrogate를 분리해 정리한다.
5. round 평균으로 정리한다.

핵심 theorem template은 다음과 같다.

```text
(1/T) sum_{t=0}^{T-1} E || grad F(theta_t) ||^2
<=
baseline_parallel_SFL_terms
+ C_dist * (1/T) sum_t sum_{k in S_t} p_k epsilon_{k,t}.
```

baseline part에는 기존 FL/SFL 문헌에서 익숙한 항들이 남아야 한다.

- finite-horizon optimization error
- stochastic gradient noise
- partial participation
- local drift / local steps
- client heterogeneity

새 논문의 고유 항은 `average distortion penalty`다.

lemma skeleton은 아래처럼 잡는 것이 적절하다.

- Lemma 1: split-interface sensitivity
  - split token perturbation이 server-side loss gradient와 client-side update를 얼마나 바꾸는지 bound
- Lemma 2: token distortion to gradient perturbation
  - `E || delta_{k,t} ||^2 <= C * epsilon_{k,t}` 형태
- Lemma 3: synchronized aggregated update decomposition
  - stochasticity, heterogeneity, token distortion 분해
- Lemma 4: one-round descent inequality
- Theorem 1: average gradient norm bound under parallel rounds
- Corollary 1: average distortion가 0이면 baseline parallel SFL order로 환원
- Corollary 2: channel adaptation이 distortion 증가보다 round latency 감소를 더 크게 만들면 wall-clock training convergence에 이득

이 구조의 장점은 theorem의 주연이 sequential service order가 아니라 **distortion-latency trade-off**가 된다는 점이다.

### 5. Assumption 정리

가정은 theorem을 닫을 수 있을 만큼은 강해야 하지만, 특정 heuristic에만 묶일 정도로 구체적이면 안 된다. 현재 가장 자연스러운 최소 집합은 다음과 같다.

- Smoothness
  - global objective 또는 server-side continuation이 `L`-smooth
- Lower bounded objective
  - standard nonconvex descent analysis를 위해 필요
- Stochastic gradient variance bound
  - mini-batch stochasticity를 제어
- Partial participation model
  - 각 round에서 `S_t`가 정해지고 unbiased sampling 또는 bounded participation bias를 가정
- Client heterogeneity bound
  - 각 client gradient와 global gradient 차이를 제한
- Conditional distortion bound
  - `E[ || D(C(Z)) - Z ||^2 | F_t ] <= epsilon_{k,t}`
- Split-interface sensitivity bound
  - activation distortion이 server-side backward signal과 client-side gradient perturbation으로 증폭되는 정도를 Lipschitz-like constant로 제한
- Feasible bandwidth/token budget set
  - 각 round에서 가능한 `m_{k,t}`, `b_{k,t}`의 feasible region이 존재

추천 framing은 다음과 같다.

- theorem assumptions
  - smoothness
  - lower boundedness
  - variance bound
  - participation model
  - heterogeneity bound
  - conditional distortion bound
  - split sensitivity bound
- system assumptions
  - channel state observability
  - achievable rate model
  - synchronous round latency surrogate

### 6. Latency-convergence optimization

per-client per-round latency는 다음처럼 둘 수 있다.

```text
tau_{k,t} = tau_comp_client(k,t) + tau_tx(k,t) + tau_comp_server(k,t).
```

synchronous aggregation에서는 round latency를

```text
tau_t = max_{k in S_t} tau_{k,t}
```

처럼 두거나, 필요하면 tractable upper bound surrogate로 바꿀 수 있다.

training-time communication latency는 token budget에 직접 의존해야 한다.

```text
tau_tx(k,t) = S(m_{k,t}) / r(g_{k,t}, b_{k,t}),
```

여기서

- `S(m_{k,t})`: forward activation token, residual fused token, index/metadata를 포함한 uplink payload size
- `r(g_{k,t}, b_{k,t})`: channel state와 bandwidth allocation 하의 achievable rate

보다 정직하게 쓰고 싶으면 forward와 backward를 분리해

```text
tau_tx(k,t) = tau_up(k,t) + tau_down(k,t)
```

로 두고,

- `tau_up(k,t)`: reduced activation uplink latency
- `tau_down(k,t)`: returned split-gradient downlink latency

를 각각 모델링할 수 있다. 첫 버전에서는 downlink가 상대적으로 작거나 uplink에 비례한다는 surrogate를 둘 수 있다.

theorem-guided scheduler는 예를 들면 다음을 풀게 된다.

```text
min_{m_{k,t}, b_{k,t}}  tau_t + lambda * sum_{k in S_t} p_k phi_k(m_{k,t}, g_{k,t})
```

또는 horizon average version을 쓸 수 있다. 여기서 `phi_k`는 distortion upper bound다.

이 논문이 꼭 exact global optimum을 줄 필요는 없다. 더 중요한 것은 다음이다.

- tractable surrogate
- monotonic structure 또는 threshold structure
- channel quality가 나빠질수록 token budget이 작아지는 정책적 함의
- 병렬 round latency와 distortion penalty가 같은 목적식 안에서 만나는 구조

## 기대 효과

- 순수 heuristic system paper보다 강하고, 비현실적인 full transformer theory보다 좁고 설득력 있는 포지셔닝이 가능하다.
- 다른 token operator에도 재사용 가능한 distortion-aware theorem template를 만든다.
- time-varying channel에서 wall-clock training time to target accuracy를 줄일 수 있는 practical scheduler를 설계할 수 있다.
- architecture-specific 요소와 theorem-generic 요소를 분리할 수 있다.
- sequential order effect를 배제해 novelty axis를 더 깨끗하게 유지할 수 있다.

## 실패 가능성

- distortion abstraction이 empirical behavior를 너무 느슨하게만 설명할 수 있다.
- chosen cut에서 class-token attention이 불안정해 keep-and-fuse가 잘 작동하지 않을 수 있다.
- metadata overhead가 커져 communication gain을 상쇄할 수 있다.
- server-side computation이 지배적이면 token adaptation이 wall-clock training latency에 큰 이득을 못 줄 수 있다.
- split point가 너무 얕거나 깊으면 정보 손실 또는 절감 효과 부족 문제가 생길 수 있다.
- 강한 static token budget baseline이 이미 충분히 좋을 수 있다.
- strict한 SFLV1 구현 비용이 커서 초기 실험 속도가 느려질 수 있다.

## 필요한 소거실험

### Operator ablation

- full-token SFL
- pruning-only static top-k
- keep-and-fuse static budget
- keep-and-fuse adaptive budget
- adaptive budget without channel awareness
- adaptive budget without residual fused token

### Theorem-to-system ablation

- theorem-guided training scheduler vs heuristic scheduler
- distortion-aware objective vs latency-only objective
- bandwidth-only adaptation vs token-only adaptation vs joint adaptation

### Environment ablation

- static good channel
- static poor channel
- time-varying channel
- heterogeneous clients with different average SNR
- IID / non-IID data split

## 공정 비교 기준

- 같은 split point를 쓰는 training-time full-token parallel-round SFL baseline
- 같은 average transmitted bits에 맞춘 static token budget baseline
- static top-k token reduction baseline
- EViT-inspired fixed-budget keep-and-fuse baseline
- 구현 가능하다면 DynamicViT-inspired fixed-budget importance pruning baseline
- public codebase 기반 ViT-SFL 재현 시 block sampling류 baseline

theory comparison에서는 더 강한 heuristic보다 `epsilon_{k,t} = 0`인 동일 parallel-round SFL stack이 핵심 baseline이다. 이것이 no-compression case를 복원한다.

## 최소 필요 근거

### Theory

- explicit distortion penalty term이 들어간 theorem
- distortion가 0일 때 baseline parallel-round SFL로 깨끗하게 환원되는 결과
- poor channel일수록 smaller token budget이 구조적으로 자연스럽다는 corollary
- round latency surrogate와 distortion penalty가 같은 목적식으로 연결된다는 설명

### Empirics

- time-varying channel에서 adaptive token reduction이 fixed token budget보다 wall-clock training time to target accuracy가 더 좋음
- matched communication budget에서 adaptive method가 final accuracy가 경쟁력 있거나 더 좋음
- comparable payload에서 residual fused token이 pruning-only보다 낫다는 evidence
- measured distortion proxy가 theorem-guided objective를 어느 정도 정당화할 만큼 성능 추세를 설명함
- 병렬 round형 baseline 위에서도 효과가 유지됨

## 다음 단계

### 즉시 사용할 benchmark / code 권장안

한 번에 하나의 거대한 benchmark로 가기보다 단계적으로 가는 것이 맞다.

1. Stage A: 공개 training-time ViT-SFL codebase에서 먼저 재현
   - 시작점: FeSViBS와 현재 Hermes bootstrap trainer
   - 목표: CIFAR-10에서 병렬 round형 full-token ViT-SFL sanity 확보
   - 이유:
     - 현재 구현 자산을 활용할 수 있다.
     - 병렬 round형으로 trainer를 재구성한 뒤 token operator를 얹기 좋다.

2. Stage B: 메인 비전 benchmark로 확장
   - dataset 후보:
     - CIFAR-100
     - Tiny-ImageNet
   - 이유:
     - communication-accuracy trade-off가 더 잘 드러난다.
     - 메인 결과용 시각화에 적합하다.

3. Stage C: non-IID와 wireless 확장
   - Dirichlet alpha 0.5, 0.1
   - block fading + discrete SNR states
   - 이유:
     - 논문 메인 claim을 실제 federated heterogeneity로 확장할 수 있다.

### 선행 코드 조사 요약

- 현재 Hermes bootstrap은 `single server_back sequential update + client front FedAvg` 구조라 SFLV2-style에 가깝다.
- 논문 시스템 모델과 실험을 정렬하려면 병렬 round형 synchronous trainer가 추가로 필요하다.
- 초기 구현에서는 strict한 분산 병렬성을 재현할 필요는 없고, **per-client local front/server copy를 round 단위로 모아 동기 집계하는 simulator**면 충분하다.
