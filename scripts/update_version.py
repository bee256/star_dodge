import subprocess

def get_git_commit_info():
    try:
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip().decode('utf-8')
        commit_date = subprocess.check_output(['git', 'log', '-1', '--format=%cd', '--date=short']).strip().decode('utf-8')
        branch_name = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf-8')
        author_name = subprocess.check_output(['git', 'log', '-1', '--format=%an']).strip().decode('utf-8')
        commit_message = subprocess.check_output(['git', 'log', '-1', '--format=%s']).strip().decode('utf-8')
        is_dirty = subprocess.check_output(['git', 'status', '--porcelain']).strip().decode('utf-8') != ''
        return commit_hash, commit_date, branch_name, author_name, commit_message, is_dirty
    except subprocess.CalledProcessError:
        return None, None, None, None, None, None

def update_version_file(version):
    commit_hash, commit_date, branch_name, author_name, commit_message, is_dirty = get_git_commit_info()
    with open('utils/version_info.py', 'w') as f:
        f.write(f'__version__ = "{version}"\n')
        if commit_hash and commit_date:
            f.write(f'__commit__ = "{commit_hash}"\n')
            f.write(f'__commit_date__ = "{commit_date}"\n')
            f.write(f'__branch__ = "{branch_name}"\n')
            f.write(f'__author__ = "{author_name}"\n')
            f.write(f'__commit_message__ = "{commit_message}"\n')
            f.write(f'__dirty__ = {is_dirty}\n')
        else:
            f.write(f'__commit__ = "unknown"\n')
            f.write(f'__commit_date__ = "unknown"\n')
            f.write(f'__branch__ = "unknown"\n')
            f.write(f'__author__ = "unknown"\n')
            f.write(f'__commit_message__ = "unknown"\n')
            f.write(f'__dirty__ = False\n')

if __name__ == "__main__":
    version = "1.0.0"  # You can update this manually or retrieve it dynamically
    update_version_file(version)