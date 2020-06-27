## Datadog agent setup

Если вам не нужны метрики, можно просто создать сеть и не выполнять вторую команду, проект будет работать и так.

```
docker network create dd-agent
DOCKER_CONTENT_TRUST=1 docker run -d --name dd-agent -v /var/run/docker.sock:/var/run/docker.sock:ro -v /proc/:/host/proc/:ro -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro -e DD_API_KEY=$DD_API_KEY -e DD_DOGSTATSD_NON_LOCAL_TRAFFIC=1 --network dd-agent datadog/agent:7
```
