#!/usr/bin/env python3
"""Generate the deterministic, diff-scoped source-file inventory for a security diff scan.

Modes
-----
revisions : compare ``base...head`` (three-dot: changes on head since the merge base).
local-patch : compare the working tree (staged + unstaged) against ``base`` (default HEAD).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


class DiffError(ValueError):
    """Raised when the repository, diff target, or output cannot be used safely."""


TEXT_CODE_EXTENSIONS = {
    "py", "pyw", "js", "jsx", "ts", "tsx", "mjs", "cjs", "go", "java", "kt", "kts",
    "rb", "php", "c", "h", "cc", "cpp", "cxx", "hpp", "hh", "cs", "rs", "swift",
    "scala", "sc", "pl", "pm", "lua", "m", "mm", "sql", "html", "htm", "xml",
    "xhtml", "json", "jsonl", "yml", "yaml", "toml", "ini", "cfg", "conf", "env",
    "properties", "css", "scss", "less", "sass", "vue", "svelte", "ejs", "hbs",
    "handlebars", "twig", "jsp", "aspx", "cgi", "gradle", "groovy", "sh", "bash",
    "zsh", "fish", "ps1", "dart", "ex", "exs", "erl", "hs", "clj", "cljs", "r",
    "pyproject", "tf", "proto", "graphql", "gql", "cgi",
    "md", "mdx", "markdown", "rst", "txt", "adoc",
}

TEXT_NAMED_FILES = {
    "Dockerfile", "Makefile", "GNUmakefile", "Rakefile", "Gemfile", "Podfile",
    "Procfile", "go.mod", "go.sum", "requirements.txt", "setup.py", "setup.cfg",
    "Cargo.toml", "Cargo.lock", "pyproject.toml", "package.json", "package-lock.json",
    "pnpm-lock.yaml", "yarn.lock", "tsconfig.json", "tsconfig.build.json",
    "Pipfile", "Pipfile.lock", "CMakeLists.txt", "pom.xml", "build.gradle",
    "settings.gradle", "build.gradle.kts", "settings.gradle.kts",
}

EXCLUDED_DIR_PARTS = {
    ".git", "node_modules", "dist", "build", "target", ".venv", "venv",
    "__pycache__", ".next", ".cache", "out", ".output", "coverage", "vendor",
}


def resolve_repository(value: str) -> Path:
    """Resolve the repository once so every scope is bound to its real root."""
    try:
        repository = Path(value).expanduser().resolve(strict=True)
    except (OSError, ValueError) as error:
        raise DiffError(f"--repo: cannot resolve repository: {value}") from error
    if not repository.is_dir():
        raise DiffError(f"--repo: expected a directory: {repository}")
    return repository


def resolve_output(value: str) -> Path:
    """Reject direct symlink outputs without constraining the artifact root."""
    if not value or "\0" in value:
        raise DiffError("--out: expected an inventory file path")
    requested = Path(value).expanduser()
    if requested.is_symlink():
        raise DiffError("--out: refusing to replace a symbolic link")
    try:
        output = requested.resolve(strict=False)
    except (OSError, ValueError) as error:
        raise DiffError(f"--out: cannot resolve inventory path: {value}") from error
    if output.exists() and not output.is_file():
        raise DiffError(f"--out: expected a regular file path: {output}")
    return output


def git_capture(repository: Path, *arguments: str) -> list[str]:
    """Run a read-only git command and return its NUL-separated lines as UTF-8.

    ``-c core.quotepath=false`` keeps non-ASCII repository-relative paths
    verbatim instead of C-style quoted, and ``-z`` makes the record boundary
    unambiguous; both bytes are decoded here as UTF-8 (git stores paths as
    bytes), independent of the console codepage.
    """
    try:
        result = subprocess.run(
            ["git", "-c", "core.quotepath=false", *arguments],
            cwd=repository,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as error:
        raise DiffError(f"git: cannot run git: {error}") from error
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).decode("utf-8", "replace").strip()
        raise DiffError(f"git {' '.join(arguments)} failed: {detail or 'unknown error'}")
    return [
        line for line in result.stdout.decode("utf-8", "replace").split("\0") if line
    ]


def is_source_like(relative: str) -> bool:
    """Keep changed files that are plausibly source or config, drop generated paths."""
    parts = Path(relative).parts
    if any(part in EXCLUDED_DIR_PARTS for part in parts):
        return False
    name = parts[-1]
    if name in TEXT_NAMED_FILES:
        return True
    suffix = Path(name).suffix.lstrip(".").lower()
    if name.endswith(".d.ts"):
        return True
    return suffix in TEXT_CODE_EXTENSIONS


def changed_files(repository: Path, mode: str, base: str, head: str | None) -> list[str]:
    """Return the repository-relative changed source files for the requested diff."""
    common = ["diff", "--name-only", "-z", "--diff-filter=ACMRT", "--no-renames"]
    if mode == "local-patch":
        target = base if base else "HEAD"
        result = git_capture(repository, *common, target)
    else:
        target = f"{base}...{head}" if head else f"{base}"
        result = git_capture(repository, *common, target)
    seen: list[str] = []
    for relative in result:
        relative = relative.strip()
        if not relative or "\0" in relative:
            continue
        if not is_source_like(relative):
            continue
        if relative not in seen:
            seen.append(relative)
    seen.sort()  # byte-order deterministic, independent of locale
    return seen


def write_inventory(output: Path, lines: list[str]) -> None:
    """Atomically write the sorted inventory, refusing to clobber a symlink."""
    data = ("\n".join(lines) + ("\n" if lines else "")).encode("utf-8")
    directory = output.parent
    try:
        directory.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=output.name + ".", dir=directory)
    except OSError as error:
        raise DiffError(f"--out: cannot create temporary file next to {output}: {error}") from error
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(temporary, output)
    except OSError as error:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise DiffError(f"--out: cannot write inventory: {output}: {error}") from error


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="repository root")
    parser.add_argument("--mode", required=True, choices=["revisions", "local-patch"])
    parser.add_argument("--base", required=True, help="base ref (local-patch: the ref to diff the working tree against)")
    parser.add_argument("--head", default=None, help="head ref for revisions mode")
    parser.add_argument("--out", required=True, help="output inventory path")
    args = parser.parse_args(argv)

    try:
        repository = resolve_repository(args.repo)
        output = resolve_output(args.out)
        lines = changed_files(repository, args.mode, args.base, args.head)
        write_inventory(output, lines)
    except DiffError as error:
        print(f"generate_diff_files: error: {error}", file=sys.stderr)
        return 1

    print(f"generate_diff_files: {len(lines)} in-scope changed files -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
