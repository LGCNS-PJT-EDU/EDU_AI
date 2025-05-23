# Dockerfile
FROM python:3.10-slim
WORKDIR /app
# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 포트노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:8000"]
