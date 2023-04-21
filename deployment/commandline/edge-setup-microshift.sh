#! /bin/bash

# check if required parameter is present in command line
if [ $#  -gt 0  ]; then
	echo "No input parameters are required. Ingore."
fi


# create dictionary to check if projects already exist
declare -A DICTIONARY
PROJECTS=`oc projects -q`
for PROJECT in $PROJECTS
do 
    echo $PROJECT
    DICTIONARY[$PROJECT]=1
done

# check if project already exists
CONFIFMAP_PROJECT=edge-server
declare -a EDGE_PROJECTS=("robots" "apriltag" "rtsp" "edge-server")
for PROJECT in ${EDGE_PROJECTS[@]}
do
    echo "*******************************************************************"
    if [ -n "${DICTIONARY[$PROJECT]}" ]; then
        printf 'Project %s exists, skipping deployment\n' "$PROJECT"
    else
        printf 'Project %s does not exist, creating projet and doing deployment\n' "$PROJECT"
        echo "-------------------------------------------------------------------"
        oc create namespace $PROJECT
        oc create -f $PROJECT.yaml -n $PROJECT
        if [ $PROJECT == $CONFIFMAP_PROJECT ]; then
            oc create configmap config --from-file=properties.ini -n $PROJECT
        fi
        sleep 5
    fi
done
echo "*******************************************************************"