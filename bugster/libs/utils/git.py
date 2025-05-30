import subprocess


def run_git_command(cmd: list[str]) -> str:
    """Run a git command and return the output."""
    # for pattern in [
    #     "package-lock.json",
    #     ".env.local",
    #     ".gitignore",
    #     "tsconfig.json",
    #     ".env",
    # ]:
    #     cmd.append(f":!{pattern}")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout
