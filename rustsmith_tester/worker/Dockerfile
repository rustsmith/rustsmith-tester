FROM rust:RUSTMITH_VERSION

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install greenstalk

ENV RUSTC_VERSION=RUSTMITH_VERSION

COPY . /sources

WORKDIR /sources

ENTRYPOINT ["python3", "main.py"]
