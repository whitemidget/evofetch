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

class GlobalVariableVersionEntity:
    def __init__(self):
        self.identifier = None
        self.uniqueName = None
        self.globalVariableIdentifier = None
        self.declaredType = None
        self.declaredClassIdentifier = None
        self.revision = None
        
    def getIdentifier(self):
        return self.identifier
    
    def setIdentifier(self, identifier):
        self.identifier = identifier
        
    def getUniqueName(self):
        return self.uniqueName
    
    def setUniqueName(self, uniqueName):
        self.uniqueName = uniqueName
        
    def getGlobalVariableIdentifier(self):
        return self.globalVariableIdentifier
       
    def setGlobalVariableIdentifier(self, globalVariableIdentifier):
        self.globalVariableIdentifier = globalVariableIdentifier
        
    def getDeclaredType(self):
        return self.declaredType
    
    def setDeclaredType(self, declaredType):
        self.declaredType = declaredType
        
    def getDeclaredClassIdentifier(self):
        return self.declaredClassIdentifier
    
    def setDeclaredClassIdentifier(self, declaredClassIdentifier):
        self.declaredClassIdentifier = declaredClassIdentifier
        
    def getRevision(self):
        return self.revision
    
    def setRevision(self, revision):
        self.revision = revision