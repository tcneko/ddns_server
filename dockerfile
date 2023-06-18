FROM python:3.10.0-bullseye as s1

MAINTAINER tcneko <tcneko@outlook.com>

RUN python3 -m pip install --no-cache-dir --upgrade aiohttp fastapi ipaddress pydantic uvicorn[standard]
COPY src/ /opt/ddns_server/
WORKDIR /opt/ddns_server

ENTRYPOINT [ "python3", "-m", "uvicorn", "ddns_server:app"]