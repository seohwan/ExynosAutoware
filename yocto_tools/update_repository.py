import os
from datetime import datetime
from tqdm import tqdm

def get_remote_branches():
    branches = []
    os.system('git branch -r > tmp.txt')
    with open('tmp.txt') as f:
        branches.extend(f.readlines())
    os.system('rm tmp.txt')

    branches = branches[1:]
    for i in range(len(branches)):
        branch = branches[i]
        branches[i] = branch.strip()
    
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

def init():
    os.system('git checkout master')
    move_to_top()
    copy_source_codes()
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

def main():
    
    init()
    branches = get_remote_branches()

    # Update autoware_ws    
    autoware_ws_path = '../autoware_ws/src'
    cateogries = get_dirs(autoware_ws_path)

    for category in cateogries:
        category_path = os.path.join(autoware_ws_path, category)
        package_groups = get_dirs(category_path)
        for package_group in package_groups:
            package_group_path = os.path.join(category_path, package_group)
            packages = get_dirs(package_group_path)
            print('Update packages in autwoare_ws/src/'+category+'/'+package_group)
            
            pb = tqdm(range(len(packages))) # progress bar
            for i in pb:
                package = packages[i]
                package_path = os.path.join(package_group_path, package)
                branch_name = 'origin/'+package
                pb.set_description(package)
                
                if branch_name not in branches: # Branch is not exist
                    create_branch(package, package_path)
                else:
                    update_branch(package, package_path)
    
    # Update rubis_ws
    rubis_ws_path = '../rubis_ws/src'
    packages = get_dirs(rubis_ws_path)

    print('Update packages in rubis_ws')
    pb = tqdm(range(len(packages)))
    for i in pb:
        package = packages[i]
        package_path = os.path.join(rubis_ws_path, package)
        branch_name = 'origin/'+package        
        pb.set_description(package)
        
        if branch_name not in branches: # Branch is not exist
            create_branch(package, package_path)
        else:
            update_branch(package, package_path)
        
    terminate()
    
    return

if __name__ == '__main__':
    main()