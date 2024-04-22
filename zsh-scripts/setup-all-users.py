#!/usr/bin/env python3

import os
import sys
import subprocess
import pwd


def main(zsh_path):
    directory = os.path.dirname(sys.argv[0])

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

    for user in list(pwd.getpwall()):
        shell = os.path.basename(user.pw_shell)
        if shell in ["sh", "bash"]:
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
