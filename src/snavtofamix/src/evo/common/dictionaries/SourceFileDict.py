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

from common.output.cdifWriter import requestNewCdifId

class SourceFileDictionary:
    def __init__(self):
        self.entityDict = {}
        self.dictByUniqueName = {}
        
    def addNew(self, sourceFileEntity):
        dbId = sourceFileEntity.getDbId()
        if not (dbId in self.entityDict):
            self.entityDict[dbId] = []
        self.entityDict[dbId].append(sourceFileEntity)
        
    def addCompleted(self, sourceFileEntity):
        if not (sourceFileEntity.getCreationTime() is None):
            uniqueName = sourceFileEntity.getUniqueName()
            if not (uniqueName in self.dictByUniqueName):
                self.dictByUniqueName[uniqueName] = sourceFileEntity
                if sourceFileEntity.getCdifId() == None:
                    sourceFileEntity.setCdifId(requestNewCdifId())
                
    def addPrepared(self, sourceFileEntity):
        self.entityDict[sourceFileEntity.getCdifId()] = sourceFileEntity
        
    def cloneEntity(self, sourceFileEntity):
        anotherEntity = sourceFileEntity.clone()
        self.addNew(anotherEntity)
        return anotherEntity
    
    def getEntity(self, dbId, commitId):
        entityList = self.entityDict[dbId]
        result = None
        for entity in entityList:
            entityCommit = entity.getCreationCommitId()
            if (entityCommit is None) or (commitId is None) or entityCommit <= commitId:
                result = entity
        return result
    

        