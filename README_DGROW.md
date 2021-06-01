## 构建web镜像
```shell
docker build -t frigate-web -f ../docker/Dockerfile.web .
```

## 构建dgrow镜像
```sh
docker build -t yangchengjian/frigate:0.8.4-amd64 -f Dockerfile.dgrow.amd64 .
```