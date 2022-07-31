# hpc-cmdb

## Development

### Kubernetes Setup

There's a shell script at the root of the repository named `setup-kubernetes.sh`.
Make sure to run it before you try to apply the configs.

### Pushing new container versions

If you make changes to the files inside the application directories, you must build a new version of the container so that Kubernetes can pull it from the docker registry.

To push a new version of the `app` application:

```bash
docker buildx build \
    --platform linux/amd64 \
    -f app/Dockerfile.prod app/ \
    -t lcrown/hpc-cmdb-app:latest \
    --push
```

If you need to build the other containers, simply replace `app` with `db` or `api`.
