FROM python:3.9-slim
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./
RUN pip install pipenv
RUN pipenv install --deploy --system

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT