FROM python:3.12-slim-bullseye

WORKDIR /polls_app

ENV VIRTUAL_ENV=/opt/venv

RUN python3 -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD [ "/opt/venv/bin/python", "manage.py", "runserver", "0.0.0.0:8000" ]