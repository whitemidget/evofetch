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

class CdifWriterAdapter:
    
    def __init__(self):
        self.outputHandle = None
        self.decorators = []
        self.currentDecorator = None
        self.buffer = None
        self.buffering = False
        
    def getOutputHandle(self):
        return self.outputHandle
    
    def setOutputHandle(self, outputHandle):
        self.outputHandle = outputHandle
        
    def getDecorators(self):
        return self.decorators
    
    def addDecorator(self, decorator):
        self.decorators.append(decorator)
        
    def removeDecorator(self, decorator):
        try:
            self.decorators.remove(decorator)
        except:
            pass
    
    def write(self, value):
        if not self.adaptOutput(value):
            self.outputHandle.write(value)
            
    def adaptOutput(self, value):
        if self.buffering:
            self.__addToBuffer(value)
            if self.endBuffer(value):
                self.buffering = False
                self.__decorate()
                self.outputHandle.write(self.buffer)
                self.buffer = None
            return True
        else:
            if self.startBuffer(value):
                self.buffering = True
                self.__addToBuffer(value)
            return self.buffering

    def startBuffer(self, value):
        for decorator in self.decorators:
            fields = decorator.getInterestedFields()
            for field in fields:
                if field in value:
                    self.currentDecorator = decorator
                    return True
            
    def endBuffer(self, value):
        return (value[-1] == ")")
    
    def __addToBuffer(self, value):
        if self.buffer is None:
            self.buffer = value
        else:
            self.buffer = self.buffer + value
            
    def __decorate(self):
        if not (self.currentDecorator is None):
            self.buffer = self.currentDecorator.decorateWriterOutput(self.buffer)
            self.currentDecorator = None 