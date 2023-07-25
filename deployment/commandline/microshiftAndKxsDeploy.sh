#! /bin/bash

FPS=7

# check if required parameter is present in command line
if [ $#  -lt 1  ]; then
        echo "Usage: $0 amd64|arm64 [targetFps]"
        exit 1
fi
if [ \( $1  != "amd64" \) -a \( $1 != "arm64" \) ]; then
        echo "Usage: $0 amd64|arm64 [targetFps]"
        exit 2
fi
if [ $1 == "arm64" ]; then
        SUFFIX="-$1"
fi

# check if targetFps has been specified
if [ $# -gt 1 ]; then
        re='^[0-9]+$'
        if ! [[ $2 =~ $re ]] ; then
                echo "Usage: $0 amd64|arm64 [targetFps]"
                exit 3
        else
                FPS=$2
        fi
fi

#echo "SUFFIX=$SUFFIX"
#echo "FPS=$FPS"


# create dictionary to check if projects already exist
declare -A DICTIONARY
NAMESPACES=`kubectl get ns --no-headers | awk '{print $1}'`
printf 'Namespaces found:\n'
echo "-------------------------------------------------------------------"
for NS in $NAMESPACES
do 
    echo $NS
    DICTIONARY[$NS]=1
done

# check if project already exists
CONFIFMAP_NS=edge-server
declare -a EDGE_NAMESPACES=("edge-demo")
for NS in ${EDGE_NAMESPACES[@]}
do
    echo "*******************************************************************"
    if [ -n "${DICTIONARY[$NS]}" ]; then
        printf 'Namespace %s exists, skipping deployment\n' "$NS"
    else
        printf 'Namespace %s does not exist, creating namespace and doing deployment\n' "$NS"
        echo "-------------------------------------------------------------------"
        kubectl create namespace $NS
	sed -i -e '/TARGET_FPS/!b; n; s/"[0-9]*"/'\""$FPS"\"'/' edge-demo${SUFFIX}.yaml	
        kubectl create -f edge-demo${SUFFIX}.yaml -n $NS
        sleep 5
    fi
done
echo "*******************************************************************"

exit 0
