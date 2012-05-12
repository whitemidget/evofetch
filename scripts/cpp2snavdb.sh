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

# This script adapted by James Goodger, 2011 from cpp2rsf.sh

##
# cpp2navdb.sh is a script that handles the parsing of C++ code,
# abstracting away the underlying steps of
# (i) parsing using Source Navigator
# (ii) metrics collection using pmccabe (used to be 4c)
# (iii) dumping SN db to ascii tables
##

# The builtin echo command ignores the -n command
# Accordingly, we lookup the true echo command.
ECHO=`which echo`

if [ -z "$FETCH" ]
then
	$ECHO "FETCH variable should be specified."
	exit 66
fi

if [[ "1" -eq $NCSSM ]]
then
	if [ -z "$JAVA_HOME" ]
	then
		$ECHO "JAVA_HOME should point to a JVM >= 1.5"
		exit 66
	fi
fi

# Include the initalizations of variables
. $FETCH/scripts/evoinit.sh

$ECHO "This script relies on a robust parser."

# C++ specific
LOG_FILE=$TARGET/fetchCpp-$PROJ_NAME-RSF.log

if [ $XVFB -eq 1 ]
then
	Xvfb $DISPLAY -screen 0 800x600x16 -ac >> $LOG_FILE 2>> $LOG_FILE & # setup X virtual framebuffer
fi

# The number of executed steps
STEPS=7

# C++ specific
if [ -z "$PMC" ]
then
        $ECHO "PMC variable should point to the pmccabe binary in fetch/bin that
suits the host platform. Someday we automate this..."
        exit 66
fi


# SN run
rm -rf $LOG_FILE $SRC_PATH/$PROJ_NAME.proj $SRC_PATH/.snprj
cd $SRC_PATH
activityDescr="(1/$STEPS) Running Source Navigator"
$ECHO -n $activityDescr "..."
$ECHO $activityDescr >> $LOG_FILE 2>> $LOG_FILE
t1=`date '+%s'`

# use headless, virtual display
if [ $XVFB -eq 1 ]
then
	if [ $USE_FILES -eq 1 ]
	then
		DISPLAY=$DISPLAY $SN --batchmode --create --import $LIST_PATH/$LIST_FILE >> $LOG_FILE
	else		
		DISPLAY=$DISPLAY $SN --batchmode --create -D parser-ext="c++","*.[ch]pp *.cc *.hh *.c *.h *.cxx *.hxx" >> $LOG_FILE
	fi
else
	if [ $USE_FILES -eq 1 ]
	then
		$SN --batchmode --create --import $LIST_PATH/$LIST_FILE >> $LOG_FILE
	else
		$SN --batchmode --create -D parser-ext="c++","*.[ch]pp *.cc *.hh *.c *.h *.cxx *.hxx" >> $LOG_FILE
	fi
fi

if [ $? -ne 0 ]
then
	$ECHO " fail!"
	$ECHO "--> check $LOG_FILE for info"
	exit 69
else
	t2=`date '+%s'`
	t=`expr $t2 - $t1` # TODO: verify calculation of time using "expr" command
	$ECHO " pass ($t sec.)"
fi

# wait 1 second to let SN finish
sleep 1

# ensure that SourceNavigator is finished before continuingsh cpp
# credit to Filip Van Rysselberghe
on_windows=`uname -a | grep "CYGWIN"`

if [[ "$on_windows" != "" ]]
then
	$ECHO "Verifying checks"
	hyper_exists=`ps -W | grep "hyper.exe" | grep -v "grep"`
	while [ -n "$hyper_exists" ]
	do
	   sleep 5
	   hyper_exists=`ps -W | grep "hyper.exe" | grep -v "grep"`
	done
fi

if [ $XVFB -eq 1 ]
then
	# kill Xvfb
	process=`cat /tmp/.X$display-lock`
	kill $process
fi

rm -rf dbdump
mkdir dbdump

# dbdump
cd $FETCH/src/snavtofamix
activityDescr="(2/$STEPS) Dumping SN database"
$ECHO -n $activityDescr "..."
$ECHO $activityDescr >> $LOG_FILE
t1=`date '+%s'`
./snav_dbdumps.sh $SRC_PATH $PROJ_NAME $SRC_PATH/dbdump >> $LOG_FILE
if [ $? -ne 0 ]
then
	$ECHO " fail!"
	$ECHO "--> check $LOG_FILE for info"
	exit 69
else
	if [ "1" -eq $VCS ]
	then
		cat $VCS_PATH/$VCS_FILE > $SRC_PATH/dbdump/$PROJ_NAME.vcs
	fi
	t2=`date '+%s'`
	t=`expr $t2 - $t1`
	$ECHO " pass ($t sec.)"
fi

# preprocessor conditional compilation (see http://www.cppreference.com/preprocessor/preprocessor_if.html)
cd $SRC_PATH
activityDescr="(3/$STEPS) Collecting conditional compilation and macro definition directives"

$ECHO -n $activityDescr "..."
$ECHO $activityDescr >> $LOG_FILE
t1=`date '+%s'`
if [ $USE_FILES -eq 1 ]
then
	cat $LIST_PATH/$LIST_FILE | xargs perl $FETCH/scripts/parserExt/preprocDirectives.pl | sed "s/\.\///g" >> ./dbdump/$PROJ_NAME.condcomp
else
	allFiles=`find . \( -name "*.cpp" -o -name "*.c" -o -name "*.cc" -o -name "*.cxx" -o -name "*.hpp" -o -name "*.h" -o -name "*.hh" -o -name "*.hxx" \)`
	for file in $allFiles; do
		echo $file
		perl $FETCH/scripts/parserExt/preprocDirectives.pl "$file" | sed "s/\.\///g" >> ./dbdump/$PROJ_NAME.condcomp
	done
fi
t2=`date '+%s'`
t=`expr $t2 - $t1`
$ECHO " pass ($t sec.)"

# alternative includes
cd $SRC_PATH
activityDescr="(4/$STEPS) Collecting include directives"
$ECHO -n $activityDescr "..."
$ECHO $activityDescr >> $LOG_FILE
t1=`date '+%s'`
grep "#include" ./dbdump/$PROJ_NAME.condcomp > ./dbdump/$PROJ_NAME.includes2
t2=`date '+%s'`
t=`expr $t2 - $t1`
$ECHO " pass ($t sec.)"

if [ "0" -eq $CPP ]
then
	rm ./dbdump/$PROJ_NAME.condcomp
fi

activityDescr="(4/$STEPS) Collecting namespace declarations and uses"
$ECHO -n $activityDescr "..."
$ECHO $activityDescr >> $LOG_FILE
cd $SRC_PATH
t1=`date '+%s'`
perl $FETCH/scripts/parserExt/namespaceScript/getNamespaces.pl -s . c cc cpp cxx h hh hpp hxx > ./dbdump/$PROJ_NAME.namespaces 2>> $LOG_FILE
if [ $? -ne 0 ]
then
	$ECHO " fail!"
	$ECHO "--> check $LOG_FILE for info"
	exit 69
else
	t2=`date '+%s'`
	t=`expr $t2 - $t1`
	$ECHO " pass ($t sec.)"
fi

activityDescr="(5/$STEPS) Calculating metrics "
$ECHO $activityDescr >> $LOG_FILE
if [[ "1" -eq $PMCM ]]
then
	cd $SRC_PATH
	$ECHO -n $activityDescr "via pmccabe ..."

	t1=`date '+%s'`
	# pmccabe can't cope with method implementations inside a class declaration scope. so we don't parse headers (with possible implementations) for now.
	if [ $USE_FILES -eq 1 ]
	then
		cat $LIST_PATH/$LIST_FILE | xargs $PMC >> $SRC_PATH/dbdump/$PROJ_NAME.pmcmetrics 2>> $LOG_FILE
	else
		find . \( -name "*.cpp" -o -name "*.c" -o -name "*.cc" -o -name "*.cxx" \) | xargs $PMC >> $SRC_PATH/dbdump/$PROJ_NAME.pmcmetrics 2>> $LOG_FILE
	fi
	t2=`date '+%s'`
	t=`expr $t2 - $t1`
	$ECHO " pass ($t sec.)"
elif [[ "1" -eq $NCSSM ]]
then
	cd $SRC_PATH
	$ECHO -n $activityDescr "via cppncss ..."

	t1=`date '+%s'`
	$FETCH/src/cppncss/bin/cppncss -k -v -r . > $SRC_PATH/dbdump/$PROJ_NAME.ncssmetrics 2>> $LOG_FILE
	t2=`date '+%s'`
	t=`expr $t2 - $t1`
	$ECHO " pass ($t sec.)"
elif [[ "1" -eq $IEMETRICS ]]
then
	cd $SRC_PATH
	$ECHO -n $activityDescr "via iemetrics ..."
	
	t1=`date '+%s'`
	python $FETCH/src/IEMetrics/src/runOnDbdump.py $SRC_PATH $SRC_PATH/dbdump $PROJ_NAME 2>> $LOG_FILE
	t2=`date '+%s'`
	t=`expr $t2 - $t1`
	$ECHO " pass ($t sec.)"
else
	$ECHO " skipped"
fi

# get control structure information
$ECHO -n "(6/$STEPS) Grepping loop and conditionals ..."
if [ $USE_FILES -eq 1 ]
then
	$FETCH/scripts/parserExt/evoGenerateCtrlStructInfo.sh $SRC_PATH $PROJ_NAME "CCOND" --files=$LIST_PATH/$LIST_FILE
	$FETCH/scripts/parserExt/evoGenerateCtrlStructInfo.sh $SRC_PATH $PROJ_NAME "CLOOP" --files=$LIST_PATH/$LIST_FILE
else
	$FETCH/scripts/parserExt/evoGenerateCtrlStructInfo.sh $SRC_PATH $PROJ_NAME "CCOND"
	$FETCH/scripts/parserExt/evoGenerateCtrlStructInfo.sh $SRC_PATH $PROJ_NAME "CLOOP"
fi
t1=`date '+%s'`
if [ $? -ne 0 ]
then
	$ECHO " fail!"
	$ECHO "--> check $LOG_FILE for info"
	exit 69
else
	t2=`date '+%s'`
	t=`expr $t2 - $t1`
	$ECHO " pass ("$t "sec.)"
fi

# some cleanup, these files eat hard disks!
activityDescr="(7/$STEPS) Cleaning temporary files"
$ECHO -n $activityDescr "..."
$ECHO $activityDescr >> $LOG_FILE
t1=`date '+%s'`
rm -rf $SRC_PATH/$PROJ_PATH.proj $SRC_PATH/.snprj $SRC_PATH/dbdump/*.tmp
if [ $? -ne 0 ]
then
	$ECHO " fail!"
	exit 69
else
	t2=`date '+%s'`
	t=`expr $t2 - $t1`
	$ECHO " pass ($t sec.)"
fi

exit 0

