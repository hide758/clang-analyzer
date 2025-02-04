# Clang Analyzer

## install

```shell
podman pod create --name clang-analyzer
podman build -t clang-analyzer -f Containerfile
podman run --detach --pod clang-analyzer -it --volume $PWD/target:/app/target --volume $PWD/app:/app --name clang-analyzer-python clang-analyzer
podman run --detach --pod clang-analyzer -it --volume $PWD/db/var_data:/var/lib/mysql  --env-file .env --name clang-analyzer-mysql docker.io/mysql:lts
```

## survey

```shell
python manage.py survey
```
