# OpenSpec Guide

## 목적

이 저장소의 실험 기능은 OpenSpec 변경 단위로 관리합니다.

## 기본 흐름

1. 변경 제안 생성
2. `proposal.md` 작성
3. `design.md` 작성
4. `specs/*.md` 작성
5. `tasks.md` 작성
6. 구현
7. 아카이브

## 자주 쓰는 명령

```powershell
openspec status --change "<change-name>"
openspec instructions proposal --change "<change-name>"
openspec instructions design --change "<change-name>"
openspec instructions specs --change "<change-name>"
openspec instructions tasks --change "<change-name>"
openspec instructions apply --change "<change-name>"
```

## 작성 원칙

- 변경 범위는 한 번에 한 주제로 제한합니다.
- proposal은 왜 필요한지, design은 어떻게 할지, spec은 무엇을 해야 하는지에 집중합니다.
- tasks는 하나씩 끝낼 수 있게 작게 나눕니다.

## 주의 사항

- `context`와 `rules`는 문서에 복사하지 않습니다.
- spec의 scenario는 테스트 가능한 형태로 작성합니다.
- 구현이 끝나면 `openspec status`로 완료 여부를 확인합니다.
