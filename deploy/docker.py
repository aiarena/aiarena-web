import os

from .settings import IMAGES, PROJECT_NAME, PROJECT_PATH
from .utils import echo, run, str_to_bool


_COMPOSE_VERSION: tuple[int, ...] | None = None

ARCH_AMD64 = "amd64"
ARCH_ARM64 = "arm64"


def cli(cmd, **kwargs):
    """
    Shortcut for docker.
    """
    return run("docker %s" % cmd, **kwargs)


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
        ("docker-compose " f"-p {project_name} " f"-f {compose_file} " f"{cmd}"),
        **kwargs,
    )


def build_image(
    image: str,
    tag: str | set[str] = "latest",
    build_args: dict = None,
    extra_args: str = "",
    arch: str = None,
):
    echo(f"Build environment image: {image}:{tag}")

    tags = {tag} if isinstance(tag, str) else tag
    image_tags: str = " ".join([f"-t {PROJECT_NAME}/{image}:{t}" for t in tags])

    path = IMAGES[image]
    if build_args:
        args = " ".join([f'--build-arg {k}="{v}"' for k, v in build_args.items()])
    else:
        args = ""
    if arch:
        platform = f"--platform={arch}"
    else:
        platform = ""
    cli(f"build --force-rm {args} {platform} {extra_args} {image_tags} -f {path} .")


def remove_unused_local_images():
    unused_images = cli("images -f dangling=true -q", capture_stdout=True).stdout_lines
    if unused_images:
        echo("Removing %s unused image(s)" % len(unused_images))
        try:
            cli("rmi %s" % " ".join(unused_images))
        except RuntimeError:
            echo("Oops, one of those images is actually used, skipping..")


def remove_container(name):
    cont_ids = cli("ps -aq --filter name=%s" % name, capture_stdout=True).stdout_lines
    if cont_ids:
        echo("Removing container: %s" % name)
        cli("rm -f %s" % " ".join(cont_ids))


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
