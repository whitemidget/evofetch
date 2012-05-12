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

class InheritanceEntity:
    def __init__(self):
        self.identifier = None
        self.subclassName = None
        self.subclassVersionIdentifier = None
        self.superclassName = None
        self.superclassIdentifier = None
        
    def getIdentifier(self):
        return self.identifier
    
    def setIdentifier(self, identifier):
        self.identifier = identifier
        
    def getSubclassName(self):
        return self.subclassName
    
    def setSubclassName(self, subclassName):
        self.subclassName = subclassName
        
    def getSubclassVersionIdentifier(self):
        return self.subclassVersionIdentifier
    
    def setSubclassVersionIdentifier(self, subclassVersionIdentifier):
        self.subclassVersionIdentifier = subclassVersionIdentifier
        
    def getSuperclassName(self):
        return self.subclassName
    
    def setSuperclassName(self, superclassName):
        self.superclassName = superclassName
        
    def getSuperclassIdentifier(self):
        return self.superclassIdentifier
    
    def setSuperclassIdentifier(self, superclassIdentifier):
        self.superclassIdentifier = superclassIdentifier