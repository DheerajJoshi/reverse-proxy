import random
import sys
import yaml
import argparse


# def populateConfig(args):
#     sub_domain = args.sub_domain
#     ingress_port = args.ingress_port
#     target_port = args.target_port
#     configIn = {
#         "proxy": {
#             "listen": {"address": "127.0.0.1", "port": "%s" % (ingress_port)},
#             "services": [
#                 {
#                     "name": "%s" % (sub_domain),
#                     "domain": "%s.mycompany.com" % (sub_domain),
#                     "hosts": [
#                         {"address": "10.0.0.1", "port": "%s" % (target_port)},
#                         {"address": "10.0.0.2", "port": "%s" % (target_port)},
#                         {"address": "10.0.0.3", "port": "%s" % (target_port)},
#                         {"address": "10.0.0.4", "port": "%s" % (target_port)},
#                         {"address": "10.0.0.5", "port": "%s" % (target_port)},
#                     ],
#                 }
#             ],
#         }
#     }
#
#     configOut = yaml.dump(configIn, default_flow_style=False)
#     return configOut


def populateConfig(args):
    sub_domain = args.sub_domain
    ingress_port = args.ingress_port
    target_port = args.target_port
    configIn = {
        "proxy": {
            "listen": {"address": "127.0.0.1", "port": "%s" % (ingress_port)},
            "services": [
                {
                    "name": "%s" % (sub_domain),
                    "domain": "%s.mycompany.com" % (sub_domain),
                    "hosts": [
                        {
                            "address": "http://www.google.com",
                            "port": "%s" % (target_port),
                        },
                        {
                            "address": "http://www.bing.com",
                            "port": "%s" % (target_port),
                        },
                        {
                            "address": "http://www.stackoverflow.com",
                            "port": "%s" % (target_port),
                        },
                        {
                            "address": "http://www.kubernetes.io",
                            "port": "%s" % (target_port),
                        },
                        {
                            "address": "http://www.docker.com",
                            "port": "%s" % (target_port),
                        },
                    ],
                }
            ],
        }
    }

    configOut = yaml.dump(configIn, default_flow_style=False)
    return configOut


def validateYaml(config):
    try:
        yaml.safe_load(config)
        return config
    except Exception as e:
        sys.exit("Failed to validate config.")


if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.add_argument(
        "--sub-domain", default="my-service", help="name of sub-domain"
    )
    argp.add_argument(
        "--ingress-port",
        default=8080,
        help="Ingress port on which traffic will come",
    )
    argp.add_argument(
        "--target-port",
        default="",
        help="Target port on which traffic will go",
    )
    args = argp.parse_args()
    config = validateYaml(populateConfig(args))
    reverse_proxy_config = open("config.yaml", "w")
    reverse_proxy_config.write(config)
    reverse_proxy_config.close()
