#!/usr/bin/env bash

docker exec -t qgis sh -c "cd /tests_directory/ && qgis_testrunner.sh tests.qgis.runner.test_package"
