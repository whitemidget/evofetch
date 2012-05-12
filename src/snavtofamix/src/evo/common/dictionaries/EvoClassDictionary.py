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

from cplusplus.dictionaries.oldArch.ClassDictionary import ClassDictionary, getUniqueName

from cplusplus.infrastructure.QualifiedNameHelperFunctions import getNonQualifiedName

from evo.common.dictionaries.RestrictedByFile import RestrictedByFile

from evo.common.objects.ClassVersion import ClassVersion

class EvoClassDictionary(ClassDictionary, RestrictedByFile):
    def __init__(self, fileDict):
        ClassDictionary.__init__(self)
        RestrictedByFile.__init__(self, fileDict)
        self.dictBySourceFile = {}
        self.classList = []
        self.versionDict = {}
        self.__clearEntityDictionaries()
        
    def add(self, className, sourceFile, lineNr, classData):
        isAdded = ClassDictionary.add(self, className, sourceFile, lineNr, classData)
        
        if isAdded:
            nonQualifiedClassName = getNonQualifiedName(className)
            if not (sourceFile in self.dictBySourceFile):
                self.dictBySourceFile[sourceFile] = []
            fileClassList = self.dictBySourceFile[sourceFile]
            if not (nonQualifiedClassName in fileClassList):
                fileClassList.append(nonQualifiedClassName)
            uniqueClassName = getUniqueName(classData)
            self.classList.append(uniqueClassName)             

        return isAdded

    def containsClass(self, className, sourceFile, namespaceName):
        return (not self.isFilePermitted(sourceFile)) or \
            ClassDictionary.containsClass(self, className, sourceFile, namespaceName)
            
    def addVersion(self, version):
        self.versionDict[version.getClassName()] = version
        
    def addClassChange(self, className, revision):
        if not (className in self.versionDict):
            version = ClassVersion(revision, className)
            version.setModification(True)
            self.addVersion(version) 
    
    def mergeInto(self, destinationDict):
        self.__clearEntityDictionaries()
        if not (self.fileDict is None):
            fileList = self.fileDict.getFileList()
            for sourceFile in fileList:
                lookForFile = sourceFile[1:]
                if lookForFile in destinationDict.dictBySourceFile:
                    for containedClass in destinationDict.dictBySourceFile[lookForFile]:
                        for lineNr in destinationDict.dict[containedClass][lookForFile]:
                            classData = destinationDict.dict[containedClass][lookForFile][lineNr]
                            uniqueClassName = getUniqueName(classData)
                            self.__addClass(lookForFile, uniqueClassName, self.priorClasses)
                        del destinationDict.dict[containedClass][lookForFile]
                    del destinationDict.dictBySourceFile[lookForFile]
        for className in self.dict:
            for sourceFile in self.dict[className]:
                for lineNr in self.dict[className][sourceFile]:
                    classData = self.dict[className][sourceFile][lineNr]
                    uniqueClassName = getUniqueName(classData)
                    self.__addClass(sourceFile, uniqueClassName, self.currentClasses)
                    destinationDict.add(className, sourceFile, lineNr, classData)    
        self.__findClassVersions()                            
    
    def removeSourceFile(self, revision, sourceFile, dictForVersions):
        self.__clearEntityDictionaries()
        lookForFile = sourceFile[1:]
        if lookForFile in self.dictBySourceFile:
            for containedClass in self.dictBySourceFile[lookForFile]:
                for lineNr in self.dict[containedClass][lookForFile]:
                    classData = self.dict[containedClass][lookForFile][lineNr]
                    uniqueClassName = getUniqueName(classData)
                    self.__addClass(lookForFile, uniqueClassName, self.priorClasses)
                del self.dict[containedClass][lookForFile]
            del self.dictBySourceFile[lookForFile]
        
            classList = self.priorClasses[lookForFile]
            for uniqueClassName in classList:
                version = ClassVersion(revision, uniqueClassName)
                version.setDeletion(True)
                dictForVersions.addVersion(version)
        self.__clearEntityDictionaries()
    
    def __clearEntityDictionaries(self):
        self.priorClasses = {}
        self.currentClasses = {}
    
    def __addClass(self, sourceFile, uniqueClassName, dictionary):
        if not sourceFile in dictionary:
            dictionary[sourceFile] = []
        classList = dictionary[sourceFile]
        if not uniqueClassName in classList:
            classList.append(uniqueClassName)

    def __findClassVersions(self):
        for sourceFile in self.priorClasses:
            lookForFile = '/' + sourceFile
            revision = self.fileDict.getRevisionForFile(lookForFile)
            if sourceFile in self.currentClasses:
                for uniqueClassName in self.priorClasses[sourceFile]:
                    if not (uniqueClassName in self.currentClasses[sourceFile]):
                        version = ClassVersion(revision, uniqueClassName)
                        version.setDeletion(True)
                        self.addVersion(version)
                for uniqueClassName in self.currentClasses[sourceFile]:
                    if not (uniqueClassName in self.priorClasses[sourceFile]):
                        version = ClassVersion(revision, uniqueClassName)
                        version.setCreation(True)
                        self.addVersion(version)
            else:
                for uniqueClassName in self.priorClasses[sourceFile]:
                    version = ClassVersion(revision, uniqueClassName)
                    version.setDeletion(True)
                    self.addVersion(version)
        for sourceFile in self.currentClasses:
            if not (sourceFile in self.priorClasses):
                lookForFile = '/' + sourceFile
                revision = self.fileDict.getRevisionForFile(lookForFile)
                for uniqueClassName in self.currentClasses[sourceFile]:
                    version = ClassVersion(revision, uniqueClassName)
                    version.setCreation(True)
                    self.addVersion(version)
