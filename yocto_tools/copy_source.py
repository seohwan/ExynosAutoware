import os
import subprocess

# Autoware
paths = str(os.popen('find ../autoware.ai/src').read())
exynos_autoware_paths = paths.split('\n')

remove_idx = []
for i, line in enumerate(exynos_autoware_paths):
    if 'CMakeList' in line:
        remove_idx.append(i)
    elif 'package.xml' in line:
        remove_idx.append(i)
    elif '.launch' in line: 
        remove_idx.append(i)

for index in sorted(remove_idx, reverse=True):
    del paths[index]

autoware_copy_src_paths = []
for line in paths:
    autoware_copy_src_paths.append(line.replace('../','~/'))


for i in range(len(remove_idx)):
    os.system('mv '+ autoware_copy_src_paths[i] + ' ' + exynos_autoware_paths[i])


# rubis_ws
paths = str(os.popen('find ../rubis_ws/src').read())
exynos_rubis_paths = paths.split('\n')

remove_idx = []
for i, line in enumerate(exynos_rubis_paths):
    if 'CMakeList' in line or 'package.xml' in line or '.launch' in line: remove_idx.append(i)

for index in sorted(remove_idx, reverse=True):
    del paths[index]

rubis_copy_src_paths = []
for line in paths:
    rubis_copy_src_paths.append(line.replace('../','~/'))

for i in range(len(remove_idx)):
    os.system('mv '+ rubis_copy_src_paths[i] + ' ' + exynos_rubis_paths[i])

print('finish')