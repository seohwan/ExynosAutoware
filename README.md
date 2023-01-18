# ExynosAutoware

The RUBIS Autoware project for Exynos Board.
# Setup
1. Install `rubis-lab/Autoware_On_Embedded`.
2. Setup `WORKSPACE_PATH` in `yocto_tools/move_recipes.sh`

# How to Use

1. Modify source codes in `autoware.ai` and `rubis_ws`.
3. Copy source codes from `autoware.ai` and `rubis_ws`
    ```
    cd yocto_tools
    python3 synchronize_source.py 
    ```
4. Do commit.
5. Update branches.
    ```
    python3 udpate_repository.py
    ```
6. Create and move meta-autoware recipes.
    ```
    cd ../yocto_tools
    python3 create_recipes.py
    sh move_recipes.sh
    ```

# Master Branch 
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
- `yocto_tools/synchronize_source.py`
    * Syncrhonize source codes in `autoware.ai` and `rubis_ws` when they are located in `$HOME` directory.
- `yocto_tools/update_repository.py`
    * Automatically create and update branch of remote repository based on current `master` branch.
- `yocto_tools/create_recipes.py`
    * Create Yocto recipes to `yocto_tools/recipes` based on `autoware.ai` and `rubis_ws`.
- `yotcto_tools/move_recipes.sh`
    * Move autoware recipes to `recipes-autoware`. 