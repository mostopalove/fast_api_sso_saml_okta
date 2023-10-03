FROM python:3.10 as python-base

# SET ENV #
ENV PYTHONBUFFERED=1 \
    PIP_NO_CACHE_DIR="off" \
    POETRY_VERSION=1.4.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/app" \
    VENV_PATH="/app/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base as builder-base

RUN apt-get update && apt-get install --no-install-recommends -y curl \
    && curl -sSL https://install.python-poetry.org | python


ARG APP_TO_BUILD


WORKDIR $PYSETUP_PATH

RUN apt-get install pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl -y

COPY poetry.lock pyproject.toml ./

RUN python -m venv $VENV_PATH
RUN . ${VENV_PATH}/bin/activate
RUN pip install -U pip
RUN poetry install


FROM python-base as production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY . $PYSETUP_PATH
CMD cd $PYSETUP_PATH && uvicorn main:app --reload
