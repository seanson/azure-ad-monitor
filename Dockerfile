FROM python:3.12-alpine as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

WORKDIR /app

FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.2

RUN apk add --no-cache gcc libffi-dev musl-dev
RUN pip install "poetry==$POETRY_VERSION"
RUN poetry self add poetry-plugin-export
RUN python -m venv /venv

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt | /venv/bin/pip install -r /dev/stdin

COPY . .
RUN poetry build && /venv/bin/pip install dist/*.whl

FROM base as final

RUN apk add --no-cache libffi tzdata
COPY --from=builder /venv /venv
COPY uwsgi.ini docker-entrypoint.sh azure-ad-monitor ./

CMD ["./docker-entrypoint.sh"]
