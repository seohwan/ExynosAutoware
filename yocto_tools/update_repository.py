import os
from datetime import datetime
from tqdm import tqdm
from yocto_tools_lib import *
import subprocess

def init():
    os.system('git checkout master')    
    move_to_top()
    null_command = ' > /dev/null 2>&1'
    os.system('sudo rm -r ../autoware.ai'+null_command)
    os.system('sudo rm -r ../rubis_ws'+null_command)
    copy_source_codes()    
    return

def main():
    
    init()
    remote_branches = get_remote_branches()

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

            print('Update packages in autoware.ai/src/'+category+'/'+package_group)
            
            pb = tqdm(range(len(packages))) # progress bar
            for i in pb:
                package = packages[i]
                package_path = os.path.join(package_group_path, package)
                branch_name = package
                pb.set_description(branch_name)
                
                if branch_name not in remote_branches: # Branch is not exist
                    create_branch(branch_name, package_path)
                else:
                    update_branch(branch_name, package_path)
                    remote_branches.remove('origin/'+branch_name)
    
    # Update rubis_ws
    rubis_ws_path = '../rubis_ws/src'
    packages, rubis_ws_branches = get_dirs_and_branches_for_rubis_ws(rubis_ws_path)
    for branch in rubis_ws_branches:
        if branch not in local_branches: os.system('git checkout --force '+pkg)
    os.system('git checkout master')

    print('Update packages in rubis_ws')
    pb = tqdm(range(len(packages)))
    for i in pb:
        package = packages[i]
        package_path = os.path.join(rubis_ws_path, package)
        branch_name = rubis_ws_branches[i]        
        pb.set_description(branch_name)
        
        if branch_name not in remote_branches: # Branch is not exist
            create_branch(branch_name, package_path)
        else:
            update_branch(branch_name, package_path)
            remote_branches.remove('origin/'+branch_name)
    print(remote_branches)
    # Delete unexist branches    
    for branch in remote_branches:
        
        branch_name = branch.split('/')[1]
        print(branch, branch_name)
        # delete_branch(branch_name)
        
    terminate()
    
    return

if __name__ == '__main__':
    main()