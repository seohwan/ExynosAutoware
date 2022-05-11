#!/bin/sh
zip -r recipes/recipes.zip recipes/*
scp -P 2222 recipes/recipes.zip exynos@uranium.snu.ac.kr:/home/exynos/ssd/hypark/ros/sources/meta-samsung-virt/meta-sys/recipes-autoware