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

from evo.cdif2rsf.writeRevisions import importRevisionsByTransaction, importRevisionsOfFiles
from evo.cdif2rsf.writeTransactions import importTransactions
        
def writeSystemVersions(inputFile, control):
    
    transactions = {}
    revisionsOfFiles = {}
    
    importTransactions(transactions, True)
    importRevisionsByTransaction(transactions)
    importRevisionsOfFiles(revisionsOfFiles)
    
    systemVersionFile = open("transactionFileVersion.txt", 'w')
    earliestSystemVersionFile = open("earliestSystemVersion.txt", 'w')
    latestSystemVersionFile = open("latestSystemVersion.txt", 'w')

    currentFiles = {}
    
    indices = transactions.keys()
    indices.sort()
    
    for transactionId in indices:
        transaction = transactions[transactionId]
        
        for revisionId in transaction.revisions:
            fileId = revisionsOfFiles[revisionId]
            currentFiles[fileId] = revisionId
            
        for deletedRevisionId in transaction.deletedRevisions:
            fileId = revisionsOfFiles[deletedRevisionId]
            if fileId in revisionsOfFiles:
                del currentFiles[fileId]
                            
        for fileId in currentFiles:
            revisionId = currentFiles[fileId]
            systemVersionInfo = str(transactionId) + "\t" + str(revisionId) + "\n"
            systemVersionFile.write(systemVersionInfo)
            
    if len(indices) > 0:
        earliestInfo = str(indices[0]) + "\n"
        earliestSystemVersionFile.write(earliestInfo)
        latestInfo = str(indices[-1]) + "\n"    
        latestSystemVersionFile.write(latestInfo)
        
    systemVersionFile.close()
    earliestSystemVersionFile.close()
    latestSystemVersionFile.close()
                
    return EX_OK
