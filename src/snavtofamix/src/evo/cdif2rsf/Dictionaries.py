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

class Dictionaries:
    def __init__(self):
        self.transactionDict = {}
        self.revisionDict = {}
        self.classDict = {}
        self.methodDict = {}
        self.functionDict = {}
        self.attributeDict = {}
        self.globalVariableDict = {}
        
    def getRevision(self, revisionName):
        if revisionName in self.revisionDict:
            return self.revisionDict[revisionName]
        else:
            return None
        
    def storeClassVersion(self, className, classId, classVersion):
        if className in self.classDict:
            self.classDict[className].setLatestVersion(classVersion)
        else:
            self.classDict[className] = EntityHolder(classId, classVersion)
        
    def getClassId(self, className):
        if className in self.classDict:
            return self.classDict[className].getEntity()
        else:
            return None
        
    def getLatestClassVersion(self, className):
        if className in self.classDict:
            return self.classDict[className].getLatestVersion()
        else:
            return None
        
    def storeMethodVersion(self, methodName, methodEntity, methodVersion):
        if methodName in self.methodDict:
            self.methodDict[methodName].setLatestVersion(methodVersion)
        else:
            self.methodDict[methodName] = EntityHolder(methodEntity, methodVersion)
        
    def getMethodEntity(self, methodName):
        if methodName in self.methodDict:
            return self.methodDict[methodName].getEntity()
        else:
            return None
        
    def getLatestMethodVersion(self, methodName):
        if methodName in self.methodDict:
            return self.methodDict[methodName].getLatestVersion()
        else:
            return None

    def storeFunctionVersion(self, functionName, functionEntity, functionVersion):
        if functionName in self.functionDict:
            self.functionDict[functionName].setLatestVersion(functionVersion)
        else:
            self.functionDict[functionName] = EntityHolder(functionEntity, functionVersion)
        
    def getFunctionEntity(self, functionName):
        if functionName in self.functionDict:
            return self.functionDict[functionName].getEntity()
        else:
            return None
        
    def getLatestFunctionVersion(self, functionName):
        if functionName in self.functionDict:
            return self.functionDict[functionName].getLatestVersion()
        else:
            return None
        
    def storeAttributeVersion(self, attributeName, attributeEntity, attributeVersion):
        if attributeName in self.attributeDict:
            self.attributeDict[attributeName].setLatestVersion(attributeVersion)
        else:
            self.attributeDict[attributeName] = EntityHolder(attributeEntity, attributeVersion)
        
    def getAttributeEntity(self, attributeName):
        if attributeName in self.attributeDict:
            return self.attributeDict[attributeName].getEntity()
        else:
            return None
        
    def getLatestAttributeVersion(self, attributeName):
        if attributeName in self.attributeDict:
            return self.attributeDict[attributeName].getLatestVersion()
        else:
            return None
        
    def storeGlobalVariableVersion(self, globalVariableName, globalVariableEntity, globalVariableVersion):
        if globalVariableName in self.globalVariableDict:
            self.globalVariableDict[globalVariableName].setLatestVersion(globalVariableVersion)
        else:
            self.globalVariableDict[globalVariableName] = EntityHolder(globalVariableEntity, globalVariableVersion)
        
    def getGlobalVariableEntity(self, globalVariableName):
        if globalVariableName in self.globalVariableDict:
            return self.globalVariableDict[globalVariableName].getEntity()
        else:
            return None
        
    def getLatestGlobalVariableVersion(self, globalVariableName):
        if globalVariableName in self.globalVariableDict:
            return self.globalVariableDict[globalVariableName].getLatestVersion()
        else:
            return None
        
class EntityHolder:
    def __init__(self, entity, latestVersion):
        self.entity = entity
        self.latestVersion = latestVersion
        
    def getEntity(self):
        return self.entity
    
    def setEntity(self, entity):
        self.entity = entity
        
    def getLatestVersion(self):
        return self.latestVersion
    
    def setLatestVersion(self, latestVersion):
        self.latestVersion = latestVersion
        
class TransactionControl:
    def __init__(self, maxTransactions):
        self.maxTransactions = maxTransactions
        self.latestTime = None
        self.authors = []
        
    def getMaxTransactions(self):
        return self.maxTransactions
    
    def isLimiting(self):
        return (self.maxTransactions > 0)
    
    def getLatestTime(self):
        return self.latestTime
    
    def setLatestTime(self, latestTime):
        self.latestTime = latestTime
        
    def isTimeValid(self, aTime):
        return (not self.isLimiting()) or \
            (self.latestTime is None) or \
            (aTime <= self.latestTime)
            
    def addAuthor(self, author):
        if not (author in self.authors):
            self.authors.append(author)

    def isAuthorValid(self, author):
        return (not self.isLimiting()) or (author in self.authors)
        

