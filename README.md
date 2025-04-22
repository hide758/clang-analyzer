# Clang Analyzer

Parsing and analyzing C code with Clang.


## Install

```shell

podman pod create --name clang-analyzer

podman build -t clang-analyzer -f Containerfile

podman run --detach --pod clang-analyzer -it --volume $PWD/target:/app/target --volume $PWD/app:/app --name clang-analyzer-python clang-analyzer

podman run --detach --pod clang-analyzer -it --volume $PWD/db/var_data:/var/lib/mysql  --env-file .env --name clang-analyzer-mysql docker.io/mysql:lts

```

## Usage

### Analyze

Analyze functions in target source file (*.c).

```shell

python manage.py funcsurvey [--project PROJECT] [--clang-args CLANG_ARGS] TARGET_SOURCE_FILE

find target/ -name "*.c" | xargs -n 1 python manage.py funcsurvey --project "MDS-E-BD SERVO" --clang-args "-I target/ansi -I target/usv/inc -D SERVO" --remove-path-prefix "target/usv/"

```

### Export database

Export analyzing result from database.

```shell
python manage.py exportdb [--project PROJECT]
```

### Clear database

Clear database.

```shell

python manage.py cleardb

```

### Function tree

View function tree.

```shell

python manage.py functree [--project PROJECT] [--upper UpperFunctionDepth] [--lower LowerFunctionDepth] FUNCTION_NAME

```

### Make stub functions

Make stub functions from analyzed data.

```shell

python manage.py makestub [--project PROJECT] [--save-as ExportFileName] [--parent-func ParentFunctionList] 

```
