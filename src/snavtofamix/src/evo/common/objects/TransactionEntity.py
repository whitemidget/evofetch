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

class TransactionEntity:
    def __init__(self):
        self.cdifId = None
        self.transactionNumber = None
        self.name = None
        self.creationTime = None
        self.latestTime = None
        self.message = None
        self.author = None
        self.previousTransaction = None
        self.nextTransaction = None
        self.revisions = {}
        self.deletedRevisions = {}
        
    def __eq__(self, other):
        return other.getUniqueName() == self.getUniqueName()

    def getCdifId(self):
        return self.cdifId
    
    def setCdifId(self, cdifId):
        self.cdifId = cdifId
        
    def getTransactionNumber(self):
        return self.transactionNumber
    
    def setTransactionNumber(self, transactionNumber):
        self.transactionNumber = transactionNumber
        
    def getCreationTime(self):
        return self.creationTime
    
    def setCreationTime(self, creationTime):
        self.creationTime = creationTime

    def getLatestTime(self):
        return self.latestTime
    
    def setLatestTime(self, latestTime):
        self.latestTime = latestTime
        
    def getMessage(self):
        return self.message
    
    def setMessage(self, message):
        self.message = message
        
    def getAuthor(self):
        return self.author
    
    def setAuthor(self, author):
        self.author = author
        
    def getPreviousTransaction(self):
        return self.previousTransaction
    
    def setPreviousTransaction(self, previousTransaction):
        self.previousTransaction = previousTransaction
        
    def getNextTransaction(self):
        return self.nextTransaction
    
    def setNextTransaction(self, nextTransaction):
        self.nextTransaction = nextTransaction

    def getName(self):
        if self.name is None:
            return 'T' + str(self.transactionNumber)
        else:
            return self.name
        
    def setName(self, name):
        self.name = name
    
    def getUniqueName(self):
        return self.getName()
    
    def getRevisions(self):
        return self.revisions
    
    def getDeletedRevisions(self):
        return self.deletedRevisions
    
    def addRevision(self, revision):
        self.__setAttributesFromRevision(revision)
        revision.setTransaction(self)
        self.revisions[revision.getDbId()] = revision
        
    def addDeletedRevision(self, deletedRevision, deletingRevision):
        self.__setAttributesFromRevision(deletingRevision)
        deletedRevision.setDeletingTransaction(self)
        self.deletedRevisions[deletedRevision.getDbId()] = deletedRevision
        
    def hasRevisions(self):
        return (len(self.revisions) > 0)
    
    def hasDeletedRevisions(self):
        return (len(self.deletedRevisions) > 0)
        
    def __setAttributesFromRevision(self, revision):
        if self.creationTime == None:
            self.creationTime = revision.getCreationTime()
            self.author = revision.getAuthor()
            self.message = revision.getMessage()
        self.latestTime = revision.getCreationTime()
        
class TransactionListHolder:
    def __init__(self):
        self.transactionId = None
        self.transactionName = None
        self.revisions = []
        self.deletedRevisions = []
        
    def getTransactionId(self):
        return self.transactionId
    
    def setTransactionId(self, transactionId):
        self.transactionId = transactionId
        
    def getTransactionName(self):
        return self.transactionName
    
    def setTransactionName(self, transactionName):
        self.transactionName = transactionName
        
    def addRevision(self, revisionId):
        self.revisions.append(revisionId)
        
    def addDeletedRevision(self, deletedRevisionId):
        self.deletedRevisions.append(deletedRevisionId)
        