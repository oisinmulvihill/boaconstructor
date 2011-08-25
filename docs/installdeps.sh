#!/bin/bash
python -c "import docutils"
if [ "$?" == 1 ]
then
	easy_install -ZU docutils
else
	echo "docutils is present. No need to install."
fi

python -c "import sphinx"
if [ "$?" == 1 ]
then
	easy_install -ZU sphinx
else
	echo "sphinx is present. No need to install."
fi
