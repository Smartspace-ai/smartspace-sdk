FROM pandoc/minimal:2.19.2 AS pandoc

FROM python:3.10-buster

# Install Poetry and disable virtualenv creation
RUN pip install --upgrade pip && \
    pip install poetry==1.8.3 && \
    poetry config virtualenvs.create false

# Add pandoc (static binary from pandoc/minimal)
COPY --from=pandoc /pandoc /usr/local/bin/pandoc
