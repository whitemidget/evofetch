#!/bin/bash
# This file is part of Fetch (the Fact Extraction Tool CHain).
#
# Fetch is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# Fetch is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with outputtest; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#
# Copyright 2007 Manuel Breugelmans <manuel.breugelmans@student.ua.ac.be>
#

# This script adapted by James Goodger, 2011 from generateCtrlStructInfo.sh

ARGS=3

if [ $# -lt "$ARGS" ]
then
	echo -e "Usage: `basename $0` PROJECT_PATH PROJECT_NAME TYPE\n\t with type any of [JCOND|JLOOP|CCOND|CLOOP] [options]"
	echo -e "options:"
	echo -e "        --files=filename		specify a text file with a list of files to analyse"
	exit -1
fi

PROJ_PATH=$1
PROJ_NAME=$2
TYPE=$3
USE_FILES=0

# command line parsing
for i in $*
do
	case $i in
	--files=*)
		USE_FILES=1
		PREFIX=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
		LIST_PATH=$(cd `dirname "$PREFIX"` && pwd)
		LIST_FILE=`basename $PREFIX`
		;;
	esac
done

function jcond {
	if [ $USE_FILES -eq 1 ]
	then
		cat $LIST_PATH/$LIST_FILE |\
		xargs cat |\
		$FETCH/scripts/parserExt/removeComments.pl |\
		grep -noHE "(( |	|^)(if|switch)( |	|\(|$))" |\
		sed -e "s#^(standard input)#$i#" -e 's#\./##' \
			>> "$PROJ_PATH/dbdump/$PROJ_NAME.conditionals"
	else
		for i in $(find -L . -name "*.java"); do
			cat "$i" |\
			$FETCH/scripts/parserExt/removeComments.pl |\
			grep -noHE "(( |	|^)(if|switch)( |	|\(|$))" |\
			sed -e "s#^(standard input)#$i#" -e 's#\./##' \
				>> "$PROJ_PATH/dbdump/$PROJ_NAME.conditionals"
		done
	fi
}

function jloop {
	if [ $USE_FILES -eq 1 ]
	then
		cat $LIST_PATH/$LIST_FILE |\
		xargs cat |\
		$FETCH/scripts/parserExt/removeComments.pl |\
		grep -noHE "(( |	|^)(for|while|do)( |	|\(|$))" |\
		sed -e "s#^(standard input)#$i#" -e 's#\./##' \
			>> "$PROJ_PATH/dbdump/$PROJ_NAME.loops"
	else
		for i in $(find -L . -name "*.java"); do
			cat "$i" |\
			$FETCH/scripts/parserExt/removeComments.pl |\
			grep -noHE "(( |	|^)(for|while|do)( |	|\(|$))" |\
			sed -e "s#^(standard input)#$i#" -e 's#\./##' \
				>> "$PROJ_PATH/dbdump/$PROJ_NAME.loops"
		done
	fi
}

function ccond {
	if [ $USE_FILES -eq 1 ]
	then
		cat $LIST_PATH/$LIST_FILE |\
		xargs cat |\
		$FETCH/scripts/parserExt/removeComments.pl |\
		grep -noHE "(( |	|^)(if|switch)( |	|\(|$))" |\
		sed -e "s#^(standard input)#$i#" -e 's#\./##' \
			>> "$PROJ_PATH/dbdump/$PROJ_NAME.conditionals"
	else
		for i in $(find -L . -name "*.cxx" -o -name "*.cpp" -o -name "*.c" -o -name "*.h" -o -name "*.hh" -o -name "*.hpp" -o -name "*.cc"); do
			cat "$i" |\
			$FETCH/scripts/parserExt/removeComments.pl |\
			grep -noHE "(( |	|^)(if|switch)( |	|\(|$))" |\
			sed -e "s#^(standard input)#$i#" -e 's#\./##' \
				>> "$PROJ_PATH/dbdump/$PROJ_NAME.conditionals"
		done
	fi
}

function cloop {
	if [ $USE_FILES -eq 1 ]
	then
		cat $LIST_PATH/$LIST_FILE |\
		xargs cat |\
		$FETCH/scripts/parserExt/removeComments.pl |\
		grep -noHE "(( |	|^)(for|while|do)( |	|\(|$))" |\
		sed -e "s#^(standard input)#$i#" -e 's#\./##' \
			>> "$PROJ_PATH/dbdump/$PROJ_NAME.loops"
	else
		for i in $(find -L . -name "*.cxx" -o -name "*.cpp" -o -name "*.c" -o -name "*.h" -o -name "*.hh" -o -name "*.hpp" -o -name "*.cc"); do
			cat "$i" |\
			$FETCH/scripts/parserExt/removeComments.pl |\
			grep -noHE "(( |	|^)(for|while|do)( |	|\(|$))" |\
			sed -e "s#^(standard input)#$i#" -e 's#\./##' \
				>> "$PROJ_PATH/dbdump/$PROJ_NAME.loops"
		done
	fi
}

case "$TYPE" in
	'JCOND')
		jcond
		;;
	'JLOOP')
		jloop
		;;
	'CCOND')
		ccond
		;;
	'CLOOP')
		cloop
		;;
	*)
		echo -e "Usage: `basename $0` PROJECT_PATH PROJECT_NAME TYPE\n\t with type any of [JCOND|JLOOP|CCOND|CLOOP] [options]"
		echo -e "options:"
		echo -e "        --files=filename		specify a text file with a list of files to analyse"
		;;
esac

