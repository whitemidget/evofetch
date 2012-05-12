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

class ReleaseEntity:
    def __init__(self):
        self.cdifId = None
        self.dbId = None
        self.name = None
        self.creationTime = None
        
    def __eq__(self, other):
        return other.getUniqueName() == self.getUniqueName()
    
    def getCdifId(self):
        return self.cdifId
    
    def setCdifId(self, cdifId):
        self.cdifId = cdifId
    
    def getDbId(self):
        return self.dbId
    
    def setDbId(self, dbId):
        self.dbId = dbId
    
    def getName(self):
        return self.name    

    def setName(self, name):
        self.name = name
        
    def getCreationTime(self):
        return self.creationTime
    
    def setCreationTime(self, creationTime):
        self.creationTime = creationTime
        
    def getUniqueName(self):
        return self.name
    
