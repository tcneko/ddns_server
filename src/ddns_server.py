#!/usr/bin/env python3


# author: tcneko <tcneko@outlook.com>
# start from: 2023.05
# last test environment: ubuntu 22.04
# description:


# import
import hashlib
import importlib
import ipaddress
import os
import uuid
import yaml

from fastapi import FastAPI, Request
from pydantic import BaseModel


# variable
cfg = {}
dns_record = {}
dns_api_lib = {}


# function
def load_dns_api():
    global cfg, dns_api_lib
    for key, value in cfg["dns_api"].items():
        dns_api_lib[key] = importlib.import_module(value["lib"])


app = FastAPI()


@app.on_event("startup")
def load_cfg():
    env_cfg_file_path = os.getenv("DDNS_SERVER_CFG_FILE_PATH")
    if not env_cfg_file_path:
        env_cfg_file_path = "ddns_server.yaml"
    with open(env_cfg_file_path) as fp:
        global cfg
        cfg = yaml.load(fp, yaml.SafeLoader)
    load_dns_api()


@app.on_event("startup")
def load_dns_record():
    env_dns_record_file_path = os.getenv("DDNS_SERVER_DNS_RECORD_FILE_PATH")
    if not env_dns_record_file_path:
        env_dns_record_file_path = "data/dns_record.yaml"
    with open(env_dns_record_file_path) as fp:
        global dns_record
        yaml_load_out = yaml.load(fp, yaml.SafeLoader)
        if yaml_load_out != None:
            dns_record = yaml_load_out


@app.on_event("shutdown")
def dump_hostname():
    env_dns_record_file_path = os.getenv("DDNS_SERVER_DNS_RECORD_FILE_PATH")
    if not env_dns_record_file_path:
        env_dns_record_file_path = "data/dns_record.yaml"
    with open(env_dns_record_file_path, "w") as fp:
        yaml.dump(dns_record, fp, yaml.SafeDumper)


class AddDnsRecordBody(BaseModel):
    token: str
    name: str
    type: str
    content: dict
    dns_api_id: str
    dns_api_auth_id: str


@app.post("/api/v1/add_dns_record")
def api_add_dns_record(body: AddDnsRecordBody):
    if body.token == cfg["global_token"]:
        record_id = hashlib.sha256("{}_{}".format(
            body.name, body.type).encode("utf-8")).hexdigest()
        if record_id not in dns_record:
            dns_record[record_id] = {
                "name": body.name, "type": body.type, "content": body.content, "dns_api_id": body.dns_api_id, "dns_api_auth_id": body.dns_api_auth_id}
            name_token = str(uuid.uuid5(
                uuid.UUID(cfg["global_token"]), body.name))
            json_msg = {"status": "success", "token": name_token}
            return json_msg
        else:
            json_msg = {"status": "fail", "reason": "record_exist"}
            return json_msg
    else:
        json_msg = {"status": "fail", "reason": "token_error"}
        return json_msg


class RemoveDnsRecordBody(BaseModel):
    token: str
    name: str
    type: str


@app.post("/api/v1/remove_dns_record")
def api_remove_dns_record(body: RemoveDnsRecordBody):
    if body.token == cfg["global_token"]:
        record_id = hashlib.sha256("{}_{}".format(
            body.name, body.type).encode("utf-8")).hexdigest()
        if record_id in dns_record:
            del dns_record[record_id]
            json_msg = {"status": "success"}
            return json_msg
        else:
            json_msg = {"status": "fail", "reason": "record_not_exist"}
            return json_msg
    else:
        json_msg = {"status": "fail", "reason": "token_error"}
        return json_msg


class DumpDnsRecordBody(BaseModel):
    token: str


@app.post("/api/v1/dump_dns_record")
def api_dump_dns_record(body: DumpDnsRecordBody):
    if body.token == cfg["global_token"]:
        return dns_record
    else:
        json_msg = {"status": "fail", "reason": "token_error"}
        return json_msg


class UpdateDnsRecord(BaseModel):
    token: str
    name: str
    type: str
    content: dict = {}


@app.post("/api/v1/update_dns_record")
async def api_update_dns_record(request: Request, body: UpdateDnsRecord):
    record_id = hashlib.sha256("{}_{}".format(
        body.name, "a").encode("utf-8")).hexdigest()
    if body.type == "a":
        if record_id in dns_record:
            if body.token == str(uuid.uuid5(uuid.UUID(cfg["global_token"]), body.name)):
                if not body.content:
                    client_host = request.client.host
                    try:
                        client_ip_address = ipaddress.ip_address(client_host)
                        if client_ip_address.version == 4:
                            ipv4_addr = str(client_ip_address)
                            content = {"ipv4_addr": ipv4_addr}
                        else:
                            json_msg = {"status": "fail",
                                        "reason": "addr_error"}
                            return json_msg
                    except:
                        json_msg = {"status": "fail", "reason": "addr_error"}
                        return json_msg
                else:
                    content = body.content
                if dns_record[record_id]["content"]["ipv4_addr"] != content["ipv4_addr"]:
                    dns_record[record_id]["content"]["ipv4_addr"] = content["ipv4_addr"]
                    dns_api = dns_api_lib[dns_record[record_id]["dns_api_id"]]
                    auth_id = dns_record[record_id]["dns_api_auth_id"]
                    auth = cfg["dns_api_auth"][auth_id]["auth"]
                    out = await dns_api.update_dns_record(body.name, "a", content, auth)
                    if out["status"] != "success":
                        json_msg = {"status": "fail",
                                    "reason": "dns_api_error"}
                        return json_msg
                json_msg = {"status": "success"}
                return json_msg
            else:
                json_msg = {"status": "fail", "reason": "token_error"}
                return json_msg
        else:
            json_msg = {"status": "fail", "reason": "record_not_exist"}
            return json_msg
    else:
        json_msg = {"status": "fail", "reason": "type_error"}
        return json_msg
