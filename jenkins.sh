#!/bin/bash
#
#
VIRTUALENV={VIRTUALENV:=virtualenv}
TMPBUILDDIR=${TMPBUILDDIR:=/tmp/p_`date +'%Y%m%d%H%M%S'`}
BASKET=${BASKET:=-i http://localhost/basket}
SRC=`pwd`/lib

# Build Test Environment:
echo "Building Test Environment"
${VIRTUALENV} $TMPBUILDDIR
source ${TMPBUILDDIR}/bin/activate
${TMPBUILDDIR}/bin/easy_install ${BASKET} nose NoseXUnit coverage pylint

if [ "$?" == 0 ]
then
    ${TMPBUILDDIR}/bin/nosetests -sv --with-nosexunit --source-folder=$SRC
    #  --enable-cover --enable-audit
else
    echo "Test dependancy install FAILED!"
fi

# Clean up
deactivate
echo "Clean up: "${TMPBUILDDIR}
rm -rf ${TMPBUILDDIR}
