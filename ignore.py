import os

# Check if .gitignore file exists, if not, create one
if not os.path.exists('.gitignore'):
    with open('.gitignore', 'w') as f:
        f.write('.venv\n')
else:
    # If .gitignore exists, append .venv to it
    with open('.gitignore', 'a') as f:
        f.write('.venv\n')