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

from evo.cdif2rsf.objects.MethodEntity import MethodEntity
from evo.cdif2rsf.objects.MethodVersionEntity import MethodVersionEntity
from evo.common.objects.MethodVersion import MethodVersion
from evo.common.processing.Utils import requestNewRSFId

def buildMethodChanges(cdifFile, changeDict):
    
    """ Reads methods from a CDIF file into a dictionary """
    for line in cdifFile:
        line = line.strip()
        
        # if the line is the start of an entity
        if line.startswith("(MethodVersion FM"):
            
            revision = None
            methodChange = None
            
            for line in cdifFile:
                line = line.strip()
                if line.startswith("(revision "):
                    revision = line.split("\"")[1]
                elif line.startswith("(versionOfMethod "):
                    methodName = line.split("\"")[1]
                    methodChange = MethodVersion(revision, methodName) 
                elif line.startswith("(isCreation "):
                    boolValue = (line.split("-")[1] == "TRUE")
                    methodChange.setCreation(boolValue)
                elif line.startswith("(isModification "):
                    boolValue = (line.split("-")[1] == "TRUE")
                    methodChange.setModification(boolValue)
                elif line.startswith("(isDeletion "):
                    boolValue = (line.split("-")[1] == "TRUE")
                    methodChange.setDeletion(boolValue)
                elif line.startswith(")"):
                    changeDict[methodName] = methodChange
                    break
                
def buildMethods(cdifFile, changeDict, dictionaries, versionDict, containmentDict):
               
    for line in cdifFile:
        line = line.strip()
        
        # if the line is the start of an entity
        if line.startswith("(Method FM") or line.startswith("MethodDefinition FM"):
                        
            for line in cdifFile:
                line = line.strip()
                if line.startswith("(belongsTo "):
                    parentClass = line.split("\"")[1]
                elif line.startswith("(uniqueName "):
                    uniqueMethodName = line.split("\"")[1]
                elif line.startswith("(isAbstract "):
                    isAbstract = (line.split("-")[1] == "TRUE")
                elif line.startswith("(accessControlQualifier "):
                    accessControlQualifier = line.split("\"")[1]
                elif line.startswith("(signature "):
                    signature = line.split("\"")[1]
                elif line.startswith("(declaredReturnType "):
                    declaredReturnType = line.split("\"")[1]
                elif line.startswith("(declaredReturnClass "):
                    declaredReturnClass = line.split("\"")[1]
                elif line.startswith("(hasClassScope "):
                    hasClassScope = (line.split("-")[1] == "TRUE")
                elif line.startswith("(revision "):
                    revision = line.split("\"")[1]
                elif line.startswith(")"):
                    latestClassVersion = dictionaries.getLatestClassVersion(parentClass)
                    if uniqueMethodName in changeDict:
                        method = dictionaries.getMethodEntity(uniqueMethodName)
                        if method is None: 
                            method = MethodEntity()
                            method.setIdentifier(requestNewRSFId())
                            method.setUniqueName(uniqueMethodName)
                            method.setClassIdentifier(dictionaries.getClassId(parentClass))
                            method.setSignature(signature)
                        methodVersion = MethodVersionEntity()
                        methodVersion.setIdentifier(requestNewRSFId())
                        methodVersion.setUniqueName(uniqueMethodName)
                        methodVersion.setMethodIdentifier(method.getIdentifier())
                        methodVersion.setAbstract(isAbstract)
                        methodVersion.setAccessControlQualifier(accessControlQualifier)
                        methodVersion.setDeclaredReturnType(declaredReturnType)
                        if declaredReturnClass != "":
                            methodVersion.setDeclaredReturnClassIdentifier( \
                                          dictionaries.getClassId(declaredReturnClass))
                        methodVersion.setClassScope(hasClassScope)
                        methodVersion.setRevision(revision)
                        methodVersion.setClassVersion(latestClassVersion)
                        versionDict[uniqueMethodName] = methodVersion
                        dictionaries.storeMethodVersion(uniqueMethodName, \
                                                        method, methodVersion)
                        containmentDict[uniqueMethodName] = methodVersion
                    else:
                        methodRevisionId = dictionaries.getRevision(revision)
                        classRevisionId = dictionaries.getRevision(latestClassVersion.getRevision())
                        if classRevisionId > methodRevisionId:
                            methodVersion = dictionaries.getLatestMethodVersion(uniqueMethodName)
                            methodVersion.setRevision(revision)
                            methodVersion.setClassVersion(latestClassVersion)
                            containmentDict[uniqueMethodName] = methodVersion
                    break
                 
def writeMethods(inputFile, dictionaries):
    
    changes = {}

    fileHandle = open(inputFile, 'r')
    buildMethodChanges(fileHandle, changes)
    fileHandle.close()

    versions = {}
    containment = {}
    
    fileHandle = open(inputFile, 'r')
    buildMethods(fileHandle, changes, dictionaries, versions, containment)
    fileHandle.close()
    
    methodChangedByRevision = {}
    methodCreatedByRevision = {}
    methodModifiedByRevision = {}
    methodDeletedByRevision = {}
    methodVersions = {}
    methodVersionBelongsToClassVersion = {}

    for change in changes.values():
        method = dictionaries.getMethodEntity(change.getMethodName())
        methodId = method.getIdentifier()
        revisionId = dictionaries.getRevision(change.getRevision())
        methodChangedByRevision[methodId] = revisionId
        if change.isCreation():
            methodCreatedByRevision[methodId] = revisionId
        if change.isModification():
            methodModifiedByRevision[methodId] = revisionId
        if change.isDeletion():
            methodDeletedByRevision[methodId] = revisionId
            
    for version in versions.values():
        versionId = version.getIdentifier()
        methodVersions[versionId] = version
        
    for version in containment.values():
        versionId = version.getIdentifier()
        methodVersionBelongsToClassVersion[versionId] = version
        
    changeFile = open("methodChangedByRevision.txt", 'a')
    creationFile = open("methodCreatedByRevision.txt", 'a')
    modificationFile = open("methodModifiedByRevision.txt", 'a')
    deletionFile = open("methodDeletedByRevision.txt", 'a')
    methodVersionFile = open("methodVersions.txt", 'a')
    methodTypeFile = open("methodVersionHasClassAsReturnType.txt", 'a')
    methodVisibilityFile = open("methodVersionVisibility.txt", 'a')
    containmentFile = open("methodVersionBelongsToClassVersion.txt", 'a')
    
    indices = methodChangedByRevision.keys()
    indices.sort()
    for methodId in indices:
        revisionId = methodChangedByRevision[methodId]
        methodChangedByRevisionInfo = str(methodId) + "\t" + str(revisionId) + "\n"
        changeFile.write(methodChangedByRevisionInfo)
    changeFile.close()
    
    indices = methodCreatedByRevision.keys()
    indices.sort()
    for methodId in indices:
        revisionId = methodCreatedByRevision[methodId]
        methodCreatedByRevisionInfo = str(methodId) + "\t" + str(revisionId) + "\n"
        creationFile.write(methodCreatedByRevisionInfo)
    creationFile.close()
    
    indices = methodModifiedByRevision.keys()
    indices.sort()
    for methodId in indices:
        revisionId = methodModifiedByRevision[methodId]
        methodModifiedByRevisionInfo = str(methodId) + "\t" + str(revisionId) + "\n"
        modificationFile.write(methodModifiedByRevisionInfo)
    modificationFile.close()
    
    indices = methodDeletedByRevision.keys()
    indices.sort()
    for methodId in indices:
        revisionId = methodDeletedByRevision[methodId]
        methodDeletedByRevisionInfo = str(methodId) + "\t" + str(revisionId) + "\n"
        deletionFile.write(methodDeletedByRevisionInfo)
    deletionFile.close()
    
    indices = methodVersions.keys()
    indices.sort()
    for identifier in indices:
        version = methodVersions[identifier]
        methodId = version.getMethodIdentifier()
        revisionId = dictionaries.getRevision(version.getRevision())
        methodVersionInfo = str(identifier) + "\t" + str(methodId) + \
                            "\t" + str(revisionId) + "\n"
        methodVersionFile.write(methodVersionInfo)
        returnClassId = version.getDeclaredReturnClassIdentifier()
        if not (returnClassId is None):
            returnClassInfo = str(identifier) + "\t" + str(returnClassId) + "\n"
            methodTypeFile.write(returnClassInfo) 
        visibility = version.getAccessControlQualifier()
        if visibility != "":
            visibilityInfo = str(identifier) + "\t\"" + visibility + "\"\n"
            methodVisibilityFile.write(visibilityInfo)
    methodVersionFile.close()
    methodTypeFile.close()
    methodVisibilityFile.close()
            
    indices = methodVersionBelongsToClassVersion.keys()
    indices.sort()
    for identifier in indices:
        version = methodVersionBelongsToClassVersion[identifier]
        classVersion = version.getClassVersion()
        classVersionId = classVersion.getIdentifier()
        containmentInfo = str(identifier) + "\t" + str(classVersionId) + "\n"
        containmentFile.write(containmentInfo)
    containmentFile.close()
            
    return EX_OK

def writeMethodEntities(dictionaries):
    
    methods = {}
    
    for uniqueMethodName in dictionaries.methodDict:
        method = dictionaries.getMethodEntity(uniqueMethodName)
        methods[method.getIdentifier()] = method
        
    methodsFile = open("methodsWithIDs.txt", 'w')
    methodContainmentFile = open("methodBelongsToClass.txt", 'w')
    methodSignatureFile = open("methodSignature.txt", 'w')
    
    indices = methods.keys()
    indices.sort()
    for identifier in indices:
        method = methods[identifier]
        methodInfo = str(identifier) + "\t" + method.getUniqueName() + "\n"
        methodsFile.write(methodInfo)
        containmentInfo = str(identifier) + "\t" + str(method.getClassIdentifier()) + "\n"
        methodContainmentFile.write(containmentInfo)
        signatureInfo = str(identifier) + "\t" + method.getSignature() + "\n"
        methodSignatureFile.write(signatureInfo)
        
    methodsFile.close()
    methodContainmentFile.close()
    methodSignatureFile.close()

    return EX_OK