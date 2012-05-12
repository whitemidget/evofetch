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

class AttributeVersionEntity:
    def __init__(self):
        self.identifier = None
        self.uniqueName = None
        self.classIdentifier = None
        self.attributeIdentifier = None
        self.accessControlQualifier = None
        self.declaredType = None
        self.declaredClassIdentifier = None
        self.hasClassScope = False
        self.revision = None
        self.classVersion = None
        
    def getIdentifier(self):
        return self.identifier
    
    def setIdentifier(self, identifier):
        self.identifier = identifier
        
    def getUniqueName(self):
        return self.uniqueName
    
    def setUniqueName(self, uniqueName):
        self.uniqueName = uniqueName
        
    def getClassIdentifier(self):
        return self.classIdentifier
    
    def setClassIdentifier(self, classIdentifier):
        self.classIdentifier = classIdentifier
        
    def getAttributeIdentifier(self):
        return self.attributeIdentifier
       
    def setAttributeIdentifier(self, attributeIdentifier):
        self.attributeIdentifier = attributeIdentifier
        
    def getAccessControlQualifier(self):
        return self.accessControlQualifier
    
    def setAccessControlQualifier(self, accessControlQualifier):
        self.accessControlQualifier = accessControlQualifier
        
    def getDeclaredType(self):
        return self.declaredType
    
    def setDeclaredType(self, declaredType):
        self.declaredType = declaredType
        
    def getDeclaredClassIdentifier(self):
        return self.declaredClassIdentifier
    
    def setDeclaredClassIdentifier(self, declaredClassIdentifier):
        self.declaredClassIdentifier = declaredClassIdentifier
        
    def hasClassScope(self):
        return self.hasClassScope
    
    def setClassScope(self, hasClassScope):
        self.hasClassScope = hasClassScope
        
    def getRevision(self):
        return self.revision
    
    def setRevision(self, revision):
        self.revision = revision
        
    def getClassVersion(self):
        return self.classVersion
    
    def setClassVersion(self, classVersion):
        self.classVersion = classVersion