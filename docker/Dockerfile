# --- build stage ---
FROM python:3.13-slim AS build
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip
COPY pyproject.toml* requirements.txt* README.md ./
# fallback to requirements if no pyproject
RUN if [ -f requirements.txt ]; then pip wheel -r requirements.txt -w /wheels; fi
COPY . .
RUN pip wheel . -w /wheels

# --- runtime stage ---
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels
COPY . .
EXPOSE 8080
CMD ["python","-m","uvicorn","aioscore.api.server:app","--host","0.0.0.0","--port","8080"]
