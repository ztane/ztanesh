#!/usr/bin/env python3

import os
import sys
import subprocess
import pwd
from pathlib import Path


def set_default_shell(shell_path: str):
    """
    Sets the default shell for both useradd and adduser.

    Args:
        shell_path (str): Absolute path to the desired shell, e.g., '/usr/bin/zsh'.
    """
    def replace_or_append_var(path: Path, key: str, new_value: str):
        if not path.exists():
            print(f"{path} not found.")
            return
        key_eq = key + "="
        lines = path.read_text().splitlines()
        changed = False
        for i, line in enumerate(lines):
            if line.strip().startswith(key_eq):
                lines[i] = f"{key_eq}{new_value}"
                changed = True
                break
        if not changed:
            lines.append(f"{key_eq}{new_value}")
            print(f"{key_eq} not found in {path}, appending.")
        else:
            print(f"Updated {key_eq} in {path}")
        path.write_text("\n".join(lines) + "\n")

    new_shell = Path(shell_path)
    if not new_shell.exists():
        raise ValueError(f"Shell '{shell_path}' does not exist.")

    replace_or_append_var(Path("/etc/default/useradd"), "SHELL", shell_path)
    replace_or_append_var(Path("/etc/adduser.conf"), "DSHELL", shell_path)


def main(zsh_path):
    print("Attempting to set default shell to Zsh on Ubuntu/Debian")
    set_default_shell(zsh_path)

    directory = os.path.dirname(os.path.abspath(sys.argv[0]))

    print("Finding out remote URL")
    # get remote url for the current repository
    remote_url = (
        subprocess.run(
            [
                "git",
                "config",
                "--get",
                "remote.origin.url",
            ],
            stdout=subprocess.PIPE,
            cwd=directory,
            check=True,
        )
        .stdout.decode()
        .strip()
    )

    if os.path.exists("/etc/skel/tools"):
        print("Skipping /etc/skel (tools directory already exists)")
    else:
        print("Cloning tools repository to /etc/skel")
        subprocess.run(
            [
                "git",
                "clone",
                remote_url,
                "tools",
            ],
            cwd="/etc/skel",
            check=True,
        )

        print("Running setup.zsh")
        subprocess.run(
            [
                "tools/zsh-scripts/setup.zsh",
                "/etc/skel",
            ],
            cwd="/etc/skel",
            check=True,
        )

    # Check for non-interactive mode
    noninteractive = bool(os.environ.get("ZTANESH_NONINTERACTIVE_SETUP"))
    
    for user in list(pwd.getpwall()):
        shell = os.path.basename(user.pw_shell)
        if shell in ["sh", "bash"]:
            if noninteractive:
                print(f"Non-interactive mode: automatically setting up {user.pw_name} (now using {shell})")
                approve = "y"
            else:
                approve = input(f"Setup for {user.pw_name} (now using {shell}) [Y/n]: ")
            if approve.lower() not in ("y", "yes", ""):
                continue

            print(f"Changing shell for {user.pw_name} to zsh")
            subprocess.run(
                [
                    "chsh",
                    "-s",
                    zsh_path,
                    user.pw_name,
                ],
                check=True,
            )
            shell = "zsh"

        if shell != "zsh":
            print(f"Skipping {user.pw_name} (using {shell})")
            continue

        if os.path.exists(f"{user.pw_dir}/tools"):
            print(f"Skipping {user.pw_name} (tools directory already exists)")
            continue

        try:
            print(f"Cloning tools repository to user home dir {user.pw_dir}")
            subprocess.run(
                [
                    "sudo",
                    "-u",
                    user.pw_name,
                    "git",
                    "clone",
                    remote_url,
                    "tools",
                ],
                cwd=user.pw_dir,
                check=True,
            )

            print(f"Running setup.zsh for {user.pw_name}")
            subprocess.run(
                [
                    "sudo",
                    "-u",
                    user.pw_name,
                    "tools/zsh-scripts/setup.zsh",
                    user.pw_dir,
                ],
                cwd=user.pw_dir,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error: {e} for {user.pw_name}")
            continue


if __name__ == "__main__":
    for path in ["/bin/zsh", "/usr/bin/zsh"]:
        if os.path.exists(path):
            zsh_path = path
            print(f"Zsh found at {zsh_path}")
            break
    else:
        print("Zsh not found")
        sys.exit(1)

    if os.getuid() != 0:
        print("Root required... using sudo")
        os.execvp("sudo", ["sudo", sys.executable, *sys.argv])

    main(zsh_path)
