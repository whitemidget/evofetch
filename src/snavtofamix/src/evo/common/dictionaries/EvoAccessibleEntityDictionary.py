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

from cplusplus.dictionaries.AccessibleEntityDictionary import AccessibleEntityDictionary

from evo.common.dictionaries.RestrictedByFile import RestrictedByFile
from evo.common.objects.AttributeVersion import AttributeVersion
from evo.common.objects.EvoAttributeReferenceEntity import EvoAttributeReferenceEntity
from evo.common.objects.GlobalVariableVersion import GlobalVariableVersion

class EvoAccessibleEntityDictionary(AccessibleEntityDictionary, RestrictedByFile):
    def __init__(self, fileDict):
        AccessibleEntityDictionary.__init__(self)
        RestrictedByFile.__init__(self, fileDict)
        self.dictBySourceFile = {}
        self.attributeList = []
        self.globalVarList = []
        self.attributeVersionDict = {}
        self.globalVarVersionDict = {}
        self.lastClassScope = False
        self.__clearEntityDictionaries()
        
    def addRef(self, attrRef):
        evoAttrRef = EvoAttributeReferenceEntity()
        evoAttrRef.assignFrom(attrRef)
        evoAttrRef.setClassScope(self.lastClassScope)
        AccessibleEntityDictionary.addRef(self, evoAttrRef)
        sourceFile = evoAttrRef.getSourceFile()
        name = evoAttrRef.getName()
        if not (sourceFile in self.dictBySourceFile):
            self.dictBySourceFile[sourceFile] = []
        refList = self.dictBySourceFile[sourceFile]
        if not (name in refList):
            refList.append(name)
        uniqueName = self.__getUniqueName(evoAttrRef)
        if evoAttrRef.getOwnerName() == "":         
            if not (uniqueName in self.globalVarList):
                self.globalVarList.append(uniqueName)
        else:
            if not (uniqueName in self.attributeList):
                self.attributeList.append(uniqueName)
        self.addingRef = evoAttrRef
    
    def addAttributeVersion(self, version, reference, classDict):
        self.attributeVersionDict[version.getAttributeName()] = version
        classDict.addClassChange(reference.getOwnerName(), version.getRevision())
        
    def addGlobalVariableVersion(self, version):
        self.globalVarVersionDict[version.getGlobalVariableName()] = version
        
    def mergeInto(self, destinationDict, classDict, backup):
        self.__clearEntityDictionaries()
        if not (self.fileDict is None):
            fileList = self.fileDict.getFileList()
            for sourceFile in fileList:
                lookForFile = sourceFile[1:]
                if lookForFile in destinationDict.dictBySourceFile:
                    for name in destinationDict.dictBySourceFile[lookForFile]:
                        refList = destinationDict.refDict[name]
                        adjustedRefList = []
                        for ref in refList:
                            if ref.getSourceFile() != lookForFile:
                                adjustedRefList.append(ref)
                            else:
                                if ref.getOwnerName() == "":
                                    self.__addEntity(ref, self.priorGlobalVars)
                                else:
                                    self.__addEntity(ref, self.priorAttributes)
                        if len(adjustedRefList) == 0:
                            del destinationDict.refDict[name]
                        else:
                            destinationDict.refDict[name] = adjustedRefList
                    del destinationDict.dictBySourceFile[lookForFile]
        for name in self.refDict:
            for ref in self.refDict[name]:
                sourceFile = ref.getSourceFile()
                lookForFile = '/' + sourceFile
                if ref.getOwnerName() == "":
                    self.__addEntity(ref, self.currentGlobalVars)
                else:
                    self.__addEntity(ref, self.currentAttributes)
                destinationDict.addRef(ref)
        self.__findAttributeVersions(classDict)
        self.__findGlobalVariableVersions()
        
    def removeSourceFile(self, revision, sourceFile, dictForVersions, classDictForVersions):
        self.__clearEntityDictionaries()
        lookForFile = sourceFile[1:]
        if lookForFile in self.dictBySourceFile:
            for name in self.dictBySourceFile[lookForFile]:
                refList = self.refDict[name]
                adjustedRefList = []
                for ref in refList:
                    if ref.getSourceFile() != lookForFile:
                        adjustedRefList.append(ref)
                    else:
                        if ref.getOwnerName() == "":
                            self.__addEntity(ref, self.priorGlobalVars)
                        else:
                            self.__addEntity(ref, self.priorAttributes)
                if len(adjustedRefList) == 0:
                    del self.refDict[name]
                else:
                    self.refDict[name] = adjustedRefList
            del self.dictBySourceFile[lookForFile]

            if lookForFile in self.priorAttributes:
                for refName in self.priorAttributes[lookForFile]:
                    oldEntity = self.priorAttributes[lookForFile][refName]
                    version = AttributeVersion(revision, refName)
                    version.setDeletion(True)
                    dictForVersions.addAttributeVersion(version, oldEntity, classDictForVersions)
    
            if lookForFile in self.priorGlobalVars:
                for refName in self.priorGlobalVars[lookForFile]:
                    version = GlobalVariableVersion(revision, refName)
                    version.setDeletion(True)
                    dictForVersions.addGlobalVariableVersion(version)
        self.__clearEntityDictionaries()

    def getInterestedFields(self):
        return ('hasClassScope',)
            
    def decorateWriterOutput(self, output):
        self.lastClassScope = ("-TRUE-" in output)
        return output

    def __clearEntityDictionaries(self):
        self.priorAttributes = {}
        self.priorGlobalVars = {}
        self.currentAttributes = {}
        self.currentGlobalVars = {}
        
    def __addEntity(self, reference, dictionary):
        uniqueName = self.__getUniqueName(reference)
        sourceFile = reference.getSourceFile()
        if not (sourceFile in dictionary):
            dictionary[sourceFile] = {}
        dictionary[sourceFile][uniqueName] = reference
        
    def __findAttributeVersions(self, classDict):
        for sourceFile in self.priorAttributes:
            lookForFile = '/' + sourceFile
            revision = self.fileDict.getRevisionForFile(lookForFile)
            if sourceFile in self.currentAttributes:
                for refName in self.priorAttributes[sourceFile]:
                    oldEntity = self.priorAttributes[sourceFile][refName]
                    if not (refName in self.currentAttributes[sourceFile]):
                        version = AttributeVersion(revision, refName)
                        version.setDeletion(True)
                        self.addAttributeVersion(version, oldEntity, classDict)
                    else:
                        newEntity = self.currentAttributes[sourceFile][refName]
                        if self.__isEntityDifferent(sourceFile, oldEntity, newEntity):
                            version = AttributeVersion(revision, refName)
                            version.setModification(True)
                            self.addAttributeVersion(version, newEntity, classDict)
                for refName in self.currentAttributes[sourceFile]:
                    if not (refName in self.priorAttributes[sourceFile]):
                        newEntity = self.currentAttributes[sourceFile][refName]
                        version = AttributeVersion(revision, refName)
                        version.setCreation(True)
                        self.addAttributeVersion(version, newEntity, classDict)
            else:
                for refName in self.priorAttributes[sourceFile]:
                    oldEntity = self.priorAttributes[sourceFile][refName]
                    version = AttributeVersion(revision, refName)
                    version.setDeletion(True)
                    self.addAttributeVersion(version, oldEntity, classDict)
        for sourceFile in self.currentAttributes:
            if not (sourceFile in self.priorAttributes):
                lookForFile = '/' + sourceFile
                revision = self.fileDict.getRevisionForFile(lookForFile)
                for refName in self.currentAttributes[sourceFile]:
                    newEntity = self.currentAttributes[sourceFile][refName]
                    version = AttributeVersion(revision, refName)
                    version.setCreation(True)
                    self.addAttributeVersion(version, newEntity, classDict)
                    
    def __findGlobalVariableVersions(self):
        for sourceFile in self.priorGlobalVars:
            lookForFile = '/' + sourceFile
            revision = self.fileDict.getRevisionForFile(lookForFile)
            if sourceFile in self.currentGlobalVars:
                for refName in self.priorGlobalVars[sourceFile]:
                    oldEntity = self.priorGlobalVars[sourceFile][refName]
                    if not (refName in self.currentGlobalVars[sourceFile]):
                        version = GlobalVariableVersion(revision, refName)
                        version.setDeletion(True)
                        self.addGlobalVariableVersion(version)
                    else:
                        newEntity = self.currentGlobalVars[sourceFile][refName]
                        if self.__isEntityDifferent(sourceFile, oldEntity, newEntity):
                            version = GlobalVariableVersion(revision, refName)
                            version.setModification(True)
                            self.addGlobalVariableVersion(version)
                for refName in self.currentGlobalVars[sourceFile]:
                    if not (refName in self.priorGlobalVars[sourceFile]):
                        version = GlobalVariableVersion(revision, refName)
                        version.setCreation(True)
                        self.addGlobalVariableVersion(version)
            else:
                for refName in self.priorGlobalVars[sourceFile]:
                    version = GlobalVariableVersion(revision, refName)
                    version.setDeletion(True)
                    self.addGlobalVariableVersion(version)
        for sourceFile in self.currentGlobalVars:
            if not (sourceFile in self.priorGlobalVars):
                lookForFile = '/' + sourceFile
                revision = self.fileDict.getRevisionForFile(lookForFile)
                for refName in self.currentGlobalVars[sourceFile]:
                    version = GlobalVariableVersion(revision, refName)
                    version.setCreation(True)
                    self.addGlobalVariableVersion(version)
                    
    def __isEntityDifferent(self, sourceFile, oldEntity, newEntity):
        oldType = oldEntity.getTypeReference().getReferencedName()
        newType = newEntity.getTypeReference().getReferencedName()
        if oldType != newType:
            return True
        elif oldEntity.getOwnerName() == "":
            return False
        elif oldEntity.hasClassScope() != newEntity.hasClassScope():
            return True
        elif oldEntity.getModifiers() != newEntity.getModifiers():
            return True
        else:
            return False
                                    
    def __getUniqueName(self, reference):
        owner = reference.getOwnerName()
        if owner == "":
            return reference.getName()
        else:
            return owner + '.' + reference.getName()
