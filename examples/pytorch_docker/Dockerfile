FROM registry.hub.docker.com/pytorch/pytorch:2.1.1-cuda12.1-cudnn8-devel

RUN pip install mlflow
RUN pip install pytorch_lightning
RUN pip install psycopg2-binary
RUN cp /opt/conda/bin/python /usr/local/bin/python
