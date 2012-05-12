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

from evo.common.dictionaries.TransactionDict import TransactionDictionary
from evo.common.objects.TransactionEntity import TransactionEntity
from evo.common.processing.Utils import convertTimeToUNIX, setRSFCounter
from common.output.cdifWriter import requestNewCdifId

def buildTransactionDict(cdifFile, transactionDict, control):
    
    """ Reads transactions from a CDIF file into a dictionary """
    transactionCount = 0
    
    for line in cdifFile:
        line = line.strip()
        
        # if the line is the start of an entity
        if line.startswith("(Transaction FM"):
            transactionEntity = TransactionEntity()
            
            transactionEntity.setCdifId(line.split("M")[1])
            setRSFCounter(transactionEntity.getCdifId())
            
            for line in cdifFile:
                line = line.strip()
                if line.startswith("(uniqueName "):
                    transactionCode = line.split("\"")[1]
                    if transactionCode.startswith("T"):
                        transactionEntity.setTransactionNumber(int(transactionCode[1:]))
                    else:
                        transactionEntity.setName(transactionCode)
                elif line.startswith("(creationTime "):
                    timeString = line.split("\"")[1]
                    transactionEntity.setCreationTime(datetime.strptime(timeString, '%Y-%m-%dT%H:%M:%S'))
                elif line.startswith("(latestTime "):
                    timeString = line.split("\"")[1]
                    transactionEntity.setLatestTime(datetime.strptime(timeString, '%Y-%m-%dT%H:%M:%S'))
                elif line.startswith("(author "):
                    transactionEntity.setAuthor(line.split("\"")[1])
                elif line.startswith("(nextTransaction "):
                    transactionId = line.split("\"")[1]
                    if transactionId != "": 
                        transactionEntity.setNextTransaction(transactionId)
                elif line.startswith("(previousTransaction "):
                    transactionId = line.split("\"")[1]
                    if transactionId != "": 
                        transactionEntity.setPreviousTransaction(transactionId)
                elif line == ")":
                    transactionCount += 1
                    transactionDict.addPreBuiltEntity(transactionEntity)
                    control.setLatestTime(transactionEntity.getLatestTime())
                    control.addAuthor(transactionEntity.getAuthor())
                    break    

            if control.isLimiting() and transactionCount == control.getMaxTransactions():
                break

def addTransactionEntity(transactionEntity, transactionBelongsToAuthor, \
                         artefactNext, artefactPrevious, transactionDict, authors):
    
    transactionId = transactionEntity.getCdifId()
    authorIdentifier = transactionEntity.getAuthor()
    nextTransaction = transactionEntity.getNextTransaction()
    previousTransaction = transactionEntity.getPreviousTransaction()

    transactionBelongsToAuthor[transactionId] = authors[authorIdentifier]
    if not (nextTransaction is None) and (nextTransaction in transactionDict.dictByName):
        nextTransactionEntity = transactionDict.getEntityByName(nextTransaction)
        artefactNext[transactionId] = nextTransactionEntity.getCdifId()
    if not (previousTransaction is None):
        previousTransactionEntity = transactionDict.getEntityByName(previousTransaction)
        artefactPrevious[transactionId] = previousTransactionEntity.getCdifId()
        
def writeTransactions(inputFile, control):
    # initialise IDCounter to 1
    requestNewCdifId()

    inputFile = open(inputFile, 'r')
    transactionDict = TransactionDictionary()
    buildTransactionDict(inputFile, transactionDict, control)
    inputFile.close()
    
    transactionsFile = open("transactionsWithIDs.txt", 'w')
    timeFile = open("artefactTime.txt", 'a')
    latestTimeFile = open("transactionLatesttime.txt", 'w')
    nextFile = open("artefactNext.txt", 'a')
    previousFile = open("artefactPrevious.txt", 'a')
    authorFile = open("transactionBelongsToAuthor.txt", 'w')
        
    # first build up the relations
    transactionBelongsToAuthor = {}
    artefactNext = {}
    artefactPrevious = {}
    
    authors = {}
    
    # build files dictionary
    authorsFile = open("authorsWithIDs.txt", 'r')
    
    for line in authorsFile:
        line = line.strip()
        lineSplittedInTabs = line.split("\t")
        authorId = lineSplittedInTabs[0]
        authorIdentifier = lineSplittedInTabs[1].split("\"")[1]
   
        if not (authorIdentifier in authors):
            authors[authorIdentifier] = authorId
    
    authorsFile.close()
    
    indices = transactionDict.dictByNumber.keys()
    indices.sort()
    
    for transactionNumber in indices:
        transactionEntity = transactionDict.getEntityByNumber(transactionNumber)
        addTransactionEntity(transactionEntity, transactionBelongsToAuthor, \
                             artefactNext, artefactPrevious, transactionDict, authors)
        transactionId = transactionEntity.getCdifId()
        transactionIdentifier = transactionEntity.getUniqueName()
        transactionInfo = str(transactionId) + "\t\"" + transactionIdentifier + "\"\n";
        transactionsFile.write(transactionInfo)
        transactionTime = convertTimeToUNIX(transactionEntity.getCreationTime())
        timeInfo = str(transactionId) + "\t\"" + str(transactionTime) + "\"\n";
        timeFile.write(timeInfo)
        latestTime = convertTimeToUNIX(transactionEntity.getLatestTime())
        timeInfo = str(transactionId) + "\t\"" + str(latestTime) + "\"\n";
        latestTimeFile.write(timeInfo)
    transactionsFile.close()
    timeFile.close()
    latestTimeFile.close()
    
    indices = transactionBelongsToAuthor.keys()
    indices.sort()
    for transactionId in indices:
        authorId = transactionBelongsToAuthor[transactionId]
        transactionBelongsToAuthorInfo = str(transactionId) + "\t" + str(authorId) + "\n"
        authorFile.write(transactionBelongsToAuthorInfo)
    authorFile.close()
    
    indices = artefactNext.keys()
    indices.sort()
    for transactionId in indices:
        nextId = artefactNext[transactionId]
        nextInfo = str(transactionId) + "\t" + str(nextId) + "\n"
        nextFile.write(nextInfo)
    nextFile.close()
    
    indices = artefactPrevious.keys()
    indices.sort()
    for transactionId in indices:
        previousId = artefactPrevious[transactionId]
        previousInfo = str(transactionId) + "\t" + str(previousId) + "\n"
        previousFile.write(previousInfo)
    previousFile.close()
        
    return EX_OK

def importTransactions(transactionDict, keyById):

    importTransactionFile = open("transactionsWithIDs.txt", 'r')
    
    for line in importTransactionFile:
        line = line.strip()
        lineSplittedInTabs = line.split("\t")
        transactionId = int(lineSplittedInTabs[0])
        transactionIdentifier = lineSplittedInTabs[1].split("\"")[1]
   
        if keyById:
            if not (transactionId in transactionDict):
                transactionDict[transactionId] = transactionIdentifier
        else:
            if not (transactionIdentifier in transactionDict):
                transactionDict[transactionIdentifier] = transactionId
    
    importTransactionFile.close()

