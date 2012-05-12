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
import shutil
import evo.common.globals.Globals

# global variables
backupCounter = 0

class SourceBackup:
    def __init__(self, options, codeFolder):
        self.options = options
        self.sourceFiles = {}
        self.codeFolder = codeFolder
        
    def getOptions(self):
        return self.options
        
    def getBackupFile(self, sourceFile):
        if sourceFile in self.sourceFiles:
            return self.sourceFiles[sourceFile]
        else:
            return ""
        
    def performBackup(self, transaction):     
        sourceExtensions = evo.common.globals.Globals.sourceExtensions
         
        revisions = transaction.getRevisions()        
        for revision in revisions.values():
            if not (revision.getPreviousRevision() is None):
                sourceFile = revision.getSourceFile()
                if sourceFile.getExtension() in sourceExtensions:
                    self.backupFile(revision.getSourceFile().getUniqueName())            
        
    def discardBackup(self):
        for backupFile in self.sourceFiles.values():
            os.remove(backupFile)
        self.sourceFiles.clear()
        
    def backupFile(self, sourceFile):
        global backupCounter
        backupFolder = self.options.getBackupFolder()
        backupCounter += 1
        backupFile = backupFolder + os.sep + str(backupCounter) + '.bak'
        fullFile = self.codeFolder + sourceFile
        shutil.copyfile(fullFile, backupFile)
        self.sourceFiles[sourceFile] = backupFile
