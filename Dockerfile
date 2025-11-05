FROM python:3.10-slim

RUN pip install uv

WORKDIR /app

COPY . .

RUN uv sync

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get upgrade -yq ca-certificates && \
    apt-get install -yq --no-install-recommends \
    prometheus-node-exporter

EXPOSE 7860
EXPOSE 8000
EXPOSE 9100

ENV GRADIO_SERVER_NAME="0.0.0.0"

CMD bash -c "prometheus-node-exporter --web.listen-address=':9100' & uv run /app/app.py"