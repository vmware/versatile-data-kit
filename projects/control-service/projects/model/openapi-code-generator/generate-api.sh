#!/bin/sh


# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

#
# This script builds a Docker image that starts Control Plane Base
#
#

set -e
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  SCRIPTDIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$SCRIPTDIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
SCRIPTDIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
BRANCHROOT="$SCRIPTDIR/../../../"
#set -x
###################################################################################################


java -jar $SCRIPTDIR/openapi-generator-cli.jar generate --generator-name spring --config $SCRIPTDIR/config-spring.json --output $BRANCHROOT/model -i $SCRIPTDIR/../apidefs/datajob-api/api.yaml
rm -rf $BRANCHROOT/model/.openapi-generator*
rm  $BRANCHROOT/model/README.md
rm  $BRANCHROOT/model/pom.xml
