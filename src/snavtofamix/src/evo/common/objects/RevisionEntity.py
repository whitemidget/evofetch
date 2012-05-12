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

class RevisionEntity:
    def __init__(self):
        self.cdifId = None
        self.dbId = None
        self.fileDbId = None
        self.commitId = None
        self.name = None
        self.message = None
        self.creationTime = None
        self.author = None
        self.sourceFile = None
        self.transaction = None
        self.deletingTransaction = None
        self.deletion = False
        self.sourceFileUniqueName = None
        self.previousRevisionId = None
        self.nextRevisionId = None
        
    def __eq__(self, other):
        return other.getUniqueName() == self.getUniqueName()

    def getCdifId(self):
        return self.cdifId
    
    def setCdifId(self, cdifId):
        self.cdifId = cdifId
        
    def getDbId(self):
        return self.dbId
    
    def setDbId(self, dbId):
        self.dbId = dbId
        
    def getFileDbId(self):
        return self.fileDbId
    
    def setFileDbId(self, fileDbId):
        self.fileDbId = fileDbId
        
    def getCommitId(self):
        return self.commitId
    
    def setCommitId(self, commitId):
        self.commitId = commitId
        
    def getName(self):
        return self.name
    
    def setName(self, name):
        self.name = name
        
    def getMessage(self):
        return self.message
    
    def setMessage(self, message):
        self.message = message
        
    def getCreationTime(self):
        return self.creationTime
    
    def setCreationTime(self, creationTime):
        self.creationTime = creationTime
        
    def getAuthor(self):
        return self.author
    
    def setAuthor(self, author):
        self.author = author
        
    def getSourceFile(self):
        return self.sourceFile
    
    def setSourceFile(self, sourceFile):
        self.sourceFile = sourceFile
       
    def getTransaction(self):
        return self.transaction
    
    def setTransaction(self, transaction):
        self.transaction = transaction
        
    def getDeletingTransaction(self):
        return self.deletingTransaction
    
    def setDeletingTransaction(self, deletingTransaction):
        self.deletingTransaction = deletingTransaction
        
    def isDeletion(self):
        return self.deletion
    
    def setDeletion(self, deletion):
        self.deletion = deletion
        
    def getUniqueName(self):
        return self.name
        
    def getNextRevision(self):
        if self.sourceFile is None:
            return None
        else:
            return self.sourceFile.getNextRevision(self)
        
    def getPreviousRevision(self):
        if self.sourceFile is None:
            return None
        else:
            return self.sourceFile.getPreviousRevision(self)
        
    def getSourceFileUniqueName(self):
        if self.sourceFile is None:
            return self.sourceFileUniqueName
        else:
            return self.sourceFile.getUniqueName()
    
    def setSourceFileUniqueName(self, sourceFileUniqueName):
        if self.sourceFile is None:
            self.sourceFileUniqueName = sourceFileUniqueName
        
    def getNextRevisionId(self):
        if self.getNextRevision() is None:
            return self.nextRevisionId
        else:
            return self.getNextRevision().getUniqueName()
    
    def setNextRevisionId(self, nextRevisionId):
        self.nextRevisionId = nextRevisionId
        
    def getPreviousRevisionId(self):
        if self.getPreviousRevision() is None:
            return self.previousRevisionId
        else:
            return self.getPreviousRevision().getUniqueName()
    
    def setPreviousRevisionId(self, previousRevisionId):
        self.previousRevisionId = previousRevisionId

class CommitEntity:
    def __init__(self):
        self.dbId = None
        self.name = None
        self.message = None
        self.creationTime = None
        self.authorDbId = None
        self.transaction = None
        self.actions = {}

    def getDbId(self):
        return self.dbId
    
    def setDbId(self, dbId):
        self.dbId = dbId
        
    def getName(self):
        return self.name
    
    def setName(self, name):
        self.name = name
        
    def getMessage(self):
        return self.message
    
    def setMessage(self, message):
        self.message = message
        
    def getCreationTime(self):
        return self.creationTime
    
    def setCreationTime(self, creationTime):
        self.creationTime = creationTime
        
    def getAuthorDbId(self):
        return self.authorDbId
    
    def setAuthorDbId(self, authorDbId):
        self.authorDbId = authorDbId
        
    def getTransaction(self):
        return self.transaction
    
    def setTransaction(self, transaction):
        self.transaction = transaction
        
    def getActions(self):
        return self.actions
    
    def addAction(self, action):
        self.actions[action.getDbId()] = action

class ActionEntity:
    def __init__(self):
        self.dbId = None
        self.fileId = None
        self.commitId = None
        self.deletion = False
        self.revision = None
        
    def getDbId(self):
        return self.dbId
    
    def setDbId(self, dbId):
        self.dbId = dbId

    def getFileId(self):
        return self.fileId
    
    def setFileId(self, fileId):
        self.fileId = fileId
        
    def getCommitId(self):
        return self.commitId
    
    def setCommitId(self, commitId):
        self.commitId = commitId
        
    def isDeletion(self):
        return self.deletion
    
    def setDeletion(self, deletion):
        self.deletion = deletion
        
    def getRevision(self):
        return self.revision
    
    def setRevision(self, revision):
        self.revision = revision
