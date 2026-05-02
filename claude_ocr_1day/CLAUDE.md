# CLAUDE.md

이 파일은 Claude Code(claude.ai/code)가 이 저장소에서 작업할 때 참조하는 지침입니다.

## 프로젝트 개요

영수증 이미지를 업로드하면 Upstage Vision LLM(OCR)으로 파싱해 지출 내역을 관리하는 1-day MVP 앱.

- **Frontend**: React 18 + Vite + TailwindCSS + TypeScript
- **Backend**: Python FastAPI + LangChain 1.2.15 + langchain-upstage 0.7.7 + Upstage Vision LLM
- **Storage**: `expenses.json` 파일 저장 (DB 없음)
- **Deployment**: Vercel

## 개발 명령어

### Frontend (`frontend/` 디렉토리)
```bash
npm install
npm run dev       # 개발 서버 (Vite)
npm run build     # 프로덕션 빌드
npm run preview   # 빌드 결과 미리보기
```

### Backend (`backend/` 디렉토리)
```bash
pip install -r requirements.txt
uvicorn main:app --reload   # 개발 서버 (포트 8000)
```

### 환경 변수
`.env` 파일에 `UPSTAGE_API_KEY` 필요. `.env.example` 참고.

## 아키텍처

### 데이터 흐름
```
React (Upload) → POST /api/upload → FastAPI
                                        ↓
                              LangChain Chain
                                        ↓
                       Upstage Vision LLM (OCR)
                        모델: document-digitization-vision
                                        ↓
                           JSON 파서 → expenses.json
```

### API 엔드포인트
| Method | Path | 역할 |
|--------|------|------|
| POST | `/api/upload` | 영수증 업로드 + OCR 파싱 |
| GET | `/api/expenses` | 지출 목록 조회 (날짜 필터 지원) |
| GET | `/api/summary` | 통계 + 카테고리별 집계 |
| DELETE | `/api/expenses/{id}` | 삭제 |
| PUT | `/api/expenses/{id}` | 수정 |

### Expense 데이터 스키마
핵심 필드: `id`, `created_at`, `store_name`, `receipt_date`, `receipt_time`, `category`, `items[]`, `subtotal`, `discount`, `tax`, `total_amount`, `payment_method`, `raw_image_path`

### 디렉토리 구조 (목표)
```
frontend/src/
  pages/       # Dashboard, UploadPage, ExpenseDetail
  components/  # Header(구현됨), ExpenseCard, DropZone, ParsePreview, SummaryCard, FilterBar, Badge, Modal, Toast
backend/
  main.py          # FastAPI 진입점
  services/
    ocr_service.py   # LangChain + Upstage 연동
    file_service.py  # expenses.json 읽기/쓰기
  api/routes.py      # 라우터
  data/expenses.json # 데이터 저장소
```

## 제약 사항

- 업로드 가능 형식: JPG, PNG, PDF (최대 10MB)
- OCR 응답 목표: 10초 이내
- 파싱 성공률 목표: 80% 이상
- Vercel 서버리스 환경에서 파일 저장 시 `localStorage` 폴백 고려 필요

## 테스트용 샘플 영수증

`images/` 디렉토리에 이마트, 스타벅스, CU, GS25, 롯데백화점, 롯데리아, IKEA, 유니클로, CGV, 메가박스, 병원, 택시 영수증 이미지 수록.
