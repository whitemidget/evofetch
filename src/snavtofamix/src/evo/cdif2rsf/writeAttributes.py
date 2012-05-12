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

from evo.cdif2rsf.objects.AttributeEntity import AttributeEntity
from evo.cdif2rsf.objects.AttributeVersionEntity import AttributeVersionEntity
from evo.common.objects.AttributeVersion import AttributeVersion
from evo.common.processing.Utils import requestNewRSFId

def buildAttributeChanges(cdifFile, changeDict):
    
    """ Reads attributes from a CDIF file into a dictionary """
    for line in cdifFile:
        line = line.strip()
        
        # if the line is the start of an entity
        if line.startswith("(AttributeVersion FM"):
            
            revision = None
            attributeChange = None
            
            for line in cdifFile:
                line = line.strip()
                if line.startswith("(revision "):
                    revision = line.split("\"")[1]
                elif line.startswith("(versionOfAttribute "):
                    attributeName = line.split("\"")[1]
                    attributeChange = AttributeVersion(revision, attributeName) 
                elif line.startswith("(isCreation "):
                    boolValue = (line.split("-")[1] == "TRUE")
                    attributeChange.setCreation(boolValue)
                elif line.startswith("(isModification "):
                    boolValue = (line.split("-")[1] == "TRUE")
                    attributeChange.setModification(boolValue)
                elif line.startswith("(isDeletion "):
                    boolValue = (line.split("-")[1] == "TRUE")
                    attributeChange.setDeletion(boolValue)
                elif line.startswith(")"):
                    changeDict[attributeName] = attributeChange
                    break
                
def buildAttributes(cdifFile, changeDict, dictionaries, versionDict, containmentDict):
               
    for line in cdifFile:
        line = line.strip()
        
        # if the line is the start of an entity
        if line.startswith("(Attribute FM"):
                        
            for line in cdifFile:
                line = line.strip()
                if line.startswith("(uniqueName "):
                    uniqueAttributeName = line.split("\"")[1]
                elif line.startswith("(belongsTo "):
                    parentClass = line.split("\"")[1]
                elif line.startswith("(declaredType "):
                    declaredType = line.split("\"")[1]
                elif line.startswith("(declaredClass "):
                    declaredClass = line.split("\"")[1]
                elif line.startswith("(accessControlQualifier "):
                    accessControlQualifier = line.split("\"")[1]
                elif line.startswith("(hasClassScope "):
                    hasClassScope = (line.split("-")[1] == "TRUE")
                elif line.startswith("(revision "):
                    revision = line.split("\"")[1]
                elif line.startswith(")"):
                    latestClassVersion = dictionaries.getLatestClassVersion(parentClass)
                    if uniqueAttributeName in changeDict:
                        attribute = dictionaries.getAttributeEntity(uniqueAttributeName)
                        if attribute is None: 
                            attribute = AttributeEntity()
                            attribute.setIdentifier(requestNewRSFId())
                            attribute.setUniqueName(uniqueAttributeName)
                            attribute.setClassIdentifier(dictionaries.getClassId(parentClass))
                        attributeVersion = AttributeVersionEntity()
                        attributeVersion.setIdentifier(requestNewRSFId())
                        attributeVersion.setUniqueName(uniqueAttributeName)
                        attributeVersion.setAttributeIdentifier(attribute.getIdentifier())
                        attributeVersion.setAccessControlQualifier(accessControlQualifier)
                        attributeVersion.setDeclaredType(declaredType)
                        if declaredClass != "":
                            attributeVersion.setDeclaredClassIdentifier( \
                                             dictionaries.getClassId(declaredClass))
                        attributeVersion.setClassScope(hasClassScope)
                        attributeVersion.setRevision(revision)
                        attributeVersion.setClassVersion(latestClassVersion)
                        versionDict[uniqueAttributeName] = attributeVersion
                        dictionaries.storeAttributeVersion(uniqueAttributeName, attribute, attributeVersion)
                    else:
                        attributeRevisionId = dictionaries.getRevision(revision)
                        classRevisionId = dictionaries.getRevision(latestClassVersion.getRevision())
                        if classRevisionId > attributeRevisionId:
                            attributeVersion = dictionaries.getLatestAttributeVersion(uniqueAttributeName)
                            attributeVersion.setRevision(revision)
                            attributeVersion.setClassVersion(latestClassVersion)
                            containmentDict[uniqueAttributeName] = attributeVersion
                    break
                 
def writeAttributes(inputFile, dictionaries):
    
    changes = {}

    fileHandle = open(inputFile, 'r')
    buildAttributeChanges(fileHandle, changes)
    fileHandle.close()

    versions = {}
    containment = {}
    
    fileHandle = open(inputFile, 'r')
    buildAttributes(fileHandle, changes, dictionaries, versions, containment)
    fileHandle.close()
    
    attributeChangedByRevision = {}
    attributeCreatedByRevision = {}
    attributeModifiedByRevision = {}
    attributeDeletedByRevision = {}
    attributeVersions = {}
    attributeVersionBelongsToClassVersion = {}

    for change in changes.values():
        attribute = dictionaries.getAttributeEntity(change.getAttributeName())
        attributeId = attribute.getIdentifier()
        revisionId = dictionaries.getRevision(change.getRevision())
        attributeChangedByRevision[attributeId] = revisionId
        if change.isCreation():
            attributeCreatedByRevision[attributeId] = revisionId
        if change.isModification():
            attributeModifiedByRevision[attributeId] = revisionId
        if change.isDeletion():
            attributeDeletedByRevision[attributeId] = revisionId
            
    for version in versions.values():
        versionId = version.getIdentifier()
        attributeVersions[versionId] = version
        
    for version in containment.values():
        versionId = version.getIdentifier()
        attributeVersionBelongsToClassVersion[versionId] = version

    changeFile = open("attributeChangedByRevision.txt", 'a')
    creationFile = open("attributeCreatedByRevision.txt", 'a')
    modificationFile = open("attributeModifiedByRevision.txt", 'a')
    deletionFile = open("attributeDeletedByRevision.txt", 'a')
    attributeVersionFile = open("attributeVersions.txt", 'a')
    attributeTypeFile = open("attributeVersionHasClassAsType.txt", 'a')
    attributeVisibilityFile = open("attributeVersionVisibility.txt", 'a')
    containmentFile = open("attributeVersionBelongsToClassVersion.txt", 'a')
    
    indices = attributeChangedByRevision.keys()
    indices.sort()
    for attributeId in indices:
        revisionId = attributeChangedByRevision[attributeId]
        attributeChangedByRevisionInfo = str(attributeId) + "\t" + str(revisionId) + "\n"
        changeFile.write(attributeChangedByRevisionInfo)
    changeFile.close()
    
    indices = attributeCreatedByRevision.keys()
    indices.sort()
    for attributeId in indices:
        revisionId = attributeCreatedByRevision[attributeId]
        attributeCreatedByRevisionInfo = str(attributeId) + "\t" + str(revisionId) + "\n"
        creationFile.write(attributeCreatedByRevisionInfo)
    creationFile.close()
    
    indices = attributeModifiedByRevision.keys()
    indices.sort()
    for attributeId in indices:
        revisionId = attributeModifiedByRevision[attributeId]
        attributeModifiedByRevisionInfo = str(attributeId) + "\t" + str(revisionId) + "\n"
        modificationFile.write(attributeModifiedByRevisionInfo)
    modificationFile.close()
    
    indices = attributeDeletedByRevision.keys()
    indices.sort()
    for attributeId in indices:
        revisionId = attributeDeletedByRevision[attributeId]
        attributeDeletedByRevisionInfo = str(attributeId) + "\t" + str(revisionId) + "\n"
        deletionFile.write(attributeDeletedByRevisionInfo)
    deletionFile.close()
    
    indices = attributeVersions.keys()
    indices.sort()
    for identifier in indices:
        version = attributeVersions[identifier]
        attributeId = version.getAttributeIdentifier()
        revisionId = dictionaries.getRevision(version.getRevision())
        attributeVersionInfo = str(identifier) + "\t" + str(attributeId) + \
                               "\t" + str(revisionId) + "\n"
        attributeVersionFile.write(attributeVersionInfo)
        typeClassId = version.getDeclaredClassIdentifier()
        if not (typeClassId is None):
            typeClassInfo = str(identifier) + "\t" + str(typeClassId) + "\n"
            attributeTypeFile.write(typeClassInfo) 
        visibility = version.getAccessControlQualifier()
        if visibility != "":
            visibilityInfo = str(identifier) + "\t\"" + visibility + "\"\n"
            attributeVisibilityFile.write(visibilityInfo)
    attributeVersionFile.close()
    attributeTypeFile.close()
    attributeVisibilityFile.close()
            
    indices = attributeVersionBelongsToClassVersion.keys()
    indices.sort()
    for identifier in indices:
        version = attributeVersionBelongsToClassVersion[identifier]
        classVersion = version.getClassVersion()
        classVersionId = classVersion.getIdentifier()
        containmentInfo = str(identifier) + "\t" + str(classVersionId) + "\n"
        containmentFile.write(containmentInfo)
    containmentFile.close()

    return EX_OK

def writeAttributeEntities(dictionaries):
    
    attributes = {}
    
    for uniqueAttributeName in dictionaries.attributeDict:
        attribute = dictionaries.getAttributeEntity(uniqueAttributeName)
        attributes[attribute.getIdentifier()] = attribute
        
    attributesFile = open("attributesWithIDs.txt", 'w')
    attributeContainmentFile = open("attributeBelongsToClass.txt", 'w')
    
    indices = attributes.keys()
    indices.sort()
    for identifier in indices:
        attribute = attributes[identifier]
        attributeInfo = str(identifier) + "\t" + attribute.getUniqueName() + "\n"
        attributesFile.write(attributeInfo)
        containmentInfo = str(identifier) + "\t" + str(attribute.getClassIdentifier()) + "\n"
        attributeContainmentFile.write(containmentInfo)
        
    attributesFile.close()
    attributeContainmentFile.close()
    
    return EX_OK
