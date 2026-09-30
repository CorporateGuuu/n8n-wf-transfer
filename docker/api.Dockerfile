FROM python:3.12-slim
WORKDIR /workspace
COPY pyproject.toml alembic.ini ./
COPY apps/api ./apps/api
RUN pip install --no-cache-dir .
RUN useradd -r -u 10001 appuser && chown -R appuser:appuser /workspace
USER appuser
WORKDIR /workspace/apps/api
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
