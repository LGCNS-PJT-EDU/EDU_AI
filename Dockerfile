# Dockerfile
FROM python:3.10-slim
WORKDIR /app
# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 포트노출
EXPOSE 8000

CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:8000"]

# 애플리케이션 실행
 CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# # ⚙️ 1. Python 베이스 이미지
#FROM python:3.10-slim
#
# # ⚙️ 2. Poetry 설치
#ENV POETRY_VERSION=1.8.2
#RUN pip install --upgrade pip && pip install poetry==$POETRY_VERSION
#
# # ⚙️ 3. 작업 디렉토리 설정
#WORKDIR /app
#
# # ⚙️ 4. pyproject.toml과 poetry.lock 복사 → 의존성 설치
#COPY pyproject.toml poetry.lock* ./
#RUN poetry config virtualenvs.create false \
#  && poetry install --no-interaction --no-ansi
#
# # ⚙️ 5. 애플리케이션 코드 복사
#COPY . .
#
# # ⚙️ 6. 포트 노출
#EXPOSE 8000
#
# # ⚙️ 7. 앱 실행 명령
#CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:8000", "--reload"]
