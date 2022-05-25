import os
from struct import pack
from tqdm import tqdm
from yocto_tools_lib import *
import hashlib

class RosRecipeInfo:
    def __init__(self):
        self.name = ''
        self.license = ''
        self.lic_files_chksum = ''
        self.dependency = []
        self.srcrev = ''
    
    def print(self):
        print('LICENSE:',self.license)
        print('LIC_FILE_CHKSUM:',self.lic_files_chksum)
        print('DEPENDENCY:',self.dependency)
        print('SRCREV:',self.srcrev)

def init():
    os.system('git checkout master')
    os.system('git reset --hard')
    move_to_top()
    os.system('sudo rm -r yocto_tools/recipes')
    return

def extract_ros_recipe_info(ros_package_name, ros_package_path):
    xml_path = ros_package_path+'/package.xml'
    
    info = RosRecipeInfo()
    info.name = ros_package_name
    
    xml = []
    with open(xml_path) as f:
        xml.extend(f.readlines())
    
    for i in range(len(xml)):
        line = xml[i]
        line_num = i + 1
        
        if 'license>' in line:
            license = line.split('>')[1]
            license = license.split('<')[0]
            if(license == 'Apache 2'): license = 'Apache-2.0'
            info.license = license
            
            lic_chksum_value = hashlib.md5(line.encode()).hexdigest()
            if ros_package_name == 'lidar_localizer':
                lic_chksum_value = '7d942f6573dba1c22962da3cdf66dbc0'

            lic_files_chksum = 'file://package.xml;beginline='+str(line_num)+';endline='+str(line_num)+';md5='+lic_chksum_value
            info.lic_files_chksum = lic_files_chksum
            
        elif 'depend>' in line and 'buildtool_depend' not in line:
            dependency = line.split('>')[1]
            dependency = dependency.split('<')[0]
            dependency = dependency.replace('_','-')

            if dependency == 'tinyxml':
                dependency = 'libtinyxml'
            elif dependency == 'ndt-gpu':
                continue
            elif dependency == 'libpcl-all-dev' or dependency == 'libpcl-dev' or dependency == 'libpcl-all':
                dependency = 'pcl'
            elif dependency == 'python-serial':
                dependency = 'python-pyserial'
            elif dependency == 'python-threading':
                dependency = 'python'
            elif dependency == 'libglew-dev':
                dependency = 'glew'
            elif dependency == 'python-yaml':
                dependency = 'python-pyyaml'
            elif dependency == 'eigen':
                dependency = 'libeigen'
            elif dependency == 'libopencv-dev':
                dependency = 'opencv'
            elif dependency == 'qtbase5-dev':
                dependency = 'qtbase'
            elif dependency == 'serial':
                dependency = 'rosserial'
            
            if dependency.endswith('-dev'):
                dependency = dependency[:-4]

            if dependency not in info.dependency:
                info.dependency.append(dependency)
    
    os.system('git log -n 1 origin/'+ros_package_name+' | head -1 > srcrev_tmp.txt')
    
    srcrev = ''
    with open('srcrev_tmp.txt') as f:
        srcrev = f.readline()
    
    srcrev = srcrev.split(' ')[1]
    srcrev = srcrev.strip('\n')
    info.srcrev = srcrev
     
    os.system('rm srcrev_tmp.txt')

    return info

def create_ros_recipe_context(ros_recipe_info):
    recipe_context = []
    
    recipe_context.append('inherit ros_distro_melodic\n')
    recipe_context.append('inherit ros_superflore_generated\n\n')
    recipe_context.append('DESCRIPTION = \"The '+ros_recipe_info.name+' package\"\n')
    recipe_context.append('AUTHOR = \"Hayeon Park <kite9240@gmail.com>\"\n')
    recipe_context.append('HOMEPAGE = \"https://none\"\n')
    recipe_context.append('SECTION = \"devel\"\n\n')
    recipe_context.append('LICENSE = \"'+ros_recipe_info.license+'\"\n')
    recipe_context.append('LIC_FILES_CHKSUM = \"'+ros_recipe_info.lic_files_chksum+'\"\n\n')
    recipe_context.append('ROS_CN = \"'+ros_recipe_info.name+'\"\n')
    recipe_context.append('ROS_BPN = \"'+ros_recipe_info.name+'\"\n\n')
    
    recipe_context.append('ROS_BUILD_DEPENDS = \" \\\n')
    for dependency in ros_recipe_info.dependency:
        recipe_context[-1] = recipe_context[-1] + '\t'+dependency+' \\\n'
    recipe_context[-1] = recipe_context[-1] + '\"\n\n'
    
    recipe_context.append('ROS_BUILDTOOL_DEPENDS = " \\\n\tcatkin-native \\\n\"\n\n')
    
    recipe_context.append('ROS_EXPORT_DEPENDS = \" \\\n')
    for dependency in ros_recipe_info.dependency:
        recipe_context[-1] = recipe_context[-1] + '\t'+dependency+' \\\n'
    recipe_context[-1] = recipe_context[-1] + '\"\n\n'
    
    recipe_context.append('ROS_BUILDTOOL_EXPORT_DEPENDS = \"\"\n\n')
    
    recipe_context.append('ROS_EXEC_DEPENDS = \" \\\n')
    for dependency in ros_recipe_info.dependency:
        recipe_context[-1] = recipe_context[-1] + '\t'+dependency+' \\\n'
    recipe_context[-1] = recipe_context[-1] + '\"\n\n'
    
    recipe_context.append('ROS_TEST_DEPENDS = \"\"\n\n')
    recipe_context.append('DEPENDS = \"${ROS_BUILD_DEPENDS} ${ROS_BUILDTOOL_DEPENDS}\"\n')
    recipe_context.append('DEPENDS += \"${ROS_EXPORT_DEPENDS} ${ROS_BUILDTOOL_EXPORT_DEPENDS}\"\n\n')
    recipe_context.append('RDEPENDS_${PN} += \"${ROS_EXEC_DEPENDS}\"\n\n')
    recipe_context.append('ROS_BRANCH = \"branch='+ros_recipe_info.name+'\"\n')
    recipe_context.append('SRC_URI = \"git://github.com/rubis-lab/ExynosAutoware;${ROS_BRANCH};protocol=https\"\n')
    recipe_context.append('SRCREV = \"'+ros_recipe_info.srcrev+'\"\n')
    recipe_context.append('S = \"${WORKDIR}/git\"\n\n')
    recipe_context.append('ROS_BUILD_TYPE = \"cmake\"\n\n')
    recipe_context.append('inherit ros_catkin\n')
    recipe_context.append('BBCLASSEXTEND_append = \"native nativesdk\"\n\n')

    recipe_context.append('FILES_${PN} += \" \\\n')
    recipe_context.append('\t${ros_libdir}/*/* \\\n')
    recipe_context.append('\"\n\n')

    recipe_context.append('FILES_${PN}-dev += \" \\\n')
    recipe_context.append('\t${ros_libdir}/*/* \\\n')
    recipe_context.append('\"')
    
    return recipe_context

def write_recipe_file(recipe_name, ros_recipe_context, recipe_version):
    recipe_name = recipe_name.replace('_','-')
    recipe_path = 'yocto_tools/recipes/'+recipe_name
    os.system('mkdir yocto_tools/recipes > /dev/null 2>&1')
    os.mkdir(recipe_path)
    f = open(recipe_path+'/'+recipe_name+'_'+recipe_version+'.bb','w')
    for line in ros_recipe_context:
        f.write(line)
    f.close()
    
    return

def main():
    init()

    recipe_version = "1.0" # Version of recipes
    
    # Create recipes for autoware.ai    
    autoware_path = 'autoware.ai/src'
    cateogries = get_dirs(autoware_path)
    
    for category in cateogries:
        category_path = os.path.join(autoware_path, category)
        package_groups = get_dirs(category_path)
        for package_group in package_groups:
            package_group_path = os.path.join(category_path, package_group)
            packages = get_dirs(package_group_path)
            
            print('Create recipes in autwoare_ws/src/'+category+'/'+package_group)        
            pb = tqdm(range(len(packages))) # progress bar
            for i in pb:
                package = packages[i]
                package_path = os.path.join(package_group_path, package)
                
                pb.set_description(package)
                info = extract_ros_recipe_info(package, package_path)
                ros_recipe_context = create_ros_recipe_context(info)
                write_recipe_file(package, ros_recipe_context, recipe_version)
    
    # Update rubis_ws
    rubis_ws_path = 'rubis_ws/src'
    packages = get_dirs(rubis_ws_path)

    print('Update packages in rubis_ws')
    pb = tqdm(range(len(packages)))
    for i in pb:
        package = packages[i]
        package_path = os.path.join(rubis_ws_path, package)
        
        pb.set_description(package)
        info = extract_ros_recipe_info(package, package_path)
        ros_recipe_context = create_ros_recipe_context(info)
        write_recipe_file(package, ros_recipe_context, recipe_version)
        
    return

if __name__ == '__main__':
    main()