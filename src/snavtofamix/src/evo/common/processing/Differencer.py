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

from evo.scope.LineChecker import LineChecker
from evo.scope.Scope import Scope

def performLDiff(backup, oldLocation, newLocation):
    workFolder = backup.getOptions().getWorkFolder()
    oldFile = workFolder + os.sep + 'entity.old' 
    newFile = workFolder + os.sep + 'entity.new'
    diffFile = workFolder + os.sep + 'entity.diff'
    oldSource = backup.getBackupFile('/' + oldLocation.getSourceFile())
    newSource = workFolder + '/' + newLocation.getSourceFile()
    extractEntity(oldSource, int(oldLocation.getStart()), oldFile)
    extractEntity(newSource, int(newLocation.getStart()), newFile)
    
    ldiffPath = os.getenv("LDIFF")
    ldiffCmd = ldiffPath + os.sep + "ldiff.pl -o ext %s %s > %s" % (oldFile, newFile, diffFile)
    
    os.system(ldiffCmd)
    os.remove(oldFile)
    os.remove(newFile)
    
    changed = False
    
    for line in open(diffFile, "r"):
        parts = line.split(',')
        if len(parts) > 1:
            difference = parts[1]
            if re.search("[0-9]*[cad][0-9]*", difference):
                changed = True
                break
            
    return changed
        
def extractEntity(sourceFile, start, destinationFile):
    
    entity = ""
    scope = Scope()
    scope.clear()
    lineChecker = LineChecker(scope)
    
    outputHandle = open(destinationFile, "w")
    outputHandle.close()
    outputHandle = open(destinationFile, "a+")
    lineNo = 0
    
    for line in open(sourceFile, "r"):
        lineNo += 1
        if lineNo >= start:
            entityCode = lineChecker.check(line)
            codeWithoutWhiteSpace = entityCode.strip() 
            if not codeWithoutWhiteSpace:
                codeWithoutWhiteSpace = ""
            else:
                if scope.outOfScope():
                    codeParts = codeWithoutWhiteSpace.split("}")
                    codeWithoutWhiteSpace = "}".join(codeParts[0:len(codeParts)-1])
            if codeWithoutWhiteSpace.strip():
                entity += codeWithoutWhiteSpace + "\n"
            if scope.entered() and scope.outOfScope():
                break
    
    outputHandle.write(entity)        
    outputHandle.close()
     
    