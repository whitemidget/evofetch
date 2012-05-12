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

from common.output.cdifWriter import writeBooleanField, writeRecordPrefix, writeRecordPrefixWithKnownId, \
                                     writeStringField, writeRecordPostfix

# output file
of = None
extractor = None

def getOutputHandle():
    return of

def setOutputHandle(handle):
    global of
    of = handle

def getExtractor():
    return extractor

def setExtractor(ext):
    global extractor
    extractor = ext

def generateFileEntityInfo():
    
    fileDict = extractor.getFilesDictionary()

    for fileEntity in fileDict.dictByUniqueName.values():

        writeRecordPrefixWithKnownId(of, "SourceFile", fileEntity.getCdifId())
        
        writeStringField(of, "name", fileEntity.getName())
        writeStringField(of, "creationTime", fileEntity.getCreationTime().isoformat())
        writeStringField(of, "uniqueName", fileEntity.getUniqueName())
        if fileEntity.getFullPath() == None:
            writeStringField(of, "fullPath", "")
        else:
            writeStringField(of, "fullPath", fileEntity.getFullPath())
            
        writeRecordPostfix(of)
        
def generateAuthorEntityInfo():
    
    authorDict = extractor.getAuthorDictionary()
    
    for authorEntity in authorDict.entityDict.values():
        
        writeRecordPrefixWithKnownId(of, "Author", authorEntity.getCdifId())
        
        writeStringField(of, "identifier", authorEntity.getIdentifier())
        writeStringField(of, "fullName", authorEntity.getFullName())
        if authorEntity.getEmailAddress() == None:
            writeStringField(of, "emailAddress", "")
        else:
            writeStringField(of, "emailAddress", authorEntity.getEmailAddress())
        
        writeRecordPostfix(of)

def generateRevisionEntityInfo():
    
    revisionDict = extractor.getRevisionDictionary()
    
    for revisionEntity in revisionDict.entityDict.values():
        
        if not revisionEntity.isDeletion():
        
            nextRevision = revisionEntity.getNextRevision()
            previousRevision = revisionEntity.getPreviousRevision()
            transaction = revisionEntity.getTransaction()
            deletingTransaction = revisionEntity.getDeletingTransaction()
        
            writeRecordPrefixWithKnownId(of, "Revision", revisionEntity.getCdifId())
            writeStringField(of, "name", revisionEntity.getName())
            writeStringField(of, "creationTime", revisionEntity.getCreationTime().isoformat())
            writeStringField(of, "uniqueName", revisionEntity.getUniqueName())
            writeStringField(of, "message", revisionEntity.getMessage())
            writeStringField(of, "revisionOf", revisionEntity.getSourceFile().getUniqueName())
            writeStringField(of, "author", revisionEntity.getAuthor().getIdentifier())
            if nextRevision is None:
                writeStringField(of, "nextRevision", "")
            else:
                writeStringField(of, "nextRevision", nextRevision.getUniqueName())
            if previousRevision is None:
                writeStringField(of, "previousRevision", "")
            else:
                writeStringField(of, "previousRevision", previousRevision.getUniqueName())
            writeStringField(of, "partOfTransaction", transaction.getUniqueName())
            if deletingTransaction is not None:
                writeStringField(of, "deletedByTransaction", deletingTransaction.getUniqueName())
            
            writeRecordPostfix(of)

def generateTransactionEntityInfo():
    
    transactionDict = extractor.getTransactionDictionary()
    
    for transactionEntity in transactionDict.dictByNumber.values():
        
        nextTransaction = transactionEntity.getNextTransaction()
        previousTransaction = transactionEntity.getPreviousTransaction()
        
        writeRecordPrefixWithKnownId(of, "Transaction", transactionEntity.getCdifId())
        writeStringField(of, "name", transactionEntity.getName())
        writeStringField(of, "uniqueName", transactionEntity.getUniqueName())
        writeStringField(of, "creationTime", transactionEntity.getCreationTime().isoformat())
        writeStringField(of, "latestTime", transactionEntity.getLatestTime().isoformat())
        writeStringField(of, "message", transactionEntity.getMessage())
        writeStringField(of, "author", transactionEntity.getAuthor().getIdentifier())
        if nextTransaction is None:
            writeStringField(of, "nextTransaction", "")
        else:
            writeStringField(of, "nextTransaction", nextTransaction.getUniqueName())
        if previousTransaction is None:
            writeStringField(of, "previousTransaction", "")
        else:
            writeStringField(of, "previousTransaction", previousTransaction.getUniqueName())
            
        writeRecordPostfix(of)

def generateSystemVersionEntityInfo():
    
    systemVersionDict = extractor.getSystemVersionDictionary()
    
    for systemVersionEntity in systemVersionDict.entityDict.values():
        
        writeRecordPrefixWithKnownId(of, "SystemVersion", systemVersionEntity.getCdifId())
        writeStringField(of, "transaction", systemVersionEntity.getTransaction().getUniqueName())
        writeStringField(of, "revision", systemVersionEntity.getRevision().getUniqueName())
        
        writeRecordPostfix(of)
        
def generateReleaseEntityInfo():
    
    releaseDict = extractor.getReleaseDictionary()
    
    for releaseEntity in releaseDict.entityDict.values():
        
        writeRecordPrefixWithKnownId(of, "Release", releaseEntity.getCdifId())
        writeStringField(of, "name", releaseEntity.getName())
        if releaseEntity.getCreationTime() == None:
            writeStringField(of, "creationTime", "")
        else:
            writeStringField(of, "creationTime", releaseEntity.getCreationTime().isoformat())
        writeStringField(of, "uniqueName", releaseEntity.getUniqueName())
        
        writeRecordPostfix(of)
        
def generateReleaseRevisionEntityInfo():
    
    releaseRevisionDict = extractor.getReleaseRevisionDictionary()
    
    for releaseRevisionEntity in releaseRevisionDict.entityDict.values():
        
        writeRecordPrefixWithKnownId(of, "ReleaseRevision", releaseRevisionEntity.getCdifId())
        writeStringField(of, "release", releaseRevisionEntity.getRelease().getUniqueName())
        writeStringField(of, "revision", releaseRevisionEntity.getRevision().getUniqueName())
        
        writeRecordPostfix(of)
        
def generateClassVersionEntityInfo(versionDict):
    
    for classVersionEntity in versionDict.values():
        
        writeRecordPrefix(of, "ClassVersion")
        writeStringField(of, "revision", classVersionEntity.getRevision())
        writeStringField(of, "versionOfClass", classVersionEntity.getClassName())
        writeBooleanField(of, "isCreation", classVersionEntity.isCreation())
        writeBooleanField(of, "isDeletion", classVersionEntity.isDeletion())
        writeBooleanField(of, "isModification", classVersionEntity.isModification())

        writeRecordPostfix(of)

def generateMethodVersionEntityInfo(versionDict):
    
    for methodVersionEntity in versionDict.values():
        
        writeRecordPrefix(of, "MethodVersion")
        writeStringField(of, "revision", methodVersionEntity.getRevision())
        writeStringField(of, "versionOfMethod", methodVersionEntity.getMethodName())
        writeBooleanField(of, "isCreation", methodVersionEntity.isCreation())
        writeBooleanField(of, "isDeletion", methodVersionEntity.isDeletion())
        writeBooleanField(of, "isModification", methodVersionEntity.isModification())

        writeRecordPostfix(of)

def generateFunctionVersionEntityInfo(versionDict):
    
    for functionVersionEntity in versionDict.values():
        
        writeRecordPrefix(of, "FunctionVersion")
        writeStringField(of, "revision", functionVersionEntity.getRevision())
        writeStringField(of, "versionOfFunction", functionVersionEntity.getFunctionName())
        writeBooleanField(of, "isCreation", functionVersionEntity.isCreation())
        writeBooleanField(of, "isDeletion", functionVersionEntity.isDeletion())
        writeBooleanField(of, "isModification", functionVersionEntity.isModification())

        writeRecordPostfix(of)

def generateAttributeVersionEntityInfo(versionDict):
    
    for attributeVersionEntity in versionDict.values():
        
        writeRecordPrefix(of, "AttributeVersion")
        writeStringField(of, "revision", attributeVersionEntity.getRevision())
        writeStringField(of, "versionOfAttribute", attributeVersionEntity.getAttributeName())
        writeBooleanField(of, "isCreation", attributeVersionEntity.isCreation())
        writeBooleanField(of, "isDeletion", attributeVersionEntity.isDeletion())
        writeBooleanField(of, "isModification", attributeVersionEntity.isModification())

        writeRecordPostfix(of)

def generateGlobalVariableVersionEntityInfo(versionDict):
    
    for globalVarVersionEntity in versionDict.values():
        
        writeRecordPrefix(of, "GlobalVariableVersion")
        writeStringField(of, "revision", globalVarVersionEntity.getRevision())
        writeStringField(of, "versionOfGlobalVariable", globalVarVersionEntity.getGlobalVariableName())
        writeBooleanField(of, "isCreation", globalVarVersionEntity.isCreation())
        writeBooleanField(of, "isDeletion", globalVarVersionEntity.isDeletion())
        writeBooleanField(of, "isModification", globalVarVersionEntity.isModification())

        writeRecordPostfix(of)


                