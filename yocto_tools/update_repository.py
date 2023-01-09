import os
from datetime import datetime
from tqdm import tqdm
from yocto_tools_lib import *
import subprocess

def init():
    os.system('git checkout master')
    move_to_top()
    copy_source_codes()
    return

def main():
    
    init()
    branches = get_remote_branches()

    # Update autoware.ai    
    autoware_path = '../autoware.ai/src'
    cateogries = get_dirs(autoware_path)
    local_branches = str(subprocess.check_output('git branch', shell=True))

    for category in cateogries:
        category_path = os.path.join(autoware_path, category)
        package_groups = get_dirs(category_path)
        for package_group in package_groups:
            package_group_path = os.path.join(category_path, package_group)
            packages = get_dirs(package_group_path)
            for pkg in packages:
                if pkg not in local_branches: os.system('git checkout --force '+pkg)
            os.system('git checkout master')

            print('Update packages in autware.ai/src/'+category+'/'+package_group)
            
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
                    branches.remove(branch_name)
    
    # Update rubis_ws
    rubis_ws_path = '../rubis_ws/src'
    packages = get_dirs(rubis_ws_path)
    for pkg in packages:
        if pkg not in local_branches: os.system('git checkout --force '+pkg)
    os.system('git checkout master')

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
            branches.remove(branch_name)
    
    # Delete unexist branches    
    for branch in branches:
        branch_name = branch.split('/')[1]
        delete_branch(branch_name)
        
    terminate()
    
    return

if __name__ == '__main__':
    main()