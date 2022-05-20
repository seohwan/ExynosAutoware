#!/bin/sh
cd recipes
zip -r recipes.zip *
scp -P 2222 recipes.zip exynos@uranium.snu.ac.kr:/home/exynos/ssd/hypark/ros/sources/meta-samsung-virt/meta-sys/recipes-autoware