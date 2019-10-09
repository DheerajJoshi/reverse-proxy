## Reverse-Proxy
###### Reverse Proxy with random forward request(in python)

> Reverse proxy server: A reverse proxy server is a type of proxy server that typically sits behind the firewall in a private network and directs client requests to the appropriate backend server. A reverse proxy provides an additional level of abstraction and control to ensure the smooth flow of network traffic between clients and servers.

<img src="https://github.com/DheerajJoshi/extra-stuff/blob/master/reverse-proxy/images/reverse-proxy.png" width="100%"/>

References: <a href="https://www.nginx.com/resources/glossary/reverse-proxy-server/">Reverse Proxy</a>

## Design and implementation

### Prerequisite

```
- Install git, python3 on base machine
- Install docker for running containers
- Install minikube(latest version)
- Install kubernetes-helm
- Install kubectl
- Install kubens and kubectx (https://github.com/ahmetb/kubectx)
```

### Run code locally on containers

```
$ git clone <path>
$ cd <path>
```

- Create python3 virtual environment

```
$ pip3 install virtualenv
$ virtualenv -p python3 .
$ source bin/activate
$ cd src/
$ python3 install -r requirements.txt
```

> How to use config.py
```
$ python3 config.py --help

usage: config.py [-h] [--sub-domain SUB_DOMAIN] [--ingress-port INGRESS_PORT]
                 [--target-port TARGET_PORT]

optional arguments:
  -h, --help            show this help message and exit
  --sub-domain SUB_DOMAIN
                        name of sub-domain
  --ingress-port INGRESS_PORT
                        Ingress port on which traffic will come
  --target-port TARGET_PORT
                        Target port on which traffic will go
```

> Create config file to pass as redirect path(output will give config.yaml file)
```
$ python3 config.py --sub-domain my-service --ingress-port 8080 --target-port 9090
```

Example of config file
> In example I am using different website names for testing the redirection of reverse proxy to hosts
```
proxy:
  listen:
    address: 127.0.0.1
    port: '8080'
  services:
  - domain: my-service.mycompany.com
    hosts:
    - address: 10.0.0.1
      port: '9090'
    - address: 10.0.0.2
      port: '9090'
    - address: 10.0.0.3
      port: '9090'
    - address: 10.0.0.4
      port: '9090'
    - address: 10.0.0.5
      port: '9090'
    name: my-service
```

Generate default configuration file for testing
> NOTE: Commented one function which can use for internal IP(need to update IP)
```
$ python3 config.py --sub-domain my-service --ingress-port 8080
```

### Run reverse-proxy server in containers

```
$ cd ..
$ docker build -t reverseproxy .
$ docker run -d -p 8080:8080 --name reverse-proxy reverseproxy:latest
```

## AUTOMATION

###To test from local machine

> go to browser and paste

```
http://localhost:8080
```

> Use curl to test from terminal(for health check)

```
$ curl http://localhost:8080/api/v2/_health_check

Health-check reverse-proxy is working!!!!!
```

### Push docker image to registry(I already pushed to docker-hub)
> NOTE: I used docker hub

```
$ docker tag reverseproxy:latest <username>/reverseproxy:randomalgo
$ docker login docker.io
```

> After success full login

```
$ docker push docker.io/<username>/reverseproxy:randomalgo
```

## Use Kubernetes-helm chart to create deployment and service
- NodePort service(to test reverse-proxy server from outside of cluster using NodePort)
- deployment

```
$ minikube start
$ kubens default
$ kubectx minikube
$ helm init
```

If `helm init` fails
> NOTE: Got some error while running helm init(Error: error installing: the server could not find the requested resource)
So, I installed tiller

### Installing tiller due to above issues(got from stackoverflow)

```
$ helmins() {kubectl -n kube-system create serviceaccount tiller &&  kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller &&  helm init --service-account=tiller}

$ helmins

$ helm init --service-account tiller --override spec.selector.matchLabels.'name'='tiller',spec.selector.matchLabels.'app'='helm' --output yaml |  sed 's@apiVersion: extensions/v1beta1@apiVersion: apps/v1@' | kubectl apply -f -
```

### Deploy reverse-proxy python app using helm chart

> Helm install and deploy application

```
$ helm install chart_reverse_proxy --name reverse-proxy

NAME: reverse-proxy
LAST DEPLOYED: Thu Oct 10 02:11:53 2019
NAMESPACE: default
STATUS: DEPLOYED

RESOURCES:
==> v1/Deployment
NAME               READY  UP-TO-DATE  AVAILABLE  AGE
reverse-proxy-app  0/1    1           0          0s

==> v1/Pod(related)
NAME                                READY  STATUS             RESTARTS  AGE
reverse-proxy-app-798975b545-mqtmd  0/1    ContainerCreating  0         0s

==> v1/Service
NAME                   TYPE      CLUSTER-IP     EXTERNAL-IP  PORT(S)         AGE
reverse-proxy-service  NodePort  10.100.44.166  <none>       8080:30653/TCP  0s
```

> helm list of all deployed application

```
$ helm list

NAME        	REVISION	UPDATED                 	STATUS  	CHART                    	APP VERSION	NAMESPACE
reverse-proxy	1       	Thu Oct 10 02:11:53 2019	DEPLOYED	chart_reverse_proxy-1.0.0	           	default
```

> helm status
```
$ helm status reverse-proxy  

LAST DEPLOYED: Thu Oct 10 02:11:53 2019
NAMESPACE: default
STATUS: DEPLOYED

RESOURCES:
==> v1/Deployment
NAME               READY  UP-TO-DATE  AVAILABLE  AGE
reverse-proxy-app  1/1    1           1          56s

==> v1/Pod(related)
NAME                                READY  STATUS   RESTARTS  AGE
reverse-proxy-app-798975b545-mqtmd  1/1    Running  0         56s

==> v1/Service
NAME                   TYPE      CLUSTER-IP     EXTERNAL-IP  PORT(S)         AGE
reverse-proxy-service  NodePort  10.100.44.166  <none>       8080:30653/TCP  56s
```

> cluster information to get cluster master node IP

```
$ kubectl cluster-info

Kubernetes master is running at https://192.168.99.100:8443
KubeDNS is running at https://192.168.99.100:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'
```

> Get all pods

```
$ kubectl get pods -o wide

NAME                                 READY   STATUS    RESTARTS   AGE     IP           NODE       NOMINATED NODE   READINESS GATES
reverse-proxy-app-798975b545-mqtmd   1/1     Running   0          3m19s   172.17.0.9   minikube   <none>           <none>
```

> Get all deployment

```
$ kubectl get deployments -o wide

NAME                READY   UP-TO-DATE   AVAILABLE   AGE     CONTAINERS          IMAGES                                 SELECTOR
reverse-proxy-app   1/1     1            1           3m25s   reverse-proxy-app   dheerajjoshi/reverseproxy:randomalgo   run=reverse-proxy-app
```

> Get all service

```
$ kubectl get services -o wide

NAME                    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE     SELECTOR
kubernetes              ClusterIP   10.96.0.1       <none>        443/TCP          144m    <none>
reverse-proxy-service   NodePort    10.100.44.166   <none>        8080:30653/TCP   3m31s   run=reverse-proxy-app
```

## checking endpoints
```
$ kubectl get endpoints

NAME                    ENDPOINTS             AGE
kubernetes              192.168.99.100:8443   144m
reverse-proxy-service   172.17.0.9:8080       3m36s
```

## MONITORING

### Add-ons for monitoring and checking scalability for calculating SLI

```
$ minikube addons enable heapster
$ minikube addons enable metrics-server
$ minikube addons open heapster
$ minikube dashboard &
```

## SCALING(Manually)

> update replicas from 1 to 7 in chart_reverse_proxy/values.yaml file

```
$ helm upgrade reverse-proxy chart_reverse_proxy

Release "reverse-proxy" has been upgraded.
LAST DEPLOYED: Thu Oct 10 02:48:34 2019
NAMESPACE: default
STATUS: DEPLOYED

RESOURCES:
==> v1/Deployment
NAME               READY  UP-TO-DATE  AVAILABLE  AGE
reverse-proxy-app  1/7    1           1          2m2s

==> v1/Pod(related)
NAME                                READY  STATUS             RESTARTS  AGE
reverse-proxy-app-798975b545-6ptbs  0/1    Pending            0         0s
reverse-proxy-app-798975b545-725tb  0/1    ContainerCreating  0         0s
reverse-proxy-app-798975b545-dn5dj  1/1    Running            0         2m2s
reverse-proxy-app-798975b545-ht7rw  0/1    Pending            0         0s
reverse-proxy-app-798975b545-qqx9w  0/1    Pending            0         0s
reverse-proxy-app-798975b545-v4lnh  0/1    ContainerCreating  0         0s
reverse-proxy-app-798975b545-wvl94  0/1    Pending            0         0s

==> v1/Service
NAME                   TYPE      CLUSTER-IP      EXTERNAL-IP  PORT(S)         AGE
reverse-proxy-service  NodePort  10.106.191.124  <none>       8080:30653/TCP  2m2s
```

## Delete complete application

```
$ helm delete reverse-proxy

release "reverse-proxy" deleted

$ helm del --purge reverse-proxy
```

## SCALING(Automatically using HPA horizontal pod autoscaler)

- Add new file `controller-hpa.yaml`

```
$ cd chart_reverse_proxy/templates
```

- content of `controller-hpa.yaml`

```
apiVersion: autoscaling/v1
kind: HorizontalPodAutoscaler
metadata:
  name: reverse-proxy-app
  namespace: default
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: reverse-proxy-app
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 50
```

- Copy above content in `controller-hpa.yaml` file and save under `chart_reverse_proxy/templates` path and run helm to deploy

```
$ cd ../../
$ helm repo update
$ helm install chart_reverse_proxy --name reverse-proxy
```

NOTE: For testing, I made cpu usage very less so when I run load testing then I can see scaling due to pod autoscaler

## TESTING

> Run in multiple terminal and check

```
$ while True; do  curl http://<master-cluster-ip>:30653/asnis/nsias ; done

$ while True; do  curl http://<master-cluster-ip>:30653/api/v2/_health_check ; done

$ watch -n 2 kubectl get hpa -o wide

Every 2.0s: kubectl get hpa -o wide

NAME                REFERENCE                      TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
reverse-proxy-app   Deployment/reverse-proxy-app   19%/1%    1         10        1          99s

$ watch -n 2 kubectl get pods -o wide

Every 2.0s: kubectl get pods -o wide

NAME                                 READY   STATUS    RESTARTS   AGE     IP            NODE       NOMINATED NODE   READINESS GATES
reverse-proxy-app-5766694678-2z7jf   0/1     Pending   0          15s     <none>        <none>     <none>           <none>
reverse-proxy-app-5766694678-b494k   0/1     Pending   0          31s     <none>        <none>     <none>           <none>
reverse-proxy-app-5766694678-c947p   1/1     Running   0          46s     172.17.0.11   minikube   <none>           <none>
reverse-proxy-app-5766694678-g6qj8   0/1     Pending   0          31s     <none>        <none>     <none>           <none>
reverse-proxy-app-5766694678-j72mc   0/1     Pending   0          15s     <none>        <none>     <none>           <none>
reverse-proxy-app-5766694678-kcb4m   1/1     Running   0          2m17s   172.17.0.10   minikube   <none>           <none>
reverse-proxy-app-5766694678-q664r   1/1     Running   0          46s     172.17.0.13   minikube   <none>           <none>
reverse-proxy-app-5766694678-rjdwq   1/1     Running   0          46s     172.17.0.12   minikube   <none>           <none>
reverse-proxy-app-5766694678-s9lrf   0/1     Pending   0          31s     <none>        <none>     <none>           <none>
reverse-proxy-app-5766694678-zcn4f   0/1     Pending   0          31s     <none>        <none>     <none>           <none>

$  minikube addons open heapster

|-------------|----------|-------------|--------------|
|  NAMESPACE  |   NAME   | TARGET PORT |     URL      |
|-------------|----------|-------------|--------------|
| kube-system | heapster |             | No node port |
|-------------|----------|-------------|--------------|
😿  service kube-system/heapster has no node port
|-------------|--------------------|-------------|-----------------------------|
|  NAMESPACE  |        NAME        | TARGET PORT |             URL             |
|-------------|--------------------|-------------|-----------------------------|
| kube-system | monitoring-grafana |             | http://<master-cluster-ip>:30002 |
|-------------|--------------------|-------------|-----------------------------|
🎉  Opening kubernetes service  kube-system/monitoring-grafana in default browser...
```

## Delete everything

```
$ helm delete reverse-proxy
$ helm del --purge reverse-proxy
$ minikube delete
```

### Limitations

- [ ] abc
- [x]

## Improvements

- [ ] abc
