#!/bin/sh
WORKSPACE_PATH="/home/hayeonp/Exynos/ws"
cd recipes
zip -r recipes.zip *
sudo rm -r $WORKSPACE_PATH/sources/meta-samsung-virt/meta-sys/recipes-autoware/*
cp recipes.zip $WORKSPACE_PATH/sources/meta-samsung-virt/meta-sys/recipes-autoware
cd $WORKSPACE_PATH/sources/meta-samsung-virt/meta-sys/recipes-autoware
unzip -o recipes.zip
rm -r recipes.zip