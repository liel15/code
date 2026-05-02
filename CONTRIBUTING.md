# Contributing

## 작업 규칙

- 변경은 가능한 한 작게 유지합니다.
- 기능과 무관한 파일은 건드리지 않습니다.
- 비밀값이나 개인 환경 파일은 커밋하지 않습니다.

## 브랜치

- `feat/*`: 새 기능
- `fix/*`: 버그 수정
- `docs/*`: 문서 작업

## 권장 절차

1. 작업 시작 전에 `git status`로 상태를 확인합니다.
2. 기능 변경은 테스트와 함께 반영합니다.
3. 커밋 메시지는 짧고 목적이 드러나게 작성합니다.
4. 푸시 전 최종 상태를 다시 확인합니다.

## 테스트와 배포

### 일정관리 웹

```powershell
python test_todo_web.py -q
python todo_web.py
```

### OCR 앱

```powershell
cd claude_ocr_1day\backend
python -m pytest
uvicorn main:app --reload
```

### 배포 전 확인

- 환경 변수 누락이 없는지 확인합니다.
- 런타임 데이터 파일이 커밋되지 않았는지 확인합니다.
- UI 변경은 브라우저에서 직접 확인합니다.

## 코드 스타일

- Python은 기존 스타일을 따릅니다.
- 템플릿/HTML은 한국어 문구를 우선 사용합니다.
- 새 디자인은 기존 톤과 섞이도록 맞춥니다.

## 제외 대상

- `.env`
- `game_state.json`
- `todos.json`
- 캐시, 로그, 빌드 산출물

## OpenSpec

- 새 변경은 `openSpec/changes/<change-name>/` 아래에 작성합니다.
- `proposal.md`, `design.md`, `specs/`, `tasks.md` 순으로 채웁니다.
- 구현은 `tasks.md` 완료 후 진행합니다.
