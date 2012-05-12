# Copyright (C) 2011 James Goodger
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors :
#       James Goodger <james@evofetch.org>

import os
import re
import sys

from os import EX_OK, EX_USAGE

from log4py import Logger, LOGLEVEL_DEBUG
from shared import addLogTarget, setLogFileName

from common.infrastructure.Timing import Timer

def getRelationsFromQuery(queryFile):
    
    queryFile = open(queryFile, 'r')
    
    relationList = []
    
    for line in queryFile:
        line = line.strip()
        
        pattern = "[a-zA-Z]*\([^\(\)]*\)"
        relationMatches = re.findall(pattern, line)
        for match in relationMatches:
            relation = match.split("(")[0].strip()
            if relation != "" and (not (relation in relationList)):
                relationList.append(relation)
                
    queryFile.close()
    
    return relationList    

def optimiseRsf(queryFile, inputFile, optimisedFile):
    
    relations = getRelationsFromQuery(queryFile)
    
    lastTransaction = ("LatestSystemVersion" in relations)
    lastTransactionId = None
    firstTransaction = ("EarliestSystemVersion" in relations)
    firstTransactionId = None
    
    inputFile = open(inputFile, 'r')
    optimisedFile = open(optimisedFile, 'w')
    
    for line in inputFile:
        columns = line.split("\t")
        if len(columns) > 0:
            relation = columns[0].strip()
            if relation in relations:
                if lastTransaction and relation == "LatestSystemVersion":
                    lastTransactionId = columns[1].strip()
                if firstTransaction and relation == "EarliestSystemVersion":
                    lastTransactionId = columns[1].strip()
                if relation == "ProducesRevision":
                    transactionId = columns[1].strip()
                    if firstTransaction or lastTransaction:
                        if lastTransaction and transactionId == lastTransactionId:
                            optimisedFile.write(line)
                        elif firstTransaction and transactionId == firstTransactionId:
                            optimisedFile.write(line)
                    else:
                        optimisedFile.write(line)
                else:
                    optimisedFile.write(line)
    
    optimisedFile.close()
    inputFile.close()
    
    return EX_OK
    
def runQuery(queryFile, optimisedFile, memory):
    
    crocoPath = os.getenv("CROCO")
    cmd = crocoPath + " -m %d %s < %s" % (memory, queryFile, optimisedFile)
    
    return os.system(cmd)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage:",sys.argv[0],"queryFileName rsfInputFile [optimisedFile] [options]"
        print "\tqueryFileName -- name of the RML query file"
        print "\trsfInputFile  -- name of the RSF file containing the relations for the query"
        print "\toptimisedFile -- an optional RSF file name to hold an optimised set of relations"
        print "\t[options]:"
        print "\t\t --logfile\tuse given logfile as a log file"
        print "\t\t --memory NUMBER\tapproximate memory for Crocopat's BDD package in MB (default 50)"
        print ""
        print "The following environment variables must also be set:"
        print ""
        print "CROCO    Refers to the CrocoPat binary in the fetch/bin folder that suits"
        print "         your platform"
        sys.exit(EX_USAGE)
        
    logFileName = None
    memorySize = 50
    optimisedFile = None
    
    crocoPath = os.getenv("CROCO")
    if crocoPath is None:
        print "The CROCO environment variable is not set"
        print "This variable should be set to the name of the CrocoPat binary in the"
        print "fetch/bin folder that suits your platform"
        sys.exit(EX_USAGE)
            
    if len(sys.argv) > 3:
        args = sys.argv[3:]
        firstArg = True
        nextLog = False
        nextMemory = False
        
        for arg in args:
            if nextLog:
                logFileName = arg
                nextLog = False
            elif nextMemory:
                memorySize = int(arg)
                nextMemory = False
            elif arg == "--logfile":
                nextLog = True
            elif arg == "--memory":
                nextMemory = True
            elif firstArg:
                optimisedFile = arg
            firstArg = False
        
    log = Logger().get_instance()
    
    if logFileName != None:
        logDirName = os.path.dirname(logFileName)
        if os.path.exists(logDirName):
            print "Setting logfile to " + logFileName
            setLogFileName(logFileName)
        else:
            print "Logging directory \"" + logDirName + "\" does not exist."
            sys.exit(0)

    addLogTarget(log)
    log.set_loglevel(LOGLEVEL_DEBUG)
    
    queryFile = sys.argv[1]
    inputFile = sys.argv[2]
    if not (optimisedFile is None):
        log.info("Optimising RSF")
        timer = Timer("Optimising RSF")
        timer.start()
        exitCode = optimiseRsf(queryFile, inputFile, optimisedFile)
        timer.stop()
        timer.log(1)
        if exitCode != EX_OK:
            sys.exit(exitCode)
        rsfFile = optimisedFile
    else:
        rsfFile = inputFile
        
    log.info("Running Query")
    timer = Timer("Running Query")
    timer.start()
    exitCode = runQuery(queryFile, rsfFile, memorySize)
    timer.stop()
    timer.log(1)
    
    if exitCode != EX_OK:
        sys.exit(exitCode)
        
    sys.exit(EX_OK)

