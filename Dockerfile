FROM python:3.10-slim

WORKDIR /app


RUN pip install pipenv --user

COPY Pipfile* ./
RUN python -m pipenv install --system --deploy

COPY api ./api
COPY pkgs ./pkgs
EXPOSE 8080


CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]

