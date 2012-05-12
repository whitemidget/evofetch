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

from evo.cdif2rsf.objects.FunctionEntity import FunctionEntity 
from evo.cdif2rsf.objects.FunctionVersionEntity import FunctionVersionEntity
from evo.common.objects.FunctionVersion import FunctionVersion
from evo.common.processing.Utils import requestNewRSFId

def buildFunctionChanges(cdifFile, changeDict):
    
    """ Reads functions from a CDIF file into a dictionary """
    for line in cdifFile:
        line = line.strip()
        
        # if the line is the start of an entity
        if line.startswith("(FunctionVersion FM"):
            
            revision = None
            functionChange = None
            
            for line in cdifFile:
                line = line.strip()
                if line.startswith("(revision "):
                    revision = line.split("\"")[1]
                elif line.startswith("(versionOfFunction "):
                    functionName = line.split("\"")[1]
                    functionChange = FunctionVersion(revision, functionName) 
                elif line.startswith("(isCreation "):
                    boolValue = (line.split("-")[1] == "TRUE")
                    functionChange.setCreation(boolValue)
                elif line.startswith("(isModification "):
                    boolValue = (line.split("-")[1] == "TRUE")
                    functionChange.setModification(boolValue)
                elif line.startswith("(isDeletion "):
                    boolValue = (line.split("-")[1] == "TRUE")
                    functionChange.setDeletion(boolValue)
                elif line.startswith(")"):
                    changeDict[functionName] = functionChange
                    break
                
def buildFunctions(cdifFile, changeDict, dictionaries, versionDict, containmentDict):
               
    for line in cdifFile:
        line = line.strip()
        
        # if the line is the start of an entity
        if line.startswith("(Function FM") or line.startswith("FunctionDefinition FM"):
                        
            for line in cdifFile:
                line = line.strip()
                if line.startswith("(uniqueName "):
                    uniqueFunctionName = line.split("\"")[1]
                elif line.startswith("(signature "):
                    signature = line.split("\"")[1]
                elif line.startswith("(declaredReturnType "):
                    declaredReturnType = line.split("\"")[1]
                elif line.startswith("(declaredReturnClass "):
                    declaredReturnClass = line.split("\"")[1]
                elif line.startswith("(revision "):
                    revision = line.split("\"")[1]
                elif line.startswith(")"):
                    if uniqueFunctionName in changeDict:
                        functionObj = dictionaries.getFunctionEntity(uniqueFunctionName)
                        if functionObj is None: 
                            functionObj = FunctionEntity()
                            functionObj.setIdentifier(requestNewRSFId())
                            functionObj.setUniqueName(uniqueFunctionName)
                            functionObj.setSignature(signature)
                        functionVersion = FunctionVersionEntity()
                        functionVersion.setIdentifier(requestNewRSFId())
                        functionVersion.setUniqueName(uniqueFunctionName)
                        functionVersion.setFunctionIdentifier(functionObj.getIdentifier())
                        functionVersion.setDeclaredReturnType(declaredReturnType)
                        if declaredReturnClass != "":
                            functionVersion.setDeclaredReturnClassIdentifier( \
                                            dictionaries.getClassId(declaredReturnClass))
                        functionVersion.setRevision(revision)
                        versionDict[uniqueFunctionName] = functionVersion
                        dictionaries.storeFunctionVersion(uniqueFunctionName, functionObj, functionVersion)
                    else:
                        functionVersion = dictionaries.getLatestFunctionVersion(uniqueFunctionName)
                        functionVersion.setRevision(revision)
                    containmentDict[uniqueFunctionName] = functionVersion
                    break
                 
def writeFunctions(inputFile, dictionaries):
    
    changes = {}

    fileHandle = open(inputFile, 'r')
    buildFunctionChanges(fileHandle, changes)
    fileHandle.close()

    versions = {}
    containment = {}
    
    fileHandle = open(inputFile, 'r')
    buildFunctions(fileHandle, changes, dictionaries, versions, containment)
    fileHandle.close()
    
    functionChangedByRevision = {}
    functionCreatedByRevision = {}
    functionModifiedByRevision = {}
    functionDeletedByRevision = {}
    functionVersions = {}
    functionVersionBelongsToRevision = {}

    for change in changes.values():
        functionObj = dictionaries.getFunctionEntity(change.getFunctionName())
        functionId = functionObj.getIdentifier()
        revisionId = dictionaries.getRevision(change.getRevision())
        functionChangedByRevision[functionId] = revisionId
        if change.isCreation():
            functionCreatedByRevision[functionId] = revisionId
        if change.isModification():
            functionModifiedByRevision[functionId] = revisionId
        if change.isDeletion():
            functionDeletedByRevision[functionId] = revisionId
            
    for version in versions.values():
        versionId = version.getIdentifier()
        functionVersions[versionId] = version
        
    for version in containment.values():
        versionId = version.getIdentifier()
        functionVersionBelongsToRevision[versionId] = version
        
    changeFile = open("functionChangedByRevision.txt", 'a')
    creationFile = open("functionCreatedByRevision.txt", 'a')
    modificationFile = open("functionModifiedByRevision.txt", 'a')
    deletionFile = open("functionDeletedByRevision.txt", 'a')
    functionVersionFile = open("functionVersions.txt", 'a')
    functionTypeFile = open("functionVersionHasClassAsReturnType.txt", 'a')
    containmentFile = open("functionVersionBelongsToRevision.txt", 'a')
    
    indices = functionChangedByRevision.keys()
    indices.sort()
    for functionId in indices:
        revisionId = functionChangedByRevision[functionId]
        functionChangedByRevisionInfo = str(functionId) + "\t" + str(revisionId) + "\n"
        changeFile.write(functionChangedByRevisionInfo)
    changeFile.close()
    
    indices = functionCreatedByRevision.keys()
    indices.sort()
    for functionId in indices:
        revisionId = functionCreatedByRevision[functionId]
        functionCreatedByRevisionInfo = str(functionId) + "\t" + str(revisionId) + "\n"
        creationFile.write(functionCreatedByRevisionInfo)
    creationFile.close()
    
    indices = functionModifiedByRevision.keys()
    indices.sort()
    for functionId in indices:
        revisionId = functionModifiedByRevision[functionId]
        functionModifiedByRevisionInfo = str(functionId) + "\t" + str(revisionId) + "\n"
        modificationFile.write(functionModifiedByRevisionInfo)
    modificationFile.close()
    
    indices = functionDeletedByRevision.keys()
    indices.sort()
    for functionId in indices:
        revisionId = functionDeletedByRevision[functionId]
        functionDeletedByRevisionInfo = str(functionId) + "\t" + str(revisionId) + "\n"
        deletionFile.write(functionDeletedByRevisionInfo)
    deletionFile.close()
    
    indices = functionVersions.keys()
    indices.sort()
    for identifier in indices:
        version = functionVersions[identifier]
        functionId = version.getFunctionIdentifier()
        revisionId = dictionaries.getRevision(version.getRevision())
        functionVersionInfo = str(identifier) + "\t" + str(functionId) + \
                            "\t" + str(revisionId) + "\n"
        functionVersionFile.write(functionVersionInfo)
        returnClassId = version.getDeclaredReturnClassIdentifier()
        if not (returnClassId is None):
            returnClassInfo = str(identifier) + "\t" + str(returnClassId) + "\n"
            functionTypeFile.write(returnClassInfo) 
    functionVersionFile.close()
    functionTypeFile.close()
            
    indices = functionVersionBelongsToRevision.keys()
    indices.sort()
    for identifier in indices:
        version = functionVersionBelongsToRevision[identifier]
        revisionId = dictionaries.getRevision(version.getRevision())
        containmentInfo = str(identifier) + "\t" + str(revisionId) + "\n"
        containmentFile.write(containmentInfo)
    containmentFile.close()
            
    return EX_OK

def writeFunctionEntities(dictionaries):
    
    functions = {}
    
    for uniqueFunctionName in dictionaries.functionDict:
        functionObj = dictionaries.getFunctionEntity(uniqueFunctionName)
        functions[functionObj.getIdentifier()] = functionObj
        
    functionsFile = open("functionsWithIDs.txt", 'w')
    functionSignatureFile = open("functionSignature.txt", 'w')
    
    indices = functions.keys()
    indices.sort()
    for identifier in indices:
        functionObj = functions[identifier]
        functionInfo = str(identifier) + "\t" + functionObj.getUniqueName() + "\n"
        functionsFile.write(functionInfo)
        signatureInfo = str(identifier) + "\t" + functionObj.getSignature() + "\n"
        functionSignatureFile.write(signatureInfo)
        
    functionsFile.close()
    functionSignatureFile.close()

    return EX_OK
