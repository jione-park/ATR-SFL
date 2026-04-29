# 계획: GitHub 업로드 준비 정리

## 목표

Hermes를 로컬 연구 저장소 상태에서 GitHub 업로드 가능 상태로 정리하고, 외부 AI tool이 참고하기 쉬운 최소 문서 구조를 확인한다.

## 범위

- 현재 저장소의 git 초기화 상태 점검
- 업로드 제외 대상 정리
- 공개용 README와 AI reading path 보강
- 문서 검증 수행
- 첫 commit 직전까지 필요한 남은 조건 식별

## 입력 자료

- `AGENTS.md`
- `README.md`
- `.gitignore`
- `docs/problem_formulation.md`
- `docs/experiment_protocol.md`
- 현재 staged file 목록과 ignored file 목록

## 산출물

- GitHub 업로드 준비용 plan
- 필요한 경우 보강된 `README.md`
- 검증 통과 상태
- 첫 commit/push 전에 사용자에게 받아야 할 정보 목록

## 단계

1. 현재 git 상태와 ignore 상태를 다시 점검한다.
2. 외부 AI가 읽을 때 필요한 최소 reading path가 `README.md`에 드러나는지 확인한다.
3. 부족한 경우 `README.md`를 최소 수정해 public repo entry point를 보강한다.
4. `python3 scripts/validate_docs.py`를 실행해 markdown 관리 규칙이 깨지지 않았는지 확인한다.
5. 첫 commit 생성에 필요한 정보와 실제 push에 필요한 정보가 무엇인지 정리한다.

## 검증

- 대용량 데이터, 로컬 환경, 실험 산출물이 git 추적 대상에서 제외되어 있는지 확인
- `README.md`만 읽어도 외부 사용자나 AI가 어디부터 읽어야 하는지 알 수 있는지 확인
- `python3 scripts/validate_docs.py`가 통과하는지 확인
- 첫 commit/push를 막는 미해결 조건이 명시되어 있는지 확인

## 메모

- commit author 정보와 GitHub remote URL은 자동 추정하지 않는다.
- 연구 문서의 canonical source는 계속 `AGENTS.md`와 `docs/` 아래 문서로 유지한다.
