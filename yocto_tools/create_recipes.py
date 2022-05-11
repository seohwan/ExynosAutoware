import os
import tqdm

def main():
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
                    branches.remove(branch_name)
                    
    return

if __name__ == '__main__':
    main()