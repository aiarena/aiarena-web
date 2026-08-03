import os

from .settings import DOCKERFILE, PROJECT_NAME, PROJECT_PATH
from .utils import echo, run, str_to_bool


_COMPOSE_VERSION: tuple[int, ...] | None = None

ARCH_AMD64 = "amd64"
ARCH_ARM64 = "arm64"


def cli(cmd, **kwargs):
    """
    Shortcut for docker.
    """
    return run(f"docker {cmd}", **kwargs)


def is_compose_v2() -> bool:
    """
    Check if docker-compose v2 is used.
    """
    global _COMPOSE_VERSION
    if _COMPOSE_VERSION is None:
        ver = run("docker-compose version --short", capture_stdout=True).stdout_lines[0]
        _COMPOSE_VERSION = tuple(int(char) for char in ver.split("."))
    return _COMPOSE_VERSION[0] == 2


def is_compose_v2_compatability_enabled() -> bool:
    """
    Check compose v2 compatibility for container names is enabled.
    """
    value = os.environ.get("COMPOSE_COMPATIBILITY", "false")
    return str_to_bool(value)


def container_name(name: str, sequence: int = 1) -> str:
    """
    Return compose container name.
    """
    if is_compose_v2() and not is_compose_v2_compatability_enabled():
        return f"{PROJECT_NAME}-{name}-{sequence}"
    return f"{PROJECT_NAME}_{name}_{sequence}"


def compose(
    cmd,
    project_name=PROJECT_NAME,
    compose_file="docker-compose.yml",
    **kwargs,
):
    """
    Shortcut for docker-compose.
    """
    return run(
        (f"docker-compose -p {project_name} -f {compose_file} {cmd}"),
        **kwargs,
    )


def build_image(
    image: str,
    tag: str | set[str] = "latest",
    build_args: dict = None,
    extra_args: str = "",
    arch: str = None,
    refs: list[str] = None,
    push: bool = False,
    cache_from: str = None,
    cache_to: str = None,
):
    """Build an image with buildx.

    By default the image is tagged locally as `PROJECT_NAME/image:tag` and
    loaded into the local Docker daemon. Pass `refs` (fully-qualified registry
    URIs) together with `push=True` to upload it straight from the builder to
    the registry instead, skipping the tarball export into the local daemon and
    the subsequent re-push.
    """
    if refs is None:
        tags = {tag} if isinstance(tag, str) else tag
        refs = [f"{PROJECT_NAME}/{image}:{t}" for t in tags]

    # --push uploads every -t reference straight to the registry, so they must
    # be fully-qualified registry URIs — a bare local name would be pushed to
    # Docker Hub and fail. A registry URI has a host (with a dot) before its
    # first slash; a bare local name does not.
    if push and not all("." in ref.partition("/")[0] for ref in refs):
        raise ValueError(f"push=True requires absolute registry URIs, got: {refs}")

    echo(f"Build environment image: {', '.join(refs)}")
    image_tags: str = " ".join(f"-t {ref}" for ref in refs)

    if build_args:
        args = " ".join([f'--build-arg {k}="{v}"' for k, v in build_args.items()])
    else:
        args = ""
    if arch:
        args += f" --platform=linux/{arch}"

    # --provenance=false: by default buildx pushes each tag as a manifest LIST
    # (image + provenance/SBOM attestation), even for a single platform. The
    # deploy step assembles the multi-arch image with `docker manifest create`
    # from the per-arch tags, which refuses to nest a manifest list inside
    # another one. Disabling attestations makes each per-arch tag a plain
    # single-platform image manifest, so manifest create works.
    args += " --push --provenance=false" if push else " --load"

    if cache_from:
        args += f" --cache-from {cache_from}"
    if cache_to:
        args += f" --cache-to {cache_to}"

    # The image name is the stage to build in the shared multi-stage Dockerfile.
    cli(f"buildx build --target {image} {args} {extra_args} {image_tags} -f {DOCKERFILE} .")


def remove_unused_local_images():
    unused_images = cli("images -f dangling=true -q", capture_stdout=True).stdout_lines
    if unused_images:
        echo(f"Removing {len(unused_images)} unused image(s)")
        try:
            cli(f"rmi {' '.join(unused_images)}")
        except RuntimeError:
            echo("Oops, one of those images is actually used, skipping..")


def remove_container(name):
    cont_ids = cli(f"ps -aq --filter name={name}", capture_stdout=True).stdout_lines
    if cont_ids:
        echo(f"Removing container: {name}")
        cli(f"rm -f {' '.join(cont_ids)}")


def dev_container_run(cmd, extra_mappings=None, workdir=None, **kwargs):
    mappings = {
        str(PROJECT_PATH / "code"): "/code",
    }
    if extra_mappings is not None:
        mappings.update(extra_mappings)
    volumes = " ".join([f"-v {src}:{trg}" for src, trg in mappings.items()])
    workdir = f"-w {workdir}" if workdir else ""
    return cli(
        f'run --rm {volumes} {workdir} -i {PROJECT_NAME}/dev bash -c "{cmd}"',
        **kwargs,
    )
