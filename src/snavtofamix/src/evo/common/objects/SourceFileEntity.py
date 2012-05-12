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

class SourceFileEntity:
    def __init__(self):
        self.cdifId = None
        self.dbId = None
        self.name = None
        self.creationTime = None
        self.creationCommitId = None
        self.fullPath = None
        self.revisions = {}
        self.revisionList = None
        self.cloned = False
               
    def __eq__(self, other):
        return other.getUniqueName() == self.getUniqueName()
    
    def clone(self):
        anotherFile = SourceFileEntity()
        anotherFile.dbId = self.dbId
        anotherFile.name = self.name
        self.cloned = True
        anotherFile.cloned = True
        return anotherFile
    
    def getCdifId(self):
        return self.cdifId
    
    def setCdifId(self, cdifId):
        self.cdifId = cdifId
    
    def getDbId(self):
        return self.dbId
    
    def setDbId(self, dbId):
        self.dbId = dbId
    
    def getName(self):
        return self.name    

    def setName(self, name):
        self.name = name
        
    def getCreationTime(self):
        return self.creationTime
    
    def setCreationTime(self, creationTime):
        self.creationTime = creationTime
        
    def getCreationCommitId(self):
        return self.creationCommitId
    
    def setCreationCommitId(self, creationCommitId):
        self.creationCommitId = creationCommitId
        
    def getUniqueName(self):
        if self.fullPath == None:
            return '/' + self.name
        else:
            return self.fullPath + '/' + self.name
        
    def setUniqueName(self, uniqueName):
        parts = uniqueName.split('/')
        self.name = parts[-1]
        self.fullPath = None
        for part in parts[-2::-1]:
            if len(part) > 0:
                self.addParent(part)
    
    def getFullPath(self):
        return self.fullPath

    def setFullPath(self, fullPath):
        self.fullPath = fullPath
        
    # only used in cdif2rsf: returns full path + filename without root "/" character
    def getPath(self):
        return self.getUniqueName()[1:]
        
    def addParent(self, parent):
        if self.fullPath == None:
            self.fullPath = '/' + parent
        else:
            self.fullPath = '/' + parent + self.fullPath
        
    def addRevision(self, revision):
        self.revisions[revision.getDbId()] = revision
        
    def getNextRevision(self, revision):
        if not (revision.getDeletingTransaction() is None):
            return None
        if self.revisionList == None:
            self.revisionList = sorted(self.revisions.keys())
        i = self.revisionList.index(revision.getDbId())
        if i >= 0 and i < len(self.revisionList) - 1:
            return self.revisions[self.revisionList[i + 1]]
        else:
            return None            
        
    def getPreviousRevision(self, revision):
        if self.revisionList == None:
            self.revisionList = sorted(self.revisions.keys())
        i = self.revisionList.index(revision.getDbId())
        if i > 0:
            previousRevision = self.revisions[self.revisionList[i - 1]]
            if previousRevision.getDeletingTransaction() is None:
                return previousRevision
            else:
                return None
        else:
            return None
        
    def getFirstRevision(self):
        if self.revisionList == None:
            self.revisionList = sorted(self.revisions.keys())
        if len(self.revisionList) > 0:
            return self.revisions[self.revisionList[0]]
        else:
            return None
        
    def getLastRevision(self):
        if self.revisionList == None:
            self.revisionList = sorted(self.revisions.keys())
        if len(self.revisionList) > 0:
            return self.revisions[self.revisionList[len(self.revisionList) - 1]]
        else:
            return None
        
    def getRevisionPriorTo(self, revision):
        result = self.getLastRevision()
        while (not (result is None)) and result.getCreationTime() > revision.getCreationTime():
            result = self.getPreviousRevision(result)
        return result
    
    def getLastRevisionPriorToCommit(self, commitId):
        result = self.getLastRevision()
        while (not (result is None)) and result.getCommitId() > commitId:
            result = self.getPreviousRevision(result)
        return result
        
    def getExtension(self):
        return self.name.split('.').pop()
        
class FileLinksEntity:
    def __init__(self):
        self.fileId = None
        self.parentId = None
        self.commitId = None
        
    def getFileId(self):
        return self.fileId
    
    def setFileId(self, fileId):
        self.fileId = fileId
        
    def getParentId(self):
        return self.parentId
    
    def setParentId(self, parentId):
        self.parentId = parentId
        
    def getCommitId(self):
        return self.commitId
    
    def setCommitId(self, commitId):
        self.commitId = commitId

        