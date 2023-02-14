#!/bin/bash -x

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# TODO: consider evolving in more sophisticated manner:
# https://pypi.org/project/pytest-console-scripts/
# https://github.com/sstephenson/bats
# https://github.com/cucumber/aruba
# https://spin.atomicobject.com/2016/01/11/command-line-interface-testing-tools/

echo "Very simple functional/sanity test."
echo "It just runs the tested commands and expect they will not fail"

export PIP_EXTRA_INDEX_URL=${PIP_EXTRA_INDEX_URL:-https://test.pypi.org/simple/}


start=$SECONDS

function fail () {
  duration=$(( SECONDS - start ))

  read -r -d '' REPORT << EOM
<testsuites>
  <testsuite name="suite">
    <testcase classname="bash" name="simple-functional-test.sh" time="$duration">
      <failure message="$1"/>
    </testcase>
  </testsuite>
</testsuites>
EOM
  echo $REPORT > tests.xml
  exit 3
}

function pass() {
  duration=$(( SECONDS - start ))

  read -r -d '' REPORT << EOM
<testsuites>
  <testsuite name="simple-functional-test">
    <testcase classname="bash" name="simple-functional-test.sh" time="$duration">
    </testcase>
  </testsuite>
</testsuites>
EOM
  echo $REPORT> tests.xml
  exit 0
}

echo "Create vdk distribution and install it"
rm -rf dist/*
python setup.py sdist --formats=gztar && pip install dist/* || fail "VDK Install failed"

function restore_vdk_in_editable_mode {
  pip install -e .
  pip install --extra-index-url $PIP_EXTRA_INDEX_URL -e ./../vdk-plugins/vdk-trino
  pip install --extra-index-url $PIP_EXTRA_INDEX_URL -e ./../vdk-plugins/vdk-plugin-control-cli
}
trap restore_vdk_in_editable_mode EXIT

echo "Install database plugin for presto support"
pushd ../vdk-plugins/vdk-trino || exit
rm -rf dist/*
python setup.py sdist --formats=gztar && pip install dist/* || fail "vdk-trino plugin Install failed"
popd || exit

echo "Install vdk-control-cli plugin"
pushd ../vdk-plugins/vdk-plugin-control-cli || exit
rm -rf dist/*
python setup.py sdist --formats=gztar && pip install --extra-index-url $PIP_EXTRA_INDEX_URL dist/* || fail "vdk-control-cli plugin Install failed"
popd || exit

echo "Run commands ..."
vdk  || fail "vdk command failed"
vdk hello  || fail "vdk hello command failed"
vdk deploy --help || fail "vdk-control-cli deploy --help command failed"

vdk version || fail "vdk version failed"

export VDK_TRINO_HOST='localhost'
export VDK_TRINO_PORT=8080
export VDK_TRINO_USE_SSL=False
export VDK_TRINO_SCHEMA='default'
export VDK_TRINO_CATALOG='memory'
export VDK_TRINO_USER=example-job-user
export VDK_DB_DEFAULT_TYPE='TRINO'


VDK_TRINO_DOCKER_START=${VDK_TRINO_DOCKER_START:-yes}
echo $VDK_TRINO_DOCKER_START
if [ "$VDK_TRINO_DOCKER_START" = 'yes' ]; then
  docker stop trino || :
  docker rm trino || :
  docker run -d -p 8080:8080 --name trino --health-cmd="trino --execute 'select 1'" trinodb/trino
  #until docker inspect --format "{{json .State.Health.Status }}" trino | grep healthy; do sleep 3; done
fi
until vdk trino-query -q 'select 1'; do sleep 3; done

vdk run cicd/example-job || fail "vdk run example-job command failed"

if [ "$VDK_TRINO_DOCKER_START" = 'yes' ]; then
  docker stop trino || :
  docker rm trino || :
fi

pass
