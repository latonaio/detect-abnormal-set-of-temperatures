#!/bin/bash

IMAGE_NAME="detect-abnormal-set-of-temperatures-base"

docker build -f Dockerfile-base -t ${IMAGE_NAME}:latest .
