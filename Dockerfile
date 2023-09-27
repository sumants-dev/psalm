FROM python:3.10-slim

WORKDIR /work


RUN pip install pipenv --user

COPY Pipfile* ./
RUN python -m pipenv install --system --deploy
RUN python -m spacy download en_core_web_lg


COPY api ./api
COPY pkgs ./pkgs
COPY db ./db

COPY main.py main.py
COPY pontus.yaml pontus.yaml
EXPOSE 8080


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

