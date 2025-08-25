# Quick Setup

## One-line Installation

### Interactive Mode
Run this command and answer the prompts:

```bash
curl -sSL https://raw.githubusercontent.com/user/ztanesh/master/setup | bash -s -- user/ztanesh
```

### Non-Interactive Mode
For automated setups (answers "yes" to all prompts):

```bash
curl -sSL https://raw.githubusercontent.com/user/ztanesh/master/setup | ZTANESH_NONINTERACTIVE_SETUP=1 bash -s -- user/ztanesh
```

## What It Does

1. **Clones the repository** to `~/tools`
   - Tries SSH authentication first (`git@github.com:user/ztanesh`)
   - Falls back to HTTPS if SSH is not available

2. **Runs system-wide setup** (`~/tools/zsh-scripts/setup-all-users.py`)
   - Sets Zsh as the default shell for new users
   - Clones tools to `/etc/skel` for new user templates
   - Optionally sets up existing users with Bash/sh shells
   - Configures Zsh environment for each user

## Using Your Own Fork

If you have forked the repository, replace `user/ztanesh` with your GitHub username and repository:

```bash
curl -sSL https://raw.githubusercontent.com/yourusername/yourrepo/master/setup | bash -s -- yourusername/yourrepo
```

## Requirements

- Git
- Python 3
- Zsh installed on the system
- Sudo privileges (the script will prompt for sudo if needed)

## Environment Variables

- `ZTANESH_NONINTERACTIVE_SETUP`: Set to any non-empty value to skip all prompts and assume "yes"
