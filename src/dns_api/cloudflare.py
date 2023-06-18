#!/usr/bin/env python3


# author: tcneko <tcneko@outlook.com>
# start from: 2023.05
# last test environment: ubuntu 22.04
# description:


# import
import aiohttp


# function
async def update_dns_record(name, type, content, auth):
    async with aiohttp.ClientSession() as session:
        # get record id
        url = "https://api.cloudflare.com/client/v4/zones/{}/dns_records".format(
            auth["zone_id"])
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Email": auth["mail"],
            "X-Auth-Key": auth["token"]
        }
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                response_body = await response.json()
                json_msg = {
                    "url": url, "response_code": response.status, "response_body": response_body}
                print(json_msg)
                json_msg = {"status": "fail", "reason": "api_error"}
                return json_msg
            else:
                response_body = await response.json()
                record_id = ""
                for record in response_body["result"]:
                    if record["name"] == name:
                        record_id = record["id"]
                if not record_id:
                    json_msg = {"status": "fail", "reason": "record_not_exist"}
                    return json_msg

        # update record
        url = "https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}".format(
            auth["zone_id"], record_id)
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Email": auth["mail"],
            "X-Auth-Key": auth["token"]
        }
        if type == "a":
            data = {
                "name": name,
                "type": type,
                "content": content["ipv4_addr"]
            }
        else:
            json_msg = {"status": "fail", "reason": "type_error"}
            return json_msg
        async with session.put(url, headers=headers, json=data) as response:
            if response.status != 200:
                response_body = await response.json()
                json_msg = {
                    "url": url, "response_code": response.status, "response_body": response_body}
                print(json_msg)
                json_msg = {"status": "fail", "reason": "api_error"}
                return json_msg
            else:
                json_msg = {"status": "success"}
                return json_msg
