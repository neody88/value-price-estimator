# 주식 가치 평가기

서준식 *채권쟁이의 다시쓰는 주식투자 교과서* ROE 기반 10년 주가 예측 서비스.

## 기능

- 6자리 한국 종목코드 입력 → 4개년 ROE/BPS 자동 조회 (yfinance)
- 10년 후 공정가치 추정: `future_bps = bps × (1 + ROE_norm × 0.7)^10`
- 목표 수익률(8/10/12/15%)별 현재 매수 추천가 계산
- 경기민감주(ROE 스프레드 >8%p, 음수 연도 존재) 자동 경고

## 스택

| 레이어 | 기술 |
|---|---|
| 프론트엔드 | Next.js 15 App Router · TypeScript · Tailwind CSS |
| API | Python 3 서버리스 (Vercel) · yfinance · FinanceDataReader |
| 배포 | Vercel (Next.js + Python 혼합 런타임) |

## 로컬 개발

```bash
# 의존성 설치
npm install
pip3 install yfinance finance-datareader pydantic

# Python API 서버 (포트 8001)
python3 api/_dev_server.py 8001 &

# Next.js dev 서버 (포트 3000, /api/* → 8001 프록시 자동 설정)
npm run dev
```

http://localhost:3000 에서 확인.

## Vercel 배포

```bash
npm install -g vercel
vercel deploy
```

`vercel.json`이 `api/estimate.py`를 Python 서버리스 함수로 자동 등록합니다.

환경 변수는 별도로 필요하지 않습니다 (yfinance는 인증 불필요).

## 프로젝트 구조

```
api/
  estimate.py      # Vercel 서버리스 핸들러 (BaseHTTPRequestHandler)
  datasource.py    # yfinance + FinanceDataReader 데이터 조회
  valuation.py     # 핵심 계산 로직 (ROE 정규화, BPS 복리, 매수가)
  _models.py       # Pydantic 데이터 모델
  cache.py         # 인메모리 LRU 캐시 (서버리스 안전)
app/               # Next.js App Router
components/        # ResultCard, BuyPriceTable, RoeHistory, CyclicalWarning
lib/api.ts         # 프론트엔드 타입 + fetch 헬퍼
```

## 면책 조항

본 서비스의 결과는 추정치이며 투자 권유가 아닙니다. 투자 결정은 본인 책임으로 하시기 바랍니다.
