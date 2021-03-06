#!/bin/bash
#
#
VIRTUALENV=${VIRTUALENV:=virtualenv}
TMPBUILDDIR=${TMPBUILDDIR:=pyenv}
BASKET=${BASKET:=-f http://localhost/basket}
SRC=`pwd`/lib

# Build Test Environment:
echo "Building Test Environment"
${VIRTUALENV} --clear $TMPBUILDDIR
source ${TMPBUILDDIR}/bin/activate
${TMPBUILDDIR}/bin/easy_install ${BASKET} nose NoseXUnit coverage pylint

if [ "$?" == 0 ]
then
    echo "Running all tests"
    ${TMPBUILDDIR}/bin/nosetests -sv --with-nosexunit --source-folder=$SRC --enable-cover
    #  --enable-cover --enable-audit
else
    echo "Test dependancy install FAILED!"
fi

# Build egg and source distribution:
${TMPBUILDDIR}/bin/python setup.py bdist_egg
${TMPBUILDDIR}/bin/python setup.py sdist

# Clean up
deactivate
echo "Clean up: "${TMPBUILDDIR}
rm -rf ${TMPBUILDDIR}
