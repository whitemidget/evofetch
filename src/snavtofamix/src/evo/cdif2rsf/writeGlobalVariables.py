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

from evo.cdif2rsf.objects.GlobalVariableEntity import GlobalVariableEntity
from evo.cdif2rsf.objects.GlobalVariableVersionEntity import GlobalVariableVersionEntity
from evo.common.objects.GlobalVariableVersion import GlobalVariableVersion
from evo.common.processing.Utils import requestNewRSFId

def buildGlobalVariableChanges(cdifFile, changeDict):
    
    """ Reads global variables from a CDIF file into a dictionary """
    for line in cdifFile:
        line = line.strip()
        
        # if the line is the start of an entity
        if line.startswith("(GlobalVariableVersion FM"):
            
            revision = None
            globalVariableChange = None
            
            for line in cdifFile:
                line = line.strip()
                if line.startswith("(revision "):
                    revision = line.split("\"")[1]
                elif line.startswith("(versionOfGlobalVariable "):
                    globalVariableName = line.split("\"")[1]
                    globalVariableChange = GlobalVariableVersion(revision, globalVariableName) 
                elif line.startswith("(isCreation "):
                    boolValue = (line.split("-")[1] == "TRUE")
                    globalVariableChange.setCreation(boolValue)
                elif line.startswith("(isModification "):
                    boolValue = (line.split("-")[1] == "TRUE")
                    globalVariableChange.setModification(boolValue)
                elif line.startswith("(isDeletion "):
                    boolValue = (line.split("-")[1] == "TRUE")
                    globalVariableChange.setDeletion(boolValue)
                elif line.startswith(")"):
                    changeDict[globalVariableName] = globalVariableChange
                    break
                
def buildGlobalVariables(cdifFile, changeDict, dictionaries, versionDict, containmentDict):
               
    for line in cdifFile:
        line = line.strip()
        
        # if the line is the start of an entity
        if line.startswith("(GlobalVariable FM"):
                        
            for line in cdifFile:
                line = line.strip()
                if line.startswith("(uniqueName "):
                    uniqueGlobalVariableName = line.split("\"")[1]
                elif line.startswith("(declaredType "):
                    declaredType = line.split("\"")[1]
                elif line.startswith("(declaredClass "):
                    declaredClass = line.split("\"")[1]
                elif line.startswith("(revision "):
                    revision = line.split("\"")[1]
                elif line.startswith(")"):
                    if uniqueGlobalVariableName in changeDict:
                        globalVariable = dictionaries.getGlobalVariableEntity(uniqueGlobalVariableName)
                        if globalVariable is None: 
                            globalVariable = GlobalVariableEntity()
                            globalVariable.setIdentifier(requestNewRSFId())
                            globalVariable.setUniqueName(uniqueGlobalVariableName)
                        globalVariableVersion = GlobalVariableVersionEntity()
                        globalVariableVersion.setIdentifier(requestNewRSFId())
                        globalVariableVersion.setUniqueName(uniqueGlobalVariableName)
                        globalVariableVersion.setGlobalVariableIdentifier(globalVariable.getIdentifier())
                        globalVariableVersion.setDeclaredType(declaredType)
                        if declaredClass != "":
                            globalVariableVersion.setDeclaredClassIdentifier( \
                                             dictionaries.getClassId(declaredClass))
                        globalVariableVersion.setRevision(revision)
                        versionDict[uniqueGlobalVariableName] = globalVariableVersion
                        dictionaries.storeGlobalVariableVersion(uniqueGlobalVariableName, \
                                                                globalVariable, \
                                                                globalVariableVersion)
                    else:
                        globalVariableVersion = dictionaries.getLatestGlobalVariableVersion(uniqueGlobalVariableName)
                        globalVariableVersion.setRevision(revision)
                    containmentDict[uniqueGlobalVariableName] = globalVariableVersion
                    break
                 
def writeGlobalVariables(inputFile, dictionaries):
    
    changes = {}

    fileHandle = open(inputFile, 'r')
    buildGlobalVariableChanges(fileHandle, changes)
    fileHandle.close()

    versions = {}
    containment = {}
    
    fileHandle = open(inputFile, 'r')
    buildGlobalVariables(fileHandle, changes, dictionaries, versions, containment)
    fileHandle.close()
    
    globalVariableChangedByRevision = {}
    globalVariableCreatedByRevision = {}
    globalVariableModifiedByRevision = {}
    globalVariableDeletedByRevision = {}
    globalVariableVersions = {}
    globalVariableVersionBelongsToRevision = {}

    for change in changes.values():
        globalVariable = dictionaries.getGlobalVariableEntity(change.getGlobalVariableName())
        globalVariableId = globalVariable.getIdentifier()
        revisionId = dictionaries.getRevision(change.getRevision())
        globalVariableChangedByRevision[globalVariableId] = revisionId
        if change.isCreation():
            globalVariableCreatedByRevision[globalVariableId] = revisionId
        if change.isModification():
            globalVariableModifiedByRevision[globalVariableId] = revisionId
        if change.isDeletion():
            globalVariableDeletedByRevision[globalVariableId] = revisionId
            
    for version in versions.values():
        versionId = version.getIdentifier()
        globalVariableVersions[versionId] = version
        
    for version in containment.values():
        versionId = version.getIdentifier()
        globalVariableVersionBelongsToRevision[versionId] = version

    changeFile = open("globalVariableChangedByRevision.txt", 'a')
    creationFile = open("globalVariableCreatedByRevision.txt", 'a')
    modificationFile = open("globalVariableModifiedByRevision.txt", 'a')
    deletionFile = open("globalVariableDeletedByRevision.txt", 'a')
    globalVariableVersionFile = open("globalVariableVersions.txt", 'a')
    globalVariableTypeFile = open("globalVariableVersionHasClassAsType.txt", 'a')
    containmentFile = open("globalVariableVersionBelongsToRevision.txt", 'a')
    
    indices = globalVariableChangedByRevision.keys()
    indices.sort()
    for globalVariableId in indices:
        revisionId = globalVariableChangedByRevision[globalVariableId]
        globalVariableChangedByRevisionInfo = str(globalVariableId) + "\t" + str(revisionId) + "\n"
        changeFile.write(globalVariableChangedByRevisionInfo)
    changeFile.close()
    
    indices = globalVariableCreatedByRevision.keys()
    indices.sort()
    for globalVariableId in indices:
        revisionId = globalVariableCreatedByRevision[globalVariableId]
        globalVariableCreatedByRevisionInfo = str(globalVariableId) + "\t" + str(revisionId) + "\n"
        creationFile.write(globalVariableCreatedByRevisionInfo)
    creationFile.close()
    
    indices = globalVariableModifiedByRevision.keys()
    indices.sort()
    for globalVariableId in indices:
        revisionId = globalVariableModifiedByRevision[globalVariableId]
        globalVariableModifiedByRevisionInfo = str(globalVariableId) + "\t" + str(revisionId) + "\n"
        modificationFile.write(globalVariableModifiedByRevisionInfo)
    modificationFile.close()
    
    indices = globalVariableDeletedByRevision.keys()
    indices.sort()
    for globalVariableId in indices:
        revisionId = globalVariableDeletedByRevision[globalVariableId]
        globalVariableDeletedByRevisionInfo = str(globalVariableId) + "\t" + str(revisionId) + "\n"
        deletionFile.write(globalVariableDeletedByRevisionInfo)
    deletionFile.close()
    
    indices = globalVariableVersions.keys()
    indices.sort()
    for identifier in indices:
        version = globalVariableVersions[identifier]
        globalVariableId = version.getGlobalVariableIdentifier()
        revisionId = dictionaries.getRevision(version.getRevision())
        globalVariableVersionInfo = str(identifier) + "\t" + str(globalVariableId) + \
                               "\t" + str(revisionId) + "\n"
        globalVariableVersionFile.write(globalVariableVersionInfo)
        typeClassId = version.getDeclaredClassIdentifier()
        if not (typeClassId is None):
            typeClassInfo = str(identifier) + "\t" + str(typeClassId) + "\n"
            globalVariableTypeFile.write(typeClassInfo) 
    globalVariableVersionFile.close()
    globalVariableTypeFile.close()
            
    indices = globalVariableVersionBelongsToRevision.keys()
    indices.sort()
    for identifier in indices:
        version = globalVariableVersionBelongsToRevision[identifier]
        revisionId = dictionaries.getRevision(version.getRevision())
        containmentInfo = str(identifier) + "\t" + str(revisionId) + "\n"
        containmentFile.write(containmentInfo)
    containmentFile.close()
            
    return EX_OK

def writeGlobalVariableEntities(dictionaries):
    
    globalVariables = {}
    
    for uniqueGlobalVariableName in dictionaries.globalVariableDict:
        globalVariable = dictionaries.getGlobalVariableEntity(uniqueGlobalVariableName)
        globalVariables[globalVariable.getIdentifier()] = globalVariable
        
    globalVariablesFile = open("globalVariablesWithIDs.txt", 'w')
    
    indices = globalVariables.keys()
    indices.sort()
    for identifier in indices:
        globalVariable = globalVariables[identifier]
        globalVariableInfo = str(identifier) + "\t" + globalVariable.getUniqueName() + "\n"
        globalVariablesFile.write(globalVariableInfo)
        
    globalVariablesFile.close()

    return EX_OK
