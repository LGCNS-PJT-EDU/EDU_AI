# LGCNS_InspireCamp_Education
---
### 프로젝트 개요
**AI 기반 초개인화 개발자 성장 로드맵 추천 플랫폼**

이 서비스는 진입 단계의 전공자/비전공자와 주니어 개발자를 위한 맞춤형 커리어 성장 가이드입니다. 단순히 기술 커리큘럼을 나열하는 데 그치지 않고, 사용자의 성향, 경험, 기술 수준을 종합적으로 분석하여 왜 이 기술을 배우는지, 어떻게 접근해야 하는지를 AI가 코치처럼 피드백하고 추천합니다.

#### 주요 타겟
1. IT 진입을 꿈꾸는 전공/비전공 학습자
2. 방향을 잃은 주니어 개발자
3. 효율적인 역량 향상을 원하는 예비 취준생

---
### 기술 스택
```md
FastAPI – 웹 API 프레임워크

Uvicorn – ASGI 서버

MongoDB – 비정형 데이터 저장 (피드백, 진단 결과)

MySQL – 구조화 데이터 저장 (유저, 평가, 진도)

CromaDB - 로드맵 데이터 저장

OpenAI GPT-4 – 로드맵 및 피드백 생성

LangChain – GPT + RAG 기반 검색 기능


```

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
│ ├── config/
│ │ └── kafka_config.py
│ ├── consumer/
│ │ ├── feedback_consumer.py
│ │ └── recommendation_consumer.py
│ ├── data/
│ ├── kafka_admin/
│ │ └── topic_initializer.py
│ ├── models/
│ │ ├── feedback/
│ │ ├── interview/
│ │ ├── pre-assessment/
│ │ └── recommendation/
│ ├── clients/
│ ├── producer/
│ │ ├── feedback_producer.py
│ │ └── recommendation_producer.py
│ ├── routers/
│ │ ├── chroma_status_router.py
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
│ │ ├── insert_sample.py
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
│ │ └── tasks/
│ │   └── migrate_task.py
│ ├── utils/
│ │ ├── build_feedback_prompt.py
│ │ ├── embed.py
│ │ ├── gpt_prompt.py
│ │ ├── level_utils.py
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
### 깃 커밋 컨벤션

* 작성 방식
```
type: subject

body (optional)
...
...
...

footer (optional)
```

* 작성 예시
```
feat: 압축파일 미리보기 기능 추가

사용자의 편의를 위해 압축을 풀기 전에
다음과 같이 압축파일 미리보기를 할 수 있도록 함
 - 마우스 오른쪽 클릭
 - 윈도우 탐색기 또는 맥 파인더의 미리보기 창

Closes #125
```

* Type

| 타입 | 설명 |
| :- | - |
| ✨feat | 새로운 기능 추가 |  
| 🐛fix | 버그 수정 |  
| 📝docs | 문서 수정 |  
| 💄style | 공백, 세미콜론 등 스타일 수정 |  
| ♻️refactor | 코드 리팩토링 |  
| ⚡️perf | 성능 개선 | 
| ✅test | 테스트 추가 | 
| 👷chore | 빌드 과정 또는 보조 기능(문서 생성기능 등) 수정 | 

* Subject: 
커밋의 작업 내용 간략히 설명


* Body: 
길게 설명할 필요가 있을 시 작성


* Footer: 
Breaking Point 가 있을 때
특정 이슈에 대한 해결 작업일 때

* [Gitmoji](https://gitmoji.dev/)를 이용하여 Type을 대신하기도 합니다.

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
