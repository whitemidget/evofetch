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

class RevisionDictionary:
    def __init__(self):
        self.entityDict = {}
        self.commitDict = {}
        self.actionDict = {}
        self.dictByName = {}
        self.dictByTime = {}
        
    def add(self, revisionEntity):
        if (not revisionEntity.isDeletion()) and revisionEntity.getCdifId() == None:
            revisionEntity.setCdifId(requestNewCdifId())
        self.entityDict[revisionEntity.getDbId()] = revisionEntity
        timeKey = (revisionEntity.getCreationTime(), revisionEntity.getDbId())
        self.dictByTime[timeKey] = revisionEntity.getDbId()
     
    def addPrepared(self, revisionEntity):
        self.entityDict[revisionEntity.getCdifId()] = revisionEntity
        self.dictByName[revisionEntity.getUniqueName()] = revisionEntity

    def getEntity(self, dbId):
        return self.entityDict[dbId]

    def addCommit(self, commitEntity):
        self.commitDict[commitEntity.getDbId()] = commitEntity
        
    def getCommit(self, dbId):
        return self.commitDict[dbId]
    
    def addAction(self, actionEntity):
        self.actionDict[actionEntity.getDbId()] = actionEntity
        
    def getAction(self, dbId):
        return self.actionDict[dbId]

        