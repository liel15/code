# Vibe Coding Workspace

일정관리, 나무 키우기, OpenSpec 실험을 같이 다루는 작업 공간입니다.

## 포함된 프로젝트

- `todo_web.py`: Flask 기반 일정관리 + 나무 성장 웹
- `claude_ocr_1day/`: 영수증 OCR 지출관리 앱
- `openSpec/`: 변경 제안 및 구현 문서
- `maratang-memo-ritual-site/`: 별도 실험용 웹

## 실행

```powershell
python todo_web.py
```

기본 접속 주소:
- `http://127.0.0.1:5000/`

## 브랜치 전략

- `main`: 배포/기준 브랜치
- `feat/*`: 기능 작업 브랜치
- `fix/*`: 버그 수정 브랜치

## 메모

- 런타임 데이터는 `game_state.json`, `todos.json`에 저장됩니다.
- 개인 환경 파일은 `.gitignore`로 제외합니다.
