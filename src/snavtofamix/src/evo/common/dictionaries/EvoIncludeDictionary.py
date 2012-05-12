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

from cplusplus.dictionaries.includeDict import IncludeDictionary

from evo.common.dictionaries.RestrictedByFile import RestrictedByFile

class EvoIncludeDictionary(IncludeDictionary, RestrictedByFile):
    def __init__(self, fileDict):
        IncludeDictionary.__init__(self)
        RestrictedByFile.__init__(self, fileDict)
        
    def addEntity(self, includeEntity):
        if self.isFilePermitted(includeEntity.getIncludingFile()):
            return IncludeDictionary.addEntity(self, includeEntity)
            
