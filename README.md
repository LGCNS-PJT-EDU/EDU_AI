# 🧠 EDU_AI

AI 기반 학습 지원을 위한 백엔드/ML 플랫폼 **EDU_AI**입니다.  
학습자 맞춤 콘텐츠 추천, 인터뷰 피드백 등 AI 로직이 포함된 핵심 엔진 역할을 수행합니다.

---

## 🚀 주요 기능

### 🔍 학습 스타일 분석
- 사용자 입력을 바탕으로 **학습 스타일 예측** 

### 🧩 콘텐츠/로드맵 추천
- 분류 모델 기반 **개인 맞춤 콘텐츠 큐레이션**
- 추천된 콘텐츠에 대한 메타데이터 및 사용 히스토리 관리

### 🗣 인터뷰 피드백 모듈
- STT 기반 음성 응답 변환
- GPT 기반 평가 및 개선 피드백 생성

### 🧠 AI Q&A 지원
- 학습 질문에 대해 GPT 등 LLM으로 답변 제공

---
## 🛠 기술 스택

### 🔹 핵심 기술
![Python](https://img.shields.io/badge/Python%203.10+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)

### ⚙️ 서버 및 런타임
![Hypercorn](https://img.shields.io/badge/Hypercorn-333333?style=flat)

### 🧠 AI & LLM & RAG
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI%20GPT--4o-412991?style=flat&logo=openai&logoColor=white)
![CELERY](https://img.shields.io/badge/CELERY-BFFF00?style=flat)
![CELERYBEAT](https://img.shields.io/badge/CELERYBEAT-BFFF00?style=flat)
![OpenAI](https://img.shields.io/badge/Redis-FF4438?style=flat&logo=redis&logoColor=white)

### 📦 데이터베이스
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat&logo=mongodb&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-9D34DA?style=flat&logo=chromadb&logoColor=white)

### 🔗 API & 통신
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat&logo=pydantic&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache_Kafka-231F20?style=flat&logo=apachekafka&logoColor=white)

### 로그 및 모니터링
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=flat&logo=grafana&logoColor=white)
![OpenSearch](https://img.shields.io/badge/OpenSearch-005EB8?style=flat&logo=opensearch&logoColor=white)

### 버전 관리
![Poetry](https://img.shields.io/badge/Poetry-60A5FA?style=flat&logo=poetry&logoColor=white)

### 🧪 테스트 & 품질
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat&logo=pytest&logoColor=white)
![FastAPI TestClient](https://img.shields.io/badge/FastAPI%20TestClient-009688?style=flat&logo=fastapi&logoColor=white)

### 🐳 배포 & 운영
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat&logo=githubactions&logoColor=white)
![Amazon Elastic Kubernetes Service](https://img.shields.io/badge/Amazon%20EKS-326CE5?style=flat&logo=kubernetes&logoColor=white)
![Argo](https://img.shields.io/badge/Argo-EF7B4D?style=flat&logo=Argo&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-0F1689?style=flat&logo=Helm&logoColor=white)
![AWS EC2](https://img.shields.io/badge/AWS%20EC2-EF7B4D?logo=amazon-aws&style=flat&logoColor=white)

### 문서화
![Swagger](https://img.shields.io/badge/Swagger-85EA2D?logo=swagger&style=flat&logoColor=white)


---
### 프로젝트 구조
```md
EDU_AI/
├── .github/
├── .zen/
│ └── config.yaml
├── app/
│ ├── clients/
│ │ ├── chromadb_client.py
│ │ ├── mongodb.py
│ │ └── openai_client.py
│ │ └── opensearch_client.py
│ ├── config/
│ │ └── kafka_config.py
│ ├── consumer/
│ │ ├── feedback_consumer.py
│ │ └── recommendation_consumer.py
│ ├── kafka_admin/
│ │ └── topic_initializer.py
│ ├── models/
│ │ ├── feedback/
│ │ │ ├── request.py
│ │ │ └── response.py
│ │ ├── interview/
│ │ │ ├── evaluation_model.py
│ │ │ └── question_model.py
│ │ ├── pre-assessment/
│ │ │ ├── request.py
│ │ │ └── response.py
│ │ └── recommendation/
│ │ │ ├── request.py
│ │ │ └── response.py
│ ├── producer/
│ │ ├── feedback_producer.py
│ │ └── recommendation_producer.py
│ ├── routers/
│ │ ├── chroma_router.py
│ │ ├── chroma_status_router.py
│ │ ├── chroma_test_router.py
│ │ ├── feedback_router.py
│ │ ├── post_assessment_router.py
│ │ ├── pre_assessment_router.py
│ │ ├── question_router.py
│ │ ├── recommendation_router.py
│ │ └── status_router.py
│ ├── scripts/
│ │ ├── chroma_insert.py
│ │ ├── count_mongo_chroma.py
│ │ ├── create_index.py
│ │ ├── migrate_mongo_to_chroma.py
│ │ └── test_rag_pipeline.py
│ ├── services/
│ │ ├── assessment/
│ │ │ ├── common.py
│ │ │ ├── post.py
│ │ │ └── pre.py
│ │ ├── common/
│ │ │ └── common.py
│ │ ├── feedback/
│ │ │ └── builder.py
│ │ ├── interview/
│ │ │ ├── builder.py
│ │ │ └── evaluator.py
│ │ ├── prompt/
│ │ │ └── builder.py
│ │ ├── recommendation/
│ │ │ ├── rag_explainer.py
│ │ │ └── reranker.py
│ │ ├── sync/
│ │ │ └── sync_recommend.py
│ │ ├── mongo_recommendation.py
│ │ └── rag_module.py
│ ├── utils/
│ │ ├── build_feedback_prompt.py
│ │ ├── embed.py
│ │ ├── gpt_prompt.py
│ │ ├── level_utils.py
│ │ ├── metrics.py
│ │ ├── pretest_log_utils.py
│ │ ├── prometheus_metrics.py
│ │ └── roadmap_prompt.py
│ ├── celery_worker.py
│ └── main.py
├── prometheus/
│ └── prometheus.yml
├── .env
├── .gitignore
├── Dockerfile
├── README.md
├── docker-compose.yml
├── poetry.lock
├── pyproject.toml
├── requirements.txt
└── test_main.http
```

---

### 피드백 프롬프트 수정 기록
v1: link<br>
v2: https://github.com/LGCNS-PJT-EDU/EDU_AI/commit/369b647b877a1777c9126fe20cece7257086e281<br>
v3: https://github.com/LGCNS-PJT-EDU/EDU_AI/commit/02971bb81834d0b5c17067743bde0169e62f239a<br>
v4: 

---

### hypercorn 실행 설정
- pip install hypercorn으로 hypercorn 설치
- 실행 환경 구성 -> Python -> main으로 이동
- scripts를 module로 바꾸고, 모듈명으로 hypercorn이라 입력
- 스크립트 매개 변수에 app.main:app --reload --bind 127.0.0.1:8000 --access-logfile - --error-logfile - 를 입력(실행 및 로그 출력)

 ---

API 문서
Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

URL: http://ai.takeit.academy/docs
