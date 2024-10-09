FROM python:3.10-buster

# Install Poetry and disable virtualenv creation
RUN pip install --upgrade pip && \
    pip install poetry==1.8.3 && \
    poetry config virtualenvs.create false