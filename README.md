# ExynosAutoware

The RUBIS Autoware project for Exynos Board.

# Maaster Branch 
- The branch that contains source codes for building Autoware.
- All packages in `autoware.ai` and `rubis_ws` included in `Autoware_On_Embedded` repository should be located in autoware.ai and rubis_ws directories of master branch. (They can be easily ported by moving `Autoware_On_Embedded/autoware.ai` and `Autoware_On_Embedded/rubis_ws` to `ExynosAutoware/autoware.ai` and `ExynosAutoware/rubis_ws`, repectively.)
- All package level directories should have a `package.xml` file.
- Package level directories
    * `autoware.ai`: `autoware.ai/src/<category>/<package_group>/<package>`
    * `rubis_ws`: `rubis_ws/src/<package>`
- For example, `rubis_ws/src/image_common` has no `package.xml` in `Autoware_On_Embedded/rubis_ws`, so all packages in it should be moved to `rubis_ws/src`.

# Other Branches
- Each branch has ros package source codes.
- They are used to create Yocto recipes.

# Yocto Tools
- `yocto_tools/update_repository.py`
    * Automatically create and update branch of remote repository based on current `master` branch.
- `yocto_tools/create_recipes.py`
    * Create Yocto recipes to `yocto_tools/recipes` based on `autoware.ai` and `rubis_ws`.
- `yotcto_tools/move_recipes.sh`
    * Move compresed recipes(`recipes.zip`) to `recipes-autoware`. Shoud launch it in `yocto_tools` after recipe creation.

# How to run ssh with source shell script
```
ssh -t root@<ip> ' PROMPT_COMMAND=\"source <shell-script-in-server>\" exec sh'
```

# TODO
* Need to create opencl based `ndt_gpu` and `vision_darknet_detect` packages.
* Need to change paths in scritps for the ExynosAutoware project.
* Need to create `range_vision_fusion` that don't use `jsk_recognition_utils`. (It can be resolved when `python-skimage` recipe is generated).
