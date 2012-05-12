# !/usr/bin/python

# IEMetrics generates metrics for invokable entities (functions or metrics)
# starting at a specified source location.
#
# Copyright (C) 2006 Bart Van Rompaey and Bart Du Bois
#
# This file is part of IEMetrics.
#
# IEMetrics is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# IEMetrics is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IEMetrics; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Copyright 2008 University of Antwerp
# Author(s): Bart Van Rompaey - bart.vanrompaey2@ua.ac.be
#					Bart Du Bois - bart.dubois@ua.ac.be
#
# Scope.py represents an abstraction of a scope. I.e., a delimitation of
# the boundaries of code through curly brackets.
#
# Another joyfull Van Rompaey & Du Bois creation

class Scope:
	def __init__(self):
		self.__bracketStackLevel = None
		self.__scopeEntered = False
		self.__inLongCommentSection = False
		self.clear()
	
	def markAsDeclaration(self):
		self.__scopeEntered = True
	
	def enter(self):
		self.__bracketStackLevel += 1
		self.__scopeEntered = True
	
	def leave(self):
		self.__bracketStackLevel -= 1
	
	def entered(self):
		return self.__scopeEntered
	
	def outOfScope(self):
		return self.__bracketStackLevel == 0
	
	def enterLongCommentSection(self):
		self.__inLongCommentSection == True
	
	def leaveLongCommentSection(self):
		self.__inLongCommentSection = False
	
	def inLongCommentSection(self):
		return self.__inLongCommentSection
	
	def clear(self):
		self.__bracketStackLevel = 0
		self.__scopeEntered = False