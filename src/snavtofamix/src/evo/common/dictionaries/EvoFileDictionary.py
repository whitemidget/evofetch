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

from common.dictionaries.FileDictionary import FileDictionary

from common.output.cdifWriter import requestNewCdifId

class EvoFileDictionary(FileDictionary):
    def __init__(self):
        FileDictionary.__init__(self)
        self.fileRevisionDict = {}
        
    def getFileList(self):
        return self.fileRevisionDict.keys()
    
    def getRevisionForFile(self, sourceFile):
        if sourceFile in self.fileRevisionDict:
            return self.fileRevisionDict[sourceFile]
        else:
            return ""
    
    def add(self, fileEntity):
        filePath = '/' + fileEntity.getPath()
        if filePath in self.fileRevisionDict: 
            if not fileEntity in self.entityDict.values():
                fileEntity.setCdifId(requestNewCdifId())
                self.entityDict[fileEntity.getCdifId()] = fileEntity
                return True
        
        return False
    
    def restrictToTransaction(self, transaction):
        
        self.fileRevisionDict = {}
        revisions = transaction.getRevisions()
        
        for revision in revisions.values():
            sourceFile = revision.getSourceFile()
            fileName = sourceFile.getUniqueName()
            self.fileRevisionDict[fileName] = revision.getUniqueName()
        
    def getInterestedFields(self):
        return ('sourceAnchor',)
            
    def decorateWriterOutput(self, output):
        strings = output.split('"')
        if len(strings) == 3:
            fileName = '/' + strings[1]
            if fileName in self.fileRevisionDict:
                revisionName = self.fileRevisionDict[fileName]
                output = output + '\n\t(revision "' + revisionName + '")'
        return output
            
