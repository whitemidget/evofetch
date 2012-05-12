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

from evo.cdif2rsf.objects.ClassVersionEntity import ClassVersionEntity
from evo.cdif2rsf.objects.InheritanceEntity import InheritanceEntity
from evo.common.objects.ClassVersion import ClassVersion
from evo.common.processing.Utils import requestNewRSFId

def buildClassChanges(cdifFile, changeDict):
    
    """ Reads classes from a CDIF file into a dictionary """
    for line in cdifFile:
        line = line.strip()
        
        # if the line is the start of an entity
        if line.startswith("(ClassVersion FM"):
            
            revision = None
            classChange = None
            
            for line in cdifFile:
                line = line.strip()
                if line.startswith("(revision "):
                    revision = line.split("\"")[1]
                elif line.startswith("(versionOfClass "):
                    className = line.split("\"")[1]
                    classChange = ClassVersion(revision, className) 
                elif line.startswith("(isCreation "):
                    boolValue = (line.split("-")[1] == "TRUE")
                    classChange.setCreation(boolValue)
                elif line.startswith("(isModification "):
                    boolValue = (line.split("-")[1] == "TRUE")
                    classChange.setModification(boolValue)
                elif line.startswith("(isDeletion "):
                    boolValue = (line.split("-")[1] == "TRUE")
                    classChange.setDeletion(boolValue)
                elif line.startswith(")"):
                    changeDict[className] = classChange
                    break
                
def buildClasses(cdifFile, changeDict, dictionaries, versionDict, containmentDict):
               
    for line in cdifFile:
        line = line.strip()
        
        # if the line is the start of an entity
        if line.startswith("(Class FM"):
                        
            for line in cdifFile:
                line = line.strip()
                if line.startswith("(uniqueName "):
                    uniqueClassName = line.split("\"")[1]
                elif line.startswith("(isAbstract "):
                    isAbstract = (line.split("-")[1] == "TRUE")
                elif line.startswith("(revision "):
                    revision = line.split("\"")[1]
                elif line.startswith(")"):
                    if uniqueClassName in changeDict:
                        rsfNumber = dictionaries.getClassId(uniqueClassName)
                        if rsfNumber is None:
                            rsfNumber = requestNewRSFId()
                        classVersion = ClassVersionEntity()
                        classVersion.setIdentifier(requestNewRSFId())
                        classVersion.setUniqueName(uniqueClassName)
                        classVersion.setClassIdentifier(rsfNumber)
                        classVersion.setAbstract(isAbstract)
                        classVersion.setRevision(revision)
                        versionDict[uniqueClassName] = classVersion
                        dictionaries.storeClassVersion(uniqueClassName, rsfNumber, classVersion)
                    else:
                        classVersion = dictionaries.getLatestClassVersion(uniqueClassName)
                        classVersion.setRevision(revision)
                    containmentDict[uniqueClassName] = classVersion
                    break

def buildInheritance(cdifFile, changeDict, dictionaries, versionDict, inheritanceDict):

    if len(changeDict) > 0:
        for line in cdifFile:
            line = line.strip()
            
            if line.startswith("(InheritanceDefinition FM"):
                
                subclass = ""
                superclass = ""
                
                for line in cdifFile:
                    line = line.strip()
                    if line.startswith("(subclass "):
                        subclass = line.split("\"")[1]
                        if not (subclass in changeDict):
                            break
                    elif line.startswith("(superclass "):
                        superclass = line.split("\"")[1]
                    elif line.startswith(")"):
                        inheritanceId = requestNewRSFId()
                        classVersion = versionDict[subclass]
                        superClassId = dictionaries.getClassId(superclass)
                        inheritance = InheritanceEntity()
                        inheritance.setIdentifier(inheritanceId)
                        inheritance.setSubclassName(subclass)
                        inheritance.setSubclassVersionIdentifier(classVersion.getIdentifier())
                        inheritance.setSuperclassName(superclass)
                        inheritance.setSuperclassIdentifier(superClassId)
                        inheritanceDict[inheritanceId] = inheritance
                        break                                                

def writeClasses(inputFile, dictionaries):
    
    changes = {}

    fileHandle = open(inputFile, 'r')
    buildClassChanges(fileHandle, changes)
    fileHandle.close()

    versions = {}
    containment = {}
    
    fileHandle = open(inputFile, 'r')
    buildClasses(fileHandle, changes, dictionaries, versions, containment)
    fileHandle.close()

    inheritance = {}
    
    fileHandle = open(inputFile, 'r')
    buildInheritance(fileHandle, changes, dictionaries, versions, inheritance)
    fileHandle.close()
    
    classChangedByRevision = {}
    classCreatedByRevision = {}
    classModifiedByRevision = {}
    classDeletedByRevision = {}
    classVersions = {}
    classVersionBelongsToRevision = {}

    for change in changes.values():
        classId = dictionaries.getClassId(change.getClassName())
        revisionId = dictionaries.getRevision(change.getRevision())
        classChangedByRevision[classId] = revisionId
        if change.isCreation():
            classCreatedByRevision[classId] = revisionId
        if change.isModification():
            classModifiedByRevision[classId] = revisionId
        if change.isDeletion():
            classDeletedByRevision[classId] = revisionId
            
    for version in versions.values():
        versionId = version.getIdentifier()
        classVersions[versionId] = version
        
    for version in containment.values():
        versionId = version.getIdentifier()
        classVersionBelongsToRevision[versionId] = version
        
    changeFile = open("classChangedByRevision.txt", 'a')
    creationFile = open("classCreatedByRevision.txt", 'a')
    modificationFile = open("classModifiedByRevision.txt", 'a')
    deletionFile = open("classDeletedByRevision.txt", 'a')
    classVersionFile = open("classVersions.txt", 'a')
    inheritanceFile = open("inheritanceWithIDs.txt", 'a')
    containmentFile = open("classVersionBelongsToRevision.txt", 'a')
    
    indices = classChangedByRevision.keys()
    indices.sort()
    for classId in indices:
        revisionId = classChangedByRevision[classId]
        classChangedByRevisionInfo = str(classId) + "\t" + str(revisionId) + "\n"
        changeFile.write(classChangedByRevisionInfo)
    changeFile.close()
    
    indices = classCreatedByRevision.keys()
    indices.sort()
    for classId in indices:
        revisionId = classCreatedByRevision[classId]
        classCreatedByRevisionInfo = str(classId) + "\t" + str(revisionId) + "\n"
        creationFile.write(classCreatedByRevisionInfo)
    creationFile.close()
    
    indices = classModifiedByRevision.keys()
    indices.sort()
    for classId in indices:
        revisionId = classModifiedByRevision[classId]
        classModifiedByRevisionInfo = str(classId) + "\t" + str(revisionId) + "\n"
        modificationFile.write(classModifiedByRevisionInfo)
    modificationFile.close()
    
    indices = classDeletedByRevision.keys()
    indices.sort()
    for classId in indices:
        revisionId = classDeletedByRevision[classId]
        classDeletedByRevisionInfo = str(classId) + "\t" + str(revisionId) + "\n"
        deletionFile.write(classDeletedByRevisionInfo)
    deletionFile.close()
    
    indices = classVersions.keys()
    indices.sort()
    for identifer in indices:
        version = classVersions[identifer]
        classId = version.getClassIdentifier()
        revisionId = dictionaries.getRevision(version.getRevision())
        classVersionInfo = str(identifer) + "\t" + str(classId) + \
                           "\t" + str(revisionId) + "\n"
        classVersionFile.write(classVersionInfo)
    classVersionFile.close()
    
    indices = classVersionBelongsToRevision.keys()
    indices.sort()
    for identifier in indices:
        version = classVersionBelongsToRevision[identifier]
        revisionId = dictionaries.getRevision(version.getRevision())
        containmentInfo = str(identifier) + "\t" + str(revisionId) + "\n"
        containmentFile.write(containmentInfo)
    containmentFile.close()
    
    indices = inheritance.keys()
    indices.sort()
    for identifier in indices:
        inheritanceEntity = inheritance[identifier]
        identifier = inheritanceEntity.getIdentifier()
        subclassName = inheritanceEntity.getSubclassName()
        subclassId = inheritanceEntity.getSubclassVersionIdentifier()
        superclassName = inheritanceEntity.getSuperclassName()
        superclassId = inheritanceEntity.getSuperclassIdentifier()
        inhInfo = str(identifier) + "\t\"" + subclassName + "->" + \
                  superclassName + "\"\t" + str(subclassId) + "\t" + \
                  str(superclassId) + "\n"
        inheritanceFile.write(inhInfo)
    inheritanceFile.close()        
            
    return EX_OK

def writeClassEntities(dictionaries):
    
    classes = {}
    
    for uniqueClassName in dictionaries.classDict:
        rsfNumber = dictionaries.getClassId(uniqueClassName)
        classes[rsfNumber] = uniqueClassName
    
    classesFile = open("classesWithIDs.txt", 'w')
    
    indices = classes.keys()
    indices.sort()
    for rsfNumber in indices:
        uniqueClassName = classes[rsfNumber]
        classInfo = str(rsfNumber) + "\t" + uniqueClassName + "\n"
        classesFile.write(classInfo)
        
    classesFile.close()
    
    return EX_OK

