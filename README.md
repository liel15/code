# Vibe Coding Workspace

일정관리, 나무 키우기, OpenSpec 실험을 같이 다루는 작업 공간입니다.

## 개요

이 저장소는 여러 실험 프로젝트를 한 번에 관리하는 워크스페이스입니다. 현재는 `todo_web.py` 기반의 일정관리 + 나무 성장 웹과 `claude_ocr_1day` 기반의 영수증 OCR 앱을 함께 포함합니다.

## 포함된 프로젝트

- `todo_web.py`: Flask 기반 일정관리 + 나무 성장 웹
- `claude_ocr_1day/`: 영수증 OCR 지출관리 앱
- `openSpec/`: 변경 제안 및 구현 문서
- `maratang-memo-ritual-site/`: 별도 실험용 웹

## 실행 방법

### 일정관리 웹

```powershell
python todo_web.py
```

접속 주소: `http://127.0.0.1:5000/`

### OCR 앱

```powershell
cd claude_ocr_1day\backend
uvicorn main:app --reload --host 127.0.0.1 --port 5000
```

프론트는 `claude_ocr_1day/frontend`를 기준으로 개발합니다.

## OpenSpec 작업

```powershell
openspec status --change "creative-web-design-improvement"
```

## 브랜치 전략

- `main`: 기준 브랜치
- `feat/*`: 기능 추가
- `fix/*`: 버그 수정
- `docs/*`: 문서 수정

## 저장소에서 제외되는 파일

다음 파일과 폴더는 버전 관리하지 않습니다.

- 환경 변수: `.env`, `.env.*`
- 실행 데이터: `game_state.json`, `todos.json`
- 캐시/빌드: `__pycache__/`, `*.pyc`, `dist/`, `build/`, `node_modules/`
- 개인 도구 설정: `.claude/`, `.opencode/`, `.taskmaster/`
- 테스트/임시 산출물: `test_result/`, 로그 파일, 임시 파일

## 메모

- 저장소는 여러 실험을 함께 담고 있으니, 작업 전 `git status`를 확인하는 것이 좋습니다.
- 실행 중 생성되는 데이터는 필요 시 백업 후 삭제해도 됩니다.
