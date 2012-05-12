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

class AuthorEntity:
    def __init__(self):
        self.cdifId = None
        self.dbId = None
        self.identifier = None
        self.fullName = None
        self.emailAddress = None
        
    def __eq__(self, other):
        return other.getIdentifier() == self.getIdentifier()
    
    def getCdifId(self):
        return self.cdifId
    
    def setCdifId(self, cdifId):
        self.cdifId = cdifId
    
    def getDbId(self):
        return self.dbId
    
    def setDbId(self, dbId):
        self.dbId = dbId
    
    def getIdentifier(self):
        return self.identifier    

    def setIdentifier(self, identifier):
        self.identifier = identifier
        
    def getFullName(self):
        return self.fullName
    
    def setFullName(self, fullName):
        self.fullName = fullName
        
    def getEmailAddress(self):
        return self.emailAddress
    
    def setEmailAddress(self, emailAddress):
        self.emailAddress = emailAddress
    
