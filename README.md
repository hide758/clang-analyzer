# Clang Analyzer

## install

```shell
podman pod create --name clang-analyzer
podman build -t clang-analyzer -f Containerfile
podman run --detach --pod clang-analyzer -it --volume $PWD/target:/app/target --volume $PWD/app:/app --name clang-analyzer-python clang-analyzer
podman run --detach --pod clang-analyzer -it --volume $PWD/db/var_data:/var/lib/mysql  --env-file .env --name clang-analyzer-mysql docker.io/mysql:lts
```

## survey

### analyze

Analyze functions in target source file (*.c).

```shell
python manage.py funcsurvey [--project PROJECT] [--clang-args CLANG_ARGS] TARGET_SOURCE_FILE
```

### export database

Export analyzing result from database.

```shell
python manage.py exportdb [--project PROJECT]
```

### crear database

Clear database.

```shell
python manage.py cleardb
```
