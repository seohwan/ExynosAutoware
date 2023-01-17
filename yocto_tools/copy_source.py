import os
import subprocess

# Autoware
paths = str(os.popen('find ../autoware.ai/src ').read())
exynos_autoware_paths = paths.split('\n')

remove_idx = []
for i, line in enumerate(exynos_autoware_paths):
    if '.cpp' in line \
        or '.c' in line \
        or '.cu' in line \
        or '.h' in line \
        or '.cpp' in line \
        or '.msg' in line : continue
    remove_idx.append(i)

for index in sorted(remove_idx, reverse=True):
    del exynos_autoware_paths[index]

autoware_copy_src_paths = []
for line in exynos_autoware_paths:     
    autoware_copy_src_paths.append(line.replace('../','~/'))
for i in range(len(autoware_copy_src_paths)):
    os.system('cp '+ autoware_copy_src_paths[i] + ' ' + exynos_autoware_paths[i])

# rubis_ws
paths = str(os.popen('find ../rubis_ws/src').read())
exynos_rubis_paths = paths.split('\n')

remove_idx = []
for i, line in enumerate(exynos_rubis_paths):
    if '.cpp' in line \
        or '.c' in line \
        or '.cu' in line \
        or '.h' in line \
        or '.cpp' in line \
        or '.msg' in line: continue
    remove_idx.append(i)

for index in sorted(remove_idx, reverse=True):
    del exynos_rubis_paths[index]

rubis_copy_src_paths = []
for line in exynos_rubis_paths:
    rubis_copy_src_paths.append(line.replace('../','~/'))

for i in range(len(rubis_copy_src_paths)):
    os.system('cp '+ rubis_copy_src_paths[i] + ' ' + exynos_rubis_paths[i])

print('finish')