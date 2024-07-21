import json
import os
import subprocess
import sys
from os import path


def get_git_commit_info():
    try:
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip().decode('utf-8')
        commit_date = subprocess.check_output(['git', 'log', '-1', '--format=%cd', '--date=short']).strip().decode('utf-8')
        branch_name = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf-8')
        author_name = subprocess.check_output(['git', 'log', '-1', '--format=%an']).strip().decode('utf-8')
        commit_message = subprocess.check_output(['git', 'log', '-1', '--format=%s']).strip().decode('utf-8')
        is_dirty = subprocess.check_output(['git', 'status', '--porcelain']).strip().decode('utf-8') != ''
        commit_data = {
            'commit': commit_hash,
            'commit_date': commit_date,
            'branch': branch_name,
            'author': author_name,
            'commit_message': commit_message,
            'dirty': is_dirty
        }
        return commit_data
    except subprocess.CalledProcessError:
        return None

def update_version_file(version):
    commit_data = get_git_commit_info()
    if commit_data is None:
        print("Could not retrieve commit data", file=sys.stderr)
        sys.exit(1)

    commit_data['version'] = version

    error = None
    main_program_dir = path.dirname(path.abspath(__file__))
    base_dir = path.dirname(main_program_dir)
    os.makedirs(path.join(base_dir, 'data_no_git'), exist_ok=True)
    file_path = path.join(base_dir, 'data_no_git', 'version_info.json')
    try:
        with open(file_path, 'w') as jf:
            json.dump(commit_data, jf, indent=4)
    except IOError as e:
        error = f"File I/O error: {e}"
    except TypeError as e:
        error = f"Type error: {e}"
    except Exception as e:
        error = f"Unexpected error: {e}"

    if error:
        print(error, file=sys.stderr)
        sys.exit(1)

    print(f"Successfully updated version info to {file_path}")

if __name__ == "__main__":
    version = "1.0.0"  # You can update this manually or retrieve it dynamically
    update_version_file(version)