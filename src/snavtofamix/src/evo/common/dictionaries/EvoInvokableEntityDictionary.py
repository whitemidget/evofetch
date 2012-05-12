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

from cplusplus.dictionaries.InvokeableEntityDictionary import InvokeableEntityDictionary

from evo.common.dictionaries.RestrictedByFile import RestrictedByFile
from evo.common.objects.FunctionVersion import FunctionVersion
from evo.common.objects.MethodVersion import MethodVersion
from evo.common.processing.Differencer import performLDiff

class EvoInvokableEntityDictionary(InvokeableEntityDictionary, RestrictedByFile):
    def __init__(self, fileDict):
        InvokeableEntityDictionary.__init__(self)
        RestrictedByFile.__init__(self, fileDict)
        self.dictBySourceFile = {}
        self.methodList = []
        self.functionList = []
        self.methodVersionDict = {}
        self.functionVersionDict = {}
        self.__clearEntityDictionaries()

    def addMultiLocReference(self, reference):
        isAdded = InvokeableEntityDictionary.addMultiLocReference(self, reference)
        if isAdded:
            sourceFiles = reference.getLocation().getSourceFiles()
            name = reference.getName()
            signature = reference.getFormalParameters()
            for sourceFile in sourceFiles:
                if not (sourceFile in self.dictBySourceFile):
                    self.dictBySourceFile[sourceFile] = {}
                names = self.dictBySourceFile[sourceFile]
                if not (name in names):
                    self.dictBySourceFile[sourceFile][name] = []
                if not (signature in self.dictBySourceFile[sourceFile][name]):
                    self.dictBySourceFile[sourceFile][name].append(signature)
            uniqueName = self.__getUniqueName(reference)
            if reference.getOwnerName() != "":
                if not (uniqueName in self.methodList):
                    self.methodList.append(uniqueName)
            else:
                if not (uniqueName in self.functionList):
                    self.functionList.append(uniqueName)

    def addMethodVersion(self, version, reference, classDict):
        self.methodVersionDict[version.getMethodName()] = version
        classDict.addClassChange(reference.getOwnerName(), version.getRevision())
    
    def addFunctionVersion(self, version):
        self.functionVersionDict[version.getFunctionName()] = version
                
    def retrieveAllMultiLocReferences(self):
        allReferences = InvokeableEntityDictionary.retrieveAllMultiLocReferences(self)
        return self.__filterReferences(allReferences)
    
    def retrieveMultiLocReferencesFor(self, classNameOrEmpty, nameOfMethodOrFunction):
        allReferences = InvokeableEntityDictionary.retrieveMultiLocReferencesFor(self, classNameOrEmpty, nameOfMethodOrFunction)
        return self.__filterReferences(allReferences)
    
    def mergeInto(self, destinationDict, classDict, backup):
        self.__clearEntityDictionaries()
        if not (self.fileDict is None):
            fileList = self.fileDict.getFileList()
            for sourceFile in fileList:
                lookForFile = sourceFile[1:]
                if lookForFile in destinationDict.dictBySourceFile:
                    for name in destinationDict.dictBySourceFile[lookForFile]:
                        for signature in destinationDict.dictBySourceFile[lookForFile][name]:
                            refList = destinationDict.dict[name][signature]
                            adjustedRefList = []
                            for ref in refList:
                                sources = ref.getLocation().getSourceFiles()
                                if not (lookForFile in sources):
                                    adjustedRefList.append(ref)
                                else:
                                    declarations = ref.getLocation().getDeclarationLocations()
                                    definitions = ref.getLocation().getDefinitionLocations()
                                    deleteList = []
                                    for loc in declarations:
                                        if loc.getSourceFile() == lookForFile:
                                            deleteList.append(loc)
                                    for loc in deleteList:
                                        index = declarations.index(loc)
                                        del declarations[index]
                                    deleteList = []
                                    for loc in definitions:
                                        if loc.getSourceFile() == lookForFile:
                                            deleteList.append(loc)
                                    for loc in deleteList:
                                        index = definitions.index(loc)
                                        if ref.getOwnerName() == "":
                                            self.__addEntity(ref, definitions[index], self.priorFunctions)
                                        else:
                                            self.__addEntity(ref, definitions[index], self.priorMethods)
                                        del definitions[index]
                                    if len(declarations) > 0 or len(definitions) > 0:
                                        adjustedRefList.append(ref)                                    
                            if len(adjustedRefList) == 0:
                                del destinationDict.dict[name][signature]
                            else:
                                destinationDict.dict[name][signature] = adjustedRefList
                        if len(destinationDict.dict[name]) == 0:
                            del destinationDict.dict[name]
                    del destinationDict.dictBySourceFile[lookForFile]
        for name in self.dict:
            for signature in self.dict[name]:
                for ref in self.dict[name][signature]:
                    locs = ref.getLocation().getLocations()
                    for location in locs:
                        if ref.getOwnerName() == "":
                            self.__addEntity(ref, location, self.currentFunctions)
                        else:
                            self.__addEntity(ref, location, self.currentMethods)
                    destinationDict.addMultiLocReference(ref)
        self.__findMethodVersions(classDict, backup)
        self.__findFunctionVersions(backup)
                    
    def removeSourceFile(self, revision, sourceFile, dictForVersions, classDictForVersions):
        self.__clearEntityDictionaries()
        lookForFile = sourceFile[1:]
        if lookForFile in self.dictBySourceFile:
            for name in self.dictBySourceFile[lookForFile]:
                for signature in self.dictBySourceFile[lookForFile][name]:
                    refList = self.dict[name][signature]
                    adjustedRefList = []
                    for ref in refList:
                        sources = ref.getLocation().getSourceFiles()
                        if not (lookForFile in sources):
                            adjustedRefList.append(ref)
                        else:
                            declarations = ref.getLocation().getDeclarationLocations()
                            definitions = ref.getLocation().getDefinitionLocations()
                            deleteList = []
                            for loc in declarations:
                                if loc.getSourceFile() == lookForFile:
                                    deleteList.append(loc)
                            for loc in deleteList:
                                index = declarations.index(loc)
                                del declarations[index]
                            deleteList = []
                            for loc in definitions:
                                if loc.getSourceFile() == lookForFile:
                                    deleteList.append(loc)
                            for loc in deleteList:
                                index = definitions.index(loc)
                                if ref.getOwnerName() == "":
                                    self.__addEntity(ref, definitions[index], self.priorFunctions)
                                else:
                                    self.__addEntity(ref, definitions[index], self.priorMethods)
                                del definitions[index]
                            if len(declarations) > 0 or len(definitions) > 0:
                                adjustedRefList.append(ref)                                    
                    if len(adjustedRefList) == 0:
                        del self.dict[name][signature]
                    else:
                        self.dict[name][signature] = adjustedRefList
                if len(self.dict[name]) == 0:
                    del self.dict[name]
            del self.dictBySourceFile[lookForFile]

            if lookForFile in self.priorMethods:
                for refName in self.priorMethods[lookForFile]:
                    oldHolder = self.priorMethods[lookForFile][refName]
                    oldEntity = oldHolder.getReference()
                    version = MethodVersion(revision, refName)
                    version.setDeletion(True)
                    dictForVersions.addMethodVersion(version, oldEntity, classDictForVersions)
    
            if lookForFile in self.priorFunctions:
                for refName in self.priorFunctions[lookForFile]:
                    version = FunctionVersion(revision, refName)
                    version.setDeletion(True)
                    dictForVersions.addFunctionVersion(version)
        self.__clearEntityDictionaries()
   
    def __clearEntityDictionaries(self):
        self.priorMethods = {}
        self.priorFunctions = {}
        self.currentMethods = {}
        self.currentFunctions = {}
        
    def __addEntity(self, reference, location, dictionary):
        uniqueName = self.__getUniqueName(reference)
        sourceFile = location.getSourceFile()
        if not (sourceFile in dictionary):
            dictionary[sourceFile] = {}
        locationHolder = LocationHolder(reference, location)
        dictionary[sourceFile][uniqueName] = locationHolder
        
    def __findMethodVersions(self, classDict, backup):
        for sourceFile in self.priorMethods:
            lookForFile = '/' + sourceFile
            revision = self.fileDict.getRevisionForFile(lookForFile)
            if sourceFile in self.currentMethods:
                for refName in self.priorMethods[sourceFile]:
                    oldHolder = self.priorMethods[sourceFile][refName]
                    oldEntity = oldHolder.getReference()
                    oldLocation = oldHolder.getLocation()
                    if not (refName in self.currentMethods[sourceFile]):
                        version = MethodVersion(revision, refName)
                        version.setDeletion(True)
                        self.addMethodVersion(version, oldEntity, classDict)
                    else:
                        newHolder = self.currentMethods[sourceFile][refName]
                        newEntity = newHolder.getReference()
                        newLocation = newHolder.getLocation()
                        if self.__isEntityDifferent(sourceFile, oldEntity, oldLocation, newEntity, newLocation, backup):
                            version = MethodVersion(revision, refName)
                            version.setModification(True)
                            self.addMethodVersion(version, newEntity, classDict)
                    for refName in self.currentMethods[sourceFile]:
                        if not (refName in self.priorMethods[sourceFile]):
                            newHolder = self.currentMethods[sourceFile][refName]
                            newEntity = newHolder.getReference()
                            version = MethodVersion(revision, refName)
                            version.setCreation(True)
                            self.addMethodVersion(version, newEntity, classDict)
            else:
                for refName in self.priorMethods[sourceFile]:
                    oldHolder = self.priorMethods[sourceFile][refName]
                    oldEntity = oldHolder.getReference()
                    version = MethodVersion(revision, refName)
                    version.setDeletion(True)
                    self.addMethodVersion(version, oldEntity, classDict)
        for sourceFile in self.currentMethods:
            if not (sourceFile in self.priorMethods):
                lookForFile = '/' + sourceFile
                revision = self.fileDict.getRevisionForFile(lookForFile)
                for refName in self.currentMethods[sourceFile]:
                    newHolder = self.currentMethods[sourceFile][refName]
                    newEntity = newHolder.getReference()
                    version = MethodVersion(revision, refName)
                    version.setCreation(True)
                    self.addMethodVersion(version, newEntity, classDict)
                    
    def __findFunctionVersions(self, backup):
        for sourceFile in self.priorFunctions:
            lookForFile = '/' + sourceFile
            revision = self.fileDict.getRevisionForFile(lookForFile)
            if sourceFile in self.currentFunctions:
                for refName in self.priorFunctions[sourceFile]:
                    oldHolder = self.priorFunctions[sourceFile][refName]
                    oldEntity = oldHolder.getReference()
                    oldLocation = oldHolder.getLocation()
                    if not (refName in self.currentFunctions[sourceFile]):
                        version = FunctionVersion(revision, refName)
                        version.setDeletion(True)
                        self.addFunctionVersion(version)
                    else:
                        newHolder = self.currentFunctions[sourceFile][refName]
                        newEntity = newHolder.getReference()
                        newLocation = newHolder.getLocation()
                        if self.__isEntityDifferent(sourceFile, oldEntity, oldLocation, newEntity, newLocation, backup):
                            version = FunctionVersion(revision, refName)
                            version.setModification(True)
                            self.addFunctionVersion(version)
                for refName in self.currentFunctions[sourceFile]:
                    if not (refName in self.priorFunctions[sourceFile]):
                        version = FunctionVersion(revision, refName)
                        version.setCreation(True)
                        self.addFunctionVersion(version)
            else:
                for refName in self.priorFunctions[sourceFile]:
                    version = FunctionVersion(revision, refName)
                    version.setDeletion(True)
                    self.addFunctionVersion(version)
        for sourceFile in self.currentFunctions:
            if not (sourceFile in self.priorFunctions):
                lookForFile = '/' + sourceFile
                revision = self.fileDict.getRevisionForFile(lookForFile)
                for refName in self.currentFunctions[sourceFile]:
                    version = FunctionVersion(revision, refName)
                    version.setCreation(True)
                    self.addFunctionVersion(version)
                    
    def __isEntityDifferent(self, sourceFile, oldEntity, oldLocation, newEntity, newLocation, backup):
        oldType = oldEntity.getTypeReference().getReferencedName()
        newType = newEntity.getTypeReference().getReferencedName()
        if oldType != newType:
            return True
        elif oldEntity.getOwnerName() == "":
            if (oldLocation is None) or (newLocation is None):
                return False
            else:
                return performLDiff(backup, oldLocation, newLocation)
        elif oldEntity.isAbstract() != newEntity.isAbstract():
            return True
        elif oldEntity.getClassScope() != newEntity.getClassScope():
            return True
        elif oldEntity.getModifiers() != newEntity.getModifiers():
            return True
        else: 
            if (oldLocation is None) or (newLocation is None):
                return False
            else:
                return performLDiff(backup, oldLocation, newLocation)
                                    
    def __getUniqueName(self, reference):
        if reference.getOwnerName() != "":
            parentRef = reference.getParentReference()
            return parentRef.getReferencedName() + "." + reference.getName() + reference.getFormalParameters()
        else:
            return reference.getUniqueName()

    def __filterReferences(self, references):
        if self.restricting:
            filteredReferences = []
            for reference in references:
                sourceFiles = reference.getLocation().getSourceFiles()
                if self.containsPermittedFile(sourceFiles):
                    filteredReferences.append(reference)
            return filteredReferences
        else:
            return references
        
class LocationHolder:
    def __init__(self, reference, location):
        self.reference = reference
        self.location = location
        
    def getReference(self):
        return self.reference
    
    def getLocation(self):
        return self.location

