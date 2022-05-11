import os
from datetime import datetime

def get_remote_branches():
    branches = []
    os.system('git branch -r > tmp.txt')
    with open('tmp.txt') as f:
        branches.extend(f.readlines())
    os.system('rm tmp.txt')

    for i in range(len(branches)):
        branch = branches[i]
        branches[i] = branch.strip()
    
    branches.remove('origin/master')
    branches.remove('origin/main')
    branches.remove('origin/inertiallabs_sdk')
    branches = [branch for branch in branches if not branch.startswith('origin/HEAD')]
    
    return branches

def get_dirs(path):
    dirs = []
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            dirs.append(file)

    return dirs

def move_to_top():
    cur_path = os.path.dirname(os.path.realpath(__file__))
    tokens = cur_path.split('/')
    tokens = tokens[1:]

    path = ''
    for token in tokens:
        path = path + '/' + token
        if token == 'ExynosAutoware': break
    
    if('ExynosAutoware' not in path):
        print('[ERROR] Cannot find the path to ExynosAutoware')
        exit(1)
    os.chdir(path)

    return

def copy_source_codes():
    os.system('cp -r autoware_ws ..')
    os.system('cp -r rubis_ws ..')
    print('Source codes are copied to ExynosAutoware/..')
    return

def remove_copied_source_codes():
    os.system('sudo rm -r ../autoware_ws')
    os.system('sudo rm -r ../rubis_ws')
    return

def terminate():
    os.system('git checkout -f master')
    os.system('git reset --hard')
    remove_copied_source_codes()
    return

def create_branch(branch_name, src_path):
    null_command = ' > /dev/null 2>&1'

    os.system('git checkout -f -b '+branch_name+null_command)
    os.system('git push origin '+branch_name+':'+branch_name+null_command)
    os.system('sudo rm -r *'+null_command)
    os.system('cp -r '+src_path+'/* .'+null_command)
    os.system('git add -A'+null_command)
    os.system('git commit -m \"branch '+branch_name+' is created.\"'+null_command)
    os.system('git push origin '+branch_name+null_command)
    
    return

def update_branch(branch_name, src_path):
    null_command = ' > /dev/null 2>&1'
    
    os.system('git switch -f '+branch_name+null_command)
    os.system('git reset --hard'+null_command)
    os.system('sudo rm -r *'+null_command)
    os.system('cp -r '+src_path+'/* .'+null_command)
    os.system('git add -A'+null_command)
    os.system('git commit -m \"Updated at +'+str(datetime.now())+'\"'+null_command)
    os.system('git push origin '+branch_name+null_command)
    
    return

def delete_branch(branch_name):
    os.system('git push origin --delete '+branch_name)
    
    return