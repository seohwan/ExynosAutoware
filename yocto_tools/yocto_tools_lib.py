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
    
    blacklist = ['origin/master', 'origin/main']
    for target in blacklist:
        if target in branches:
            branches.remove(target)
    
    branches = [branch for branch in branches if not branch.startswith('origin/HEAD')]
    
    return branches

def get_dirs(path):
    dirs = []
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            dirs.append(file)

    return dirs

def get_dirs_and_branches_for_rubis_ws(path):
    dirs = []
    branches = []
    for file in os.listdir(path):
        if file == 'image_common':
            if os.path.isdir(os.path.join(path, file)):
                dirs.append('image_common/image_transport')
                branches.append('image_transport')
            continue
        elif file == 'ros-bridge':
            continue
        elif file == 'carla_autoware_bridge':
            continue
        elif file == 'vesc':
            if os.path.isdir(os.path.join(path, file)):        
                dirs.append('vesc/vesc_ackermann')
                dirs.append('vesc/vesc_driver')
                dirs.append('vesc/vesc_msgs')
                branches.append('vesc_ackermann')
                branches.append('vesc_driver')
                branches.append('vesc_msgs')
            continue
        elif file == 'inertiallabs_pkgs':   
            if os.path.isdir(os.path.join(path, file)):                     
                dirs.append('inertiallabs_pkgs/inertiallabs_ins')
                dirs.append('inertiallabs_pkgs/inertiallabs_msgs')
                branches.append('inertiallabs_ins')
                branches.append('inertiallabs_msgs')
            continue
        elif file == 'gicp_localizer':
            continue
        elif file == 'carla_points_map_loader':
            continue
        elif file == 'CAN_translate':
            if os.path.isdir(os.path.join(path, file)):
                dirs.append('CAN_translate/can_translate')
                branches.append('can_translate')
            continue

        if os.path.isdir(os.path.join(path, file)):
            dirs.append(file)
            branches.append(file)            
    
    return dirs, branches

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
    os.system('cp -r autoware.ai ..')
    os.system('cp -r rubis_ws ..')
    print('Source codes are copied to ExynosAutoware/..')
    return

def remove_copied_source_codes():
    os.system('sudo rm -r ../autoware.ai')
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
    
    os.system('git checkout -f '+branch_name+null_command)
    os.system('git reset --hard'+null_command)
    os.system('sudo rm -r *'+null_command)
    os.system('cp -r '+src_path+'/* .'+null_command)
    os.system('git add -A'+null_command)
    os.system('git commit -m \"Updated at +'+str(datetime.now())+'\"'+null_command)
    os.system('git push --force origin '+branch_name+null_command)
    
    return

def delete_branch(branch_name):
    os.system('git push origin --delete '+branch_name)
    
    return