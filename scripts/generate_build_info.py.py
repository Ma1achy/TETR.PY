import subprocess
import datetime
import sys
import platform
import json

def get_git_commit_hash():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')
    except subprocess.CalledProcessError:
        return 'Unknown'

def get_git_branch():
    try:
        return subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf-8')
    except subprocess.CalledProcessError:
        return 'Unknown'

def get_build_date():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_dependencies():
    # Example of getting dependencies from requirements.txt
    try:
        with open('requirements.txt', 'r') as f:
            dependencies = f.read().splitlines()
        return dependencies
    except FileNotFoundError:
        return 'Unknown'


build_info = {
    'VERSION': 'alpha 0.1', 
    'BUILD_DATE': get_build_date(),
    'GIT_COMMIT_HASH': get_git_commit_hash(),
    'GIT_BRANCH': get_git_branch(),
    'BUILD_ENV': 'development', 
    'DEPENDENCIES': get_dependencies(),
}

with open('app/state/build_info.json', 'w') as f:
    json.dump(build_info, f, indent=4)

