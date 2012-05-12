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

from os import EX_OK

from datetime import datetime

from evo.cdif2rsf.writeTransactions import importTransactions
from evo.common.dictionaries.RevisionDict import RevisionDictionary
from evo.common.objects.RevisionEntity import RevisionEntity
from evo.common.objects.TransactionEntity import TransactionListHolder
from evo.common.processing.Utils import convertTimeToUNIX, setRSFCounter
from common.output.cdifWriter import requestNewCdifId

def buildRevisionDict(cdifFile, revisionDict, control):
    
    """ Reads revisions from a CDIF file into a dictionary """
    for line in cdifFile:
        line = line.strip()
        
        # if the line is the start of an entity
        if line.startswith("(Revision FM"):
            revisionEntity = RevisionEntity()
            
            revisionEntity.setCdifId(int(line.split("M")[1]))
            setRSFCounter(revisionEntity.getCdifId())
            
            for line in cdifFile:
                line = line.strip()
                if line.startswith("(name "):
                    revisionEntity.setName(line.split("\"")[1])
                elif line.startswith("(creationTime "):
                    timeString = line.split("\"")[1]
                    revisionEntity.setCreationTime(datetime.strptime(timeString, '%Y-%m-%dT%H:%M:%S'))
                elif line.startswith("(revisionOf "):
                    revisionEntity.setSourceFileUniqueName(line.split("\"")[1])
                elif line.startswith("(author "):
                    revisionEntity.setAuthor(line.split("\"")[1])
                elif line.startswith("(nextRevision "):
                    revisionId = line.split("\"")[1]
                    if revisionId != "": 
                        revisionEntity.setNextRevisionId(revisionId)
                elif line.startswith("(previousRevision "):
                    revisionId = line.split("\"")[1]
                    if revisionId != "": 
                        revisionEntity.setPreviousRevisionId(revisionId)
                elif line.startswith("(partOfTransaction "):
                    revisionEntity.setTransaction(line.split("\"")[1])
                elif line.startswith("(deletedByTransaction "):
                    revisionEntity.setDeletingTransaction(line.split("\"")[1])
                elif line == ")":
                    if control.isTimeValid(revisionEntity.getCreationTime()):
                        revisionDict.addPrepared(revisionEntity)
                    break    

def importAuthors(authorDict):

    importAuthorFile = open("authorsWithIDs.txt", 'r')
 
    for line in importAuthorFile:
        line = line.strip()
        lineSplittedInTabs = line.split("\t")
        authorId = int(lineSplittedInTabs[0])
        authorIdentifier = lineSplittedInTabs[1].split("\"")[1]
   
        if not (authorIdentifier in authorDict):
            authorDict[authorIdentifier] = authorId
    
    importAuthorFile.close()
    
def importFiles(fileDict):

    importFileFile = open("filesWithIDs.txt", 'r')
    
    for line in importFileFile:
        line = line.strip()
        lineSplittedInTabs = line.split("\t")
        fileId = int(lineSplittedInTabs[0])
        fileUniqueName = lineSplittedInTabs[1].split("\"")[1]
   
        if not (fileUniqueName in fileDict):
            fileDict[fileUniqueName] = fileId
    
    importFileFile.close()

def addRevisionEntity(revisionEntity, revisionOfFile, revisionBelongsToAuthor, \
                      artefactNext, artefactPrevious, revisionBelongsToTransaction, \
                      revisionDeletedByTransaction, revisionDict, authors, files, \
                      transactions):
    
    revisionId = revisionEntity.getCdifId()
    sourceFileName = revisionEntity.getSourceFileUniqueName()
    authorIdentifier = revisionEntity.getAuthor()
    nextRevision = revisionEntity.getNextRevisionId()
    previousRevision = revisionEntity.getPreviousRevisionId()
    partOfTransaction = revisionEntity.getTransaction()
    deletingTransaction = revisionEntity.getDeletingTransaction()

    revisionOfFile[revisionId] = files[sourceFileName]
    revisionBelongsToAuthor[revisionId] = authors[authorIdentifier]
    if not (nextRevision is None) and (nextRevision in revisionDict.dictByName):
        nextRevisionEntity = revisionDict.dictByName[nextRevision]
        artefactNext[revisionId] = nextRevisionEntity.getCdifId()
    if not (previousRevision is None):
        previousRevisionEntity = revisionDict.dictByName[previousRevision]
        artefactPrevious[revisionId] = previousRevisionEntity.getCdifId()
    revisionBelongsToTransaction[revisionId] = transactions[partOfTransaction]
    if (not (deletingTransaction is None)) and (deletingTransaction in transactions): 
        revisionDeletedByTransaction[revisionId] = transactions[deletingTransaction]
        
def writeRevisions(inputFile, control):
    # initialise IDCounter to 1
    requestNewCdifId()

    inputFile = open(inputFile, 'r')
    revisionDict = RevisionDictionary()
    buildRevisionDict(inputFile, revisionDict, control)
    inputFile.close()
    
    revisionsFile = open("revisionsWithIDs.txt", 'w')
    timeFile = open("artefactTime.txt", 'a')
    nextFile = open("artefactNext.txt", 'a')
    previousFile = open("artefactPrevious.txt", 'a')
    fileFile = open("revisionOfFile.txt", 'w')
    authorFile = open("revisionBelongsToAuthor.txt", 'w')
    changesFile = open("revisionBelongsToTransaction.txt", 'w')
    deletesFile = open("revisionDeletedByTransaction.txt", 'w')
        
    # first build up the relations
    revisionOfFile = {}
    revisionBelongsToAuthor = {}
    artefactNext = {}
    artefactPrevious = {}
    revisionBelongsToTransaction = {}
    revisionDeletedByTransaction = {}
    
    authors = {}
    files = {}
    transactions = {}

    importAuthors(authors)  
    importFiles(files)  
    importTransactions(transactions, False)
        
    for revisionEntity in revisionDict.entityDict.values():
        addRevisionEntity(revisionEntity, revisionOfFile, revisionBelongsToAuthor, \
                          artefactNext, artefactPrevious, revisionBelongsToTransaction, \
                          revisionDeletedByTransaction, revisionDict, authors, files, \
                          transactions)
        revisionId = revisionEntity.getCdifId()
        revisionIdentifier = revisionEntity.getUniqueName()
        revisionInfo = str(revisionId) + "\t\"" + revisionIdentifier + "\"\n";
        revisionsFile.write(revisionInfo)
        revisionTime = convertTimeToUNIX(revisionEntity.getCreationTime())
        timeInfo = str(revisionId) + "\t\"" + str(revisionTime) + "\"\n";
        timeFile.write(timeInfo)
    revisionsFile.close()
    timeFile.close()
    
    indices = revisionOfFile.keys()
    indices.sort()
    for revisionId in indices:
        fileId = revisionOfFile[revisionId]
        revisionOfFileInfo = str(revisionId) + "\t" + str(fileId) + "\n"
        fileFile.write(revisionOfFileInfo)
    fileFile.close()
    
    indices = revisionBelongsToAuthor.keys()
    indices.sort()
    for revisionId in indices:
        authorId = revisionBelongsToAuthor[revisionId]
        revisionBelongsToAuthorInfo = str(revisionId) + "\t" + str(authorId) + "\n"
        authorFile.write(revisionBelongsToAuthorInfo)
    authorFile.close()
    
    indices = artefactNext.keys()
    indices.sort()
    for revisionId in indices:
        nextId = artefactNext[revisionId]
        nextInfo = str(revisionId) + "\t" + str(nextId) + "\n"
        nextFile.write(nextInfo)
    nextFile.close()
    
    indices = artefactPrevious.keys()
    indices.sort()
    for revisionId in indices:
        previousId = artefactPrevious[revisionId]
        previousInfo = str(revisionId) + "\t" + str(previousId) + "\n"
        previousFile.write(previousInfo)
    previousFile.close()
        
    indices = revisionBelongsToTransaction.keys()
    indices.sort()
    for revisionId in indices:
        transactionId = revisionBelongsToTransaction[revisionId]
        revisionBelongsToTransactionInfo = str(revisionId) + "\t" + str(transactionId) + "\n"
        changesFile.write(revisionBelongsToTransactionInfo)
    changesFile.close()
        
    indices = revisionDeletedByTransaction.keys()
    indices.sort()
    for revisionId in indices:
        transactionId = revisionDeletedByTransaction[revisionId]
        revisionDeletedByTransactionInfo = str(revisionId) + "\t" + str(transactionId) + "\n"
        deletesFile.write(revisionDeletedByTransactionInfo)
    deletesFile.close()
        
    return EX_OK

def importRevisions(revisionDict):

    importRevisionsFile = open("revisionsWithIDs.txt", 'r')
    
    for line in importRevisionsFile:
        line = line.strip()
        lineSplittedInTabs = line.split("\t")
        revisionId = int(lineSplittedInTabs[0])
        revisionUniqueName = lineSplittedInTabs[1].split("\"")[1]
   
        if not (revisionUniqueName in revisionDict):
            revisionDict[revisionUniqueName] = revisionId
    
    importRevisionsFile.close()

def importRevisionsByTransaction(transactionDict):
    
    for transactionId in transactionDict:
        transactionName = transactionDict[transactionId]
        transaction = TransactionListHolder()
        transaction.setTransactionId(transactionId)
        transaction.setTransactionName(transactionName)
        transactionDict[transactionId] = transaction
    
    importRevisionsFile = open("revisionBelongsToTransaction.txt", 'r')
    
    for line in importRevisionsFile:
        line = line.strip()
        lineSplittedInTabs = line.split("\t")
        revisionId = int(lineSplittedInTabs[0])
        transactionId = int(lineSplittedInTabs[1])
        transaction = transactionDict[transactionId]
        transaction.addRevision(revisionId)
        
    importRevisionsFile.close()
    
    importDeletedRevisionsFile = open("revisionDeletedByTransaction.txt", 'r')
    
    for line in importDeletedRevisionsFile:
        line = line.strip()
        lineSplittedInTabs = line.split("\t")
        deletedRevisionId = int(lineSplittedInTabs[0])
        transactionId = int(lineSplittedInTabs[1])
        transaction = transactionDict[transactionId]
        transaction.addDeletedRevision(deletedRevisionId)
        
    importDeletedRevisionsFile.close()
    
def importRevisionsOfFiles(revisionDict):

    importRevisionsFile = open("revisionOfFile.txt", 'r')
    
    for line in importRevisionsFile:
        line = line.strip()
        lineSplittedInTabs = line.split("\t")
        revisionId = int(lineSplittedInTabs[0])
        fileId = lineSplittedInTabs[1]
   
        if not (revisionId in revisionDict):
            revisionDict[revisionId] = fileId
    
    importRevisionsFile.close()

