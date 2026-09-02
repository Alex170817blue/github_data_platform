FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi || true

COPY . .

CMD ["tail", "-f", "/dev/null"]
