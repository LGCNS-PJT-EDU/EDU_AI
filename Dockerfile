## Dockerfile
#FROM python:3.10-slim
#WORKDIR /app
## 의존성 설치
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#
#COPY . .
#
## 포트노출
#EXPOSE 8000
#
#CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:8000"]


# ⚙️ 1. Python 베이스 이미지
FROM python:3.12-slim

# ⚙️ 2. Poetry 설치
ENV POETRY_VERSION=1.8.2
RUN pip install --upgrade pip && pip install poetry==$POETRY_VERSION

# ⚙️ 3. 작업 디렉토리 설정
WORKDIR /app

# ⚙️ 4. 전체 소스 코드 복사 (먼저 복사해야 poetry가 패키지를 인식함)
COPY . .

# ⚙️ 5. Poetry 설정 및 의존성 설치
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# ⚙️ 6. 포트 노출
EXPOSE 8000

# ⚙️ 7. 앱 실행 명령
CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:8000", "--reload"]

