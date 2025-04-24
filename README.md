# 🎭 공연예술 데이터 시각화 대시보드

공연예술 관련 데이터를 통합 분석하고 시각화하여 공연 기획자 및 운영자, 문화 정책 입안자의 **효율적인 의사결정**을 지원하는 웹 기반 대시보드입니다.

## 📌 프로젝트 개요

- **프로젝트 명**: PerformArts Insight Dashboard
- **목적**: 공연 데이터 기반 인사이트 제공을 통한 전략적 기획/운영 지원
- **주요 사용자**: 공연 기획자, 운영자, 문화 정책 기관, 스타트업, 연구자

## 🚀 주요 기능

### 🎫 관객 수 예측
- 누적 판매 추이 분석 (Line Chart)
- 좌석 수 vs 판매량 관계 분석 (Scatter Plot)
- 유사 공연 실적 비교 (Bar Chart)

### 💰 손익 예측
- 공연별 투자 대비 수익률(ROI) 시각화
- 수익/손실 구간별 공연 분포 분석

### ⚠️ 티켓 판매 위험 예측
- 판매량 기반 위험 등급 시각화
- 저조 판매 공연 탐지 기능

### 📊 장르·지역·시설 통계 분석
- 장르별 공연 수/관객 수/매출 분석
- 지역별 인기 공연 트렌드 분석
- 공연시설 연도별 변화 추이

## 📁 사용 데이터

| 데이터 명 | 설명 |
|-----------|------|
| `performance_tb.json` | 공연 기본 정보 |
| `sales_tb.json` | 티켓 판매 및 누적 관객 데이터 |
| `audience_tb.json` | 관객 통계 |
| `장르별_통계.json` | 장르별 매출/관객/공연 수 통계 |
| `지역별_통계.json` | 지역별 공연 현황 |
| `공연시설_연도_규모_분류.json` | 공연시설 연도별 규모별 분포 |

## 🛠️ 기술 스택

- **Frontend**: Next.js, React.js, Material CSS
- **Data Visualization**: Recharts
- **State Management**: Custom Hook (`useCsvData`)
- **배포환경**: [Vercel](https://vercel.com/), GitHub Pages (optional)

## 🧩 구성 구조
/components ├── Chart/ ├── Table/ ├── Insights/ └── Sidebar.jsx
/data ├── performance_tb.json ├── sales_tb.json └── ...
/pages ├── index.jsx └── ...
/hooks └── useCsvData.js


## ✅ 프로젝트 목표

- 🎯 관객 수 예측 정확도 80% 이상
- 👍 사용자 만족도 4.5점 이상 (설문 기반)
- 📈 기획 및 정책에 적용 가능한 사례 확보
  
## 📎 향후 업데이트 계획

- 데이터 시각화와 AI 챗봇 연동
- 모델 기반 공연 성공 예측 기능 추가

<h1>프로젝트 실행방법</h1>

<h2>가상환경에 필요한 패키지 설치</h2>
  
```bash
cd backend
pip install -r "requirements.txt"
```

<h2>터미널 2개 구동</h2>

-터미널1

```bash
cd backend
uvicorn demo:app --reload
```

-터미널2

```bash
cd frontend
npm run dev
```

![image](https://github.com/user-attachments/assets/82a71e87-1e56-4b40-a1fe-6e2e95c86743)

<h2>사이트 접속</h2>

http://localhost:3000/

<h2>실행된 화면</h2>

![image](https://github.com/user-attachments/assets/76c7e331-87e1-40d2-938a-53011ddafe17)

