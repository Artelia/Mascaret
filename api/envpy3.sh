#!/bin/bash

    # TELEMAC
export HOMETEL=/home/daoum/Documents/Travail/Telemac/trunk
export USETELCFG='API3gfortrans'
#export USETELCFG='API3gfortran_static'
export PYTHONUNBUFFERED='true'
export SYSTELCFG=$HOMETEL/configs/systel.cfg
export PYTHONPATH=$HOMETEL/scripts/python3/:$PYTHONPATH
export PATH=$HOMETEL/scripts/python3/:$PATH
export LD_LIBRARY_PATH=$HOMETEL/builds/$USETELCFG/wrap_api/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$HOMETEL/builds/$USETELCFG/wrap_api/lib:$PYTHONPATH



echo "fin"
