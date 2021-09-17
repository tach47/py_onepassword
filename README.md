# py_onepassword

## Requirements
- 1password.com account
- op (`brew install 1password-cli` or https://support.1password.com/command-line-getting-started/)
- `toml` python module

## Usage

✨ **Update 1password.toml with your relevant information** ✨

Example code:
```
import py_onepassword as op
secret = op.get_password('example account')    # Uses Python's x in y logic
secret = op.get_password('example acc')        # This works too.

username = op.get_username('example account')  # x in y logic works here too
username = op.get_username('example acc')
```
