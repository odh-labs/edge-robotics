#! /bin/bash

FPS=7

# check if required parameter is present in command line
if [ $#  -ne 1  ]; then
	echo "Usage: $0 loggedInUser [targetFps]"
	exit 1
fi

# check if targetFps has been specified
if [ $# -gt 1 ]; then
        re='^[0-9]+$'
        if ! [[ $2 =~ $re ]] ; then
                echo "Usage: $0  loggedInUser [targetFps]"
                exit 3
        else
                FPS=$2
        fi
fi

USER=$1

#echo "USER=$USER"
#echo "FPS=$FPS"

# check if intended user has logged in
WHO=`oc whoami`
if [ $USER == $WHO ]; then
    echo "Using $USER to deploy all components..."
else
    echo "Please log in as $USER and try again."
    exit 1
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
declare -a EDGE_PROJECTS=("edge-demo")
for PROJECT in ${EDGE_PROJECTS[@]}
do
    echo "*******************************************************************"
    if [ -n "${DICTIONARY[$PROJECT]}" ]; then
        printf 'Project %s exists, skipping deployment\n' "$PROJECT"
    else
        printf 'Project %s does not exist, creating project and doing deployment\n' "$PROJECT"
        echo "-------------------------------------------------------------------"
        oc new-project $PROJECT
	sed -i -e '/TARGET_FPS/!b; n; s/"[0-9]*"/'\""$FPS"\"'/' edge-demo.yaml
        oc create -f edge-demo.yaml
    fi
done
echo "*******************************************************************"

exit 0
