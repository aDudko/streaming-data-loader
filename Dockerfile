FROM python:3.12-slim
LABEL author="Anatol Dudko"
LABEL email="anatoly_dudko@icloud.com"

#hadolint ignore=DL3013
RUN pip install --upgrade  --no-cache-dir pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false
#hadolint ignore=DL3008
RUN apt-get update && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml .
RUN poetry install --no-root --no-interaction --no-ansi --no-cache --only main

COPY . .
ENV PYTHONPATH=src
ARG TESTS_DIR=tests
#hadolint ignore=DL3013
RUN mkdir testsresult && \
    if [ -d /app/${TESTS_DIR} ]; then \
    pip install --no-cache-dir pytest-custom_exit_code pytest-cov && \
    pytest ${TESTS_DIR} -s -v \
    --junitxml="testsresult/result.xml" \
    --suppress-tests-failed-exit-code \
    --cov=src --cov-report=xml:covresult/result.xml 2>&1; \
    fi

CMD [ "python", "main.py" ]