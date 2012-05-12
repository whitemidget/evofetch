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

import sys
from os import EX_OK

def mergeFile(inputFile, relationName, outputHandle):
    inputFile = open(inputFile, 'r')
    for line in inputFile:
        outputHandle.write(relationName + "\t" + line)
    inputFile.close()

def makeRsf(outputFileName):
    outputFile = open(outputFileName, 'w')
    
    mergeFile("earliestSystemVersion.txt", "EarliestSystemVersion", outputFile)
    mergeFile("latestSystemVersion.txt", "LatestSystemVersion", outputFile)
    
    mergeFile("authorsWithIDs.txt", "Author", outputFile)
    mergeFile("authorsFullNames.txt", "AuthorHasName", outputFile)
    mergeFile("authorsEmailAddresses.txt", "AuthorHasEmail", outputFile) 

    mergeFile("transactionsWithIDs.txt", "Transaction", outputFile)
    mergeFile("transactionLatesttime.txt", "LatestTransactionTime", outputFile)
    mergeFile("transactionBelongsToAuthor.txt", "TransactionBelongstoAuthor", outputFile)
    
    mergeFile("modulesWithIDs.txt", "Module", outputFile)
    mergeFile("moduleBelongsToModule.txt", "ModuleBelongsToModule", outputFile)
    mergeFile("filesWithIDs.txt", "File", outputFile)
    mergeFile("fileBelongsToModule.txt", "FileBelongsToModule", outputFile)
        
    mergeFile("revisionsWithIDs.txt", "Revision", outputFile)
    mergeFile("revisionOfFile.txt", "RevisionOfFile", outputFile)
    mergeFile("revisionBelongsToAuthor.txt", "RevisionBelongsToAuthor", outputFile)
    mergeFile("revisionBelongsToTransaction.txt", "RevisionBelongsToTransaction", outputFile)
    mergeFile("revisionDeletedByTransaction.txt", "RevisionDeletedByTransaction", outputFile)

    mergeFile("releasesWithIDs.txt", "Release", outputFile)

    mergeFile("revisionBelongsToRelease.txt", "RevisionBelongsToRelease", outputFile)
    
    mergeFile("transactionFileVersion.txt", "ProducesRevision", outputFile)    

    mergeFile("artefactTime.txt", "HasTimeStamp", outputFile)
    mergeFile("artefactNext.txt", "Next", outputFile)
    mergeFile("artefactPrevious.txt", "Previous", outputFile)

    mergeFile("classesWithIDs.txt", "Class", outputFile)
    mergeFile("classChangedByRevision.txt", "ClassChangedByRevision", outputFile)
    mergeFile("classCreatedByRevision.txt", "ClassCreatedByRevision", outputFile)
    mergeFile("classModifiedByRevision.txt", "ClassModifiedByRevision", outputFile)
    mergeFile("classDeletedByRevision.txt", "ClassDeletedByRevision", outputFile)
    mergeFile("classVersions.txt", "ClassVersion", outputFile)
    mergeFile("classVersionBelongsToRevision.txt", "ClassVersionBelongsToRevision", outputFile)
    mergeFile("inheritanceWithIDs.txt", "InheritsFrom", outputFile)
    
    mergeFile("methodsWithIDs.txt", "Method", outputFile)
    mergeFile("methodBelongsToClass.txt", "MethodBelongsToClass", outputFile)
    mergeFile("methodSignature.txt", "Signature", outputFile)
    mergeFile("methodChangedByRevision.txt", "MethodChangedByRevision", outputFile)
    mergeFile("methodCreatedByRevision.txt", "MethodCreatedByRevision", outputFile)
    mergeFile("methodModifiedByRevision.txt", "MethodModifiedByRevision", outputFile)
    mergeFile("methodDeletedByRevision.txt", "MethodDeletedByRevision", outputFile)
    mergeFile("methodVersions.txt", "MethodVersion", outputFile)
    mergeFile("methodVersionBelongsToClassVersion.txt", "MethodVersionBelongsToClassVersion", outputFile)
    mergeFile("methodVersionHasClassAsReturnType.txt", "HasType", outputFile)
    mergeFile("methodVersionVisibility.txt", "Visibility", outputFile)
    
    mergeFile("functionsWithIDs.txt", "Function", outputFile)
    mergeFile("functionSignature.txt", "Signature", outputFile)
    mergeFile("functionChangedByRevision.txt", "FunctionChangedByRevision", outputFile)
    mergeFile("functionCreatedByRevision.txt", "FunctionCreatedByRevision", outputFile)
    mergeFile("functionModifiedByRevision.txt", "FunctionModifiedByRevision", outputFile)
    mergeFile("functionDeletedByRevision.txt", "FunctionDeletedByRevision", outputFile)
    mergeFile("functionVersions.txt", "FunctionVersion", outputFile)
    mergeFile("functionVersionBelongsToRevision.txt", "FunctionVersionBelongsToRevision", outputFile)
    mergeFile("functionVersionHasClassAsReturnType.txt", "HasType", outputFile)
    
    mergeFile("attributesWithIDs.txt", "Attribute", outputFile)
    mergeFile("attributeBelongsToClass.txt", "AttributeBelongsToClass", outputFile)
    mergeFile("attributeChangedByRevision.txt", "AttributeChangedByRevision", outputFile)
    mergeFile("attributeCreatedByRevision.txt", "AttributeCreatedByRevision", outputFile)
    mergeFile("attributeModifiedByRevision.txt", "AttributeModifiedByRevision", outputFile)
    mergeFile("attributeDeletedByRevision.txt", "AttributeDeletedByRevision", outputFile)
    mergeFile("attributeVersions.txt", "AttributeVersion", outputFile)
    mergeFile("attributeVersionBelongsToClassVersion.txt", "AttributeVersionBelongsToClassVersion", outputFile)
    mergeFile("attributeVersionHasClassAsType.txt", "HasType", outputFile)
    mergeFile("attributeVersionVisibility.txt", "Visibility", outputFile)
    
    mergeFile("globalVariablesWithIDs.txt", "GlobalVariable", outputFile)
    mergeFile("globalVariableChangedByRevision.txt", "GlobalVariableChangedByRevision", outputFile)
    mergeFile("globalVariableCreatedByRevision.txt", "GlobalVariableCreatedByRevision", outputFile)
    mergeFile("globalVariableModifiedByRevision.txt", "GlobalVariableModifiedByRevision", outputFile)
    mergeFile("globalVariableDeletedByRevision.txt", "GlobalVariableDeletedByRevision", outputFile)
    mergeFile("globalVariableVersions.txt", "GlobalVariableVersion", outputFile)
    mergeFile("globalVariableVersionBelongsToRevision.txt", "GlobalVariableVersionBelongsToRevision", outputFile)
    mergeFile("globalVariableVersionHasClassAsType.txt", "HasType", outputFile)        
    
    outputFile.close()
    
    return EX_OK

## main
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage:", sys.argv[0], "rsf-output-file-name"
        sys.exit(64)
    
    output_file_name = sys.argv[1]
    sys.exit(makeRsf(output_file_name))
