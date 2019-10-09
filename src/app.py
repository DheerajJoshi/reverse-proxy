from flask import Flask, request, redirect, Response, make_response
from flask_caching import Cache
import requests
import random
import argparse
import yaml

app = Flask(__name__)
cache = Cache(app, config={"CACHE_TYPE": "simple"})


def read_config(args):
    """
    description: This function is used to parse the config.yaml file and \n
                get desired output in dictionary as key-value pair.
    param args: inpur arguments
    return: return dictionary containing key-value for hosts and port number
    """
    config_file_name = args.config_file
    with open(config_file_name) as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    config_dict = {}
    config_dict["ingress_port"] = data["proxy"]["listen"]["port"]
    config_dict["sub_domain"] = data["proxy"]["services"][0]["name"]
    hosts = data["proxy"]["services"][0]["hosts"]
    host_list = []
    for i in hosts:
        ip_port = i["address"]
        if i["port"] == "":
            ip_port = str(ip_port)
        else:
            ip_port = str(ip_port) + ":" + str(i["port"])
        host_list.append(ip_port)
    config_dict["hosts"] = host_list
    file.close()
    return config_dict


@app.route("/")
@cache.cached(timeout=1)
def main():
    """
    description: main route path with caching enabled having timeout of 1 \n
                seconds
    return: redirect to get_request function which is having GET request type
    """
    return get_request(path="test")


# health_check of reverse-proxy
@app.route("/api/v2/_health_check")
def health_check():
    """
    description: Function which is used to check the health check for \n
                reverse-proxy server. This verify that server is up and running
    return: make_response with string output and status code of 200
    """
    headers = {"Content-Type": "application/json"}
    return make_response("Health-check reverse-proxy is working!!!!!", 200)


@app.route("/<path:path>", methods=["GET"])
@cache.cached(timeout=1)
def get_request(path):
    """
    description: route for any path(having GET request) with caching enabled \n
                having timeout of 1 seconds. This will implement very basic \n
                caching within route
    param path: any path containing (/) in between.
    logic: using random function to always use different host from list. But \n
           also using cache of 1 second which can increase
    return: response which is json file containing status-code, headers and \n
            content which will go to host directly. It will not return \n
            parameters such as content-encoding, content-length, \n
            transfer-encoding and connection
    """
    if request.method == "GET":
        choice = random.choice(app.config["hosts"])
        resp = requests.get(f"{choice}")
        excluded_headers = [
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        ]
        headers = [
            (name, value)
            for (name, value) in resp.raw.headers.items()
            if name.lower() not in excluded_headers
        ]
        response = Response(resp.content, resp.status_code, headers)
        return response


@app.route("/<path:path>", methods=["POST", "DELETE", "PUT"])
def other_request(path):
    """
    description: route for any path(having POST, DELETE, PUT requests). No \n
                need to implement cache for such request type
    param path: any path containing (/) in between.
    logic: using random function to always use different host from list.
    return: response which is json file containing status-code, headers and \n
            content which will go to host directly. It will not return \n
            parameters such as content-encoding, content-length, \n
            transfer-encoding and connection
    """
    if request.method == "POST":
        choice = random.choice(app.config["hosts"])
        resp = requests.post(f"{choice}", json=request.get_json())
        excluded_headers = [
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        ]
        headers = [
            (name, value)
            for (name, value) in resp.raw.headers.items()
            if name.lower() not in excluded_headers
        ]
        response = Response(resp.content, resp.status_code, headers)
        return response
    elif request.method == "DELETE":
        choice = random.choice(app.config["hosts"])
        resp = requests.delete(f"{choice}").content
        response = Response(resp.content, resp.status_code, headers)
        return response
    elif request.method == "PUT":
        choice = random.choice(app.config["hosts"])
        resp = requests.post(f"{choice}", json=request.get_json())
        excluded_headers = [
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        ]
        headers = [
            (name, value)
            for (name, value) in resp.raw.headers.items()
            if name.lower() not in excluded_headers
        ]
        response = Response(resp.content, resp.status_code, headers)
        return response


if __name__ == "__main__":
    """
    description: main function which calls read_config() which returns \n
                dictionary config_dict containting data from config.yaml file
    """
    argp = argparse.ArgumentParser()
    argp.add_argument("--config-file", help="yaml config file")
    # argp.add_argument(
    #     "--algo",
    #     default="random",
    #     help="Algo used to redirect the traffic from reverse proxy to server machine",
    # )
    args = argp.parse_args()
    config_dict = read_config(args)
    app.config.update(config_dict)
    ingress_port = config_dict['ingress_port']
    app.run(debug=True, port=ingress_port, host='0.0.0.0')
