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

class EntityVersion:
    def __init__(self, revision):
        self.revision = revision
        self.creation = False
        self.deletion = False
        self.modification = False
        
    def getRevision(self):
        return self.revision
        
    def isCreation(self):
        return self.creation
    
    def setCreation(self, creation):
        self.creation = creation
        
    def isDeletion(self):
        return self.deletion
    
    def setDeletion(self, deletion):
        self.deletion = deletion
        
    def isModification(self):
        return self.modification
    
    def setModification(self, modification):
        self.modification = modification
