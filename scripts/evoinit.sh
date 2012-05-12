#!/bin/bash
# This file is part of Fetch (the Fact Extraction Tool CHain).
#
# Fetch is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Fetch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Anastacia; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Copyright 2007-2008  University of Antwerp
# Author(s): Bart Van Rompaey <bart.vanrompaey2@ua.ac.be>

# This script adapted by James Goodger, 2011 from initialization.sh

##
# initialization.sh is a script that encapsulates the initialization
# of script variables for both cpp2rsf.sh and java2rsf.sh
#
# In case you would like to reuse the variables initialized here,
# include this shell script by using the following line:
# . initialization.sh
##

function printLicense() {
	$ECHO "Fetch, Copyright (C) 2006-2008 University of Antwerp"
	$ECHO "Created by Bart Van Rompaey and Bart Du Bois, Lab On REengineering"
	$ECHO "Fetch is Open Source Software/Free Software, licensed under the"
	$ECHO "GNU GPL2."
}

function help() {
	printLicense
	$ECHO ""
	$ECHO "Usage: `basename $0` SRC_ROOT [options]"
	$ECHO "options:"
	$ECHO "	--graph				build graph model (all FAMIX levels)"
	$ECHO "	--help				this message"
	$ECHO "	--iemetrics			use IEMetrics for metrics"
	$ECHO "	--ncss				use cppncss for metrics"
	$ECHO "	--nocpp				don't create C preprocessor entities (except for includes)"
	$ECHO "	--nometrics			don't calculate size and complexity metrics"
	$ECHO "	--pmc				use pmccabe for metrics (default)"
	$ECHO "	--tree				build tree model (up to FAMIX Level 2)"
	$ECHO "	--vcs [filename] 	        file changes in version control"
	$ECHO "	--xvfb				use X virtual frame buffer instead of X)"
	$ECHO " --files [filename]		specify a text file with a list of files to analyse"
}

if [ -z "$SN_HOME" ]
then
	$ECHO "SN_HOME variable should be specified."
	exit 66
fi

XVFB=0 # 0 => don't use a Virtual Xserver
PMCM=1 # by default, do metrics via PMC
NCSSM=0 # by default don't do metrics via NCSS
HELP=0
TREE=0
CPP=1
OUTPUT_EXPECTED=0
TARGET=`pwd`

SN=$SN_HOME/snavigator
VCS=0
USE_FILES=0

# keep out of the remainder
ARGS=1

if [ $# -lt "$ARGS" ]
then
	$ECHO "Usage: `basename $0` SRC_ROOT [options]"
	$ECHO "     --vcs        Generate version control metrics"
	$ECHO "     --xvfb       Use X virtual framebuffer"
	$ECHO "     --nometrics  Don't generate metrics"
	$ECHO "     --pmc        Use pmccabe as metric engine"
	$ECHO "     --ncss       Use NCSS as metric engine"
	$ECHO "     --iemetrics  Use IEMetrics as metric engine"
	$ECHO "     --graph      Generate accesses and invocations (default)"
	$ECHO "     --tree       Don't generate accesses and invocations"
	$ECHO "     --nocpp      Don't generate preprocessor data"
	$ECHO "     --output     Use the given path as the output directory"
	exit 64
fi

printLicense

# command line parsing
for i in $*
do
	case $i in
	--vcs=*)
		VCS=1
		PREFIX=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
		VCS_PATH=$(cd `dirname "$PREFIX"` && pwd)
		VCS_FILE=`basename $PREFIX`
		;;
	--xvfb)
		XVFB=1
		;;
	--nometrics)
		PMCM=0
		NCSSM=0
		IEMETRICS=0
		;;
	--pmc)
		PMCM=1
		NCSSM=0
		IEMETRICS=0
		;;
	--ncss)
		PMCM=0
		NCSSM=1
		IEMETRICS=0
		;;
	--iemetrics)
		IEMETRICS=1
		PMCM=0
		NCSSM=0
		;;
	--graph)
		;;
	--tree)
		TREE=1
		;;
	--help)
		HELP=1
		;;
	--nocpp)
		CPP=0
		;;
	--output)
		OUTPUT_EXPECTED=1
		;;
	--files=*)
		USE_FILES=1
		PREFIX=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
		LIST_PATH=$(cd `dirname "$PREFIX"` && pwd)
		LIST_FILE=`basename $PREFIX`
		;;
	*)
		# unknown option
		# potentially the output path if expected
		if [ $OUTPUT_EXPECTED -eq "1" ]
		then
			OUTPUT_PATH=$(cd "$i" && pwd)
			if [ ! -d $OUTPUT_PATH ]
			then
				$ECHO -n "$OUTPUT_DIR is not an existing path"
				$ECHO "[exiting]"
				exit 66
			fi
			TARGET=$OUTPUT_PATH
			OUTPUT_EXPECTED=0
		fi
		;;
	esac
done

$ECHO "Storing output in directory $TARGET."
SNAVTOFAMIXLOGFILE=$TARGET/snavtofamix.log

if [ $HELP -eq "1" ]
then
	help
	exit 0
fi

if [[ "$1" =~ ^- ]]
then
	help
	exit 0
fi

SRC_PATH=$(cd "$1" && pwd)
if [ ! -d $SRC_PATH ]
then
  $ECHO -N "$SRC_PATH is not an existing path"
  $ECHO "[exiting]"
  exit 66
fi

PROJ_NAME=`basename $SRC_PATH`

if [ $XVFB -eq 1 ]
then
	# Virtual X, we don't need an X server to be running for Source Navigator
	# http://en.wikipedia.org/wiki/Xvfb
	# http://www.neowin.net/forum/index.php?showtopic=449055
	# search free slot for Xserver
	for i in `seq 3000 4000`
	do
	        if [ ! -f /tmp/.X$i-lock ]
	                then
	                        display=$i
	                        break
	        fi
	done
	DISPLAY=:$display
fi

