FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VIRTUALENVS_CREATE false

RUN --mount=type=cache,target=/root/.cache pip install poetry
WORKDIR /opt/nu
COPY pyproject.toml /opt/nu

RUN --mount=type=cache,target=/root/.cache poetry install

CMD ["poetry", "run", "start"]