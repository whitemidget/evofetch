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

class RestrictedByFile:
    def __init__(self, fileDict):
        self.fileDict = fileDict
        self.restricting = True
        
    def getFileDict(self):
        return self.fileDict
    
    def setFileDict(self, fileDict):
        self.fileDict = fileDict
        
    def isRestricting(self):
        return self.restricting
    
    def setRestricting(self, restricting):
        self.restricting = restricting
        
    def isFilePermitted(self, sourceFile):
        if (not self.restricting) or self.fileDict is None:
            return True
        else:
            fileList = self.fileDict.getFileList()
            lookForFile = '/' + sourceFile;
            if lookForFile in fileList:
                return True
            else:
                return False
            
    def containsPermittedFile(self, sourceFileList):
        permitted = False
        for sourceFile in sourceFileList:
            if self.isFilePermitted(sourceFile):
                permitted = True
                break
        return permitted        
            
