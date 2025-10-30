FROM python:3.10-slim

RUN pip install uv

WORKDIR /appcd .ssh

COPY . .

RUN uv sync

EXPOSE 7860

CMD ["uv", "run", "app.py"]