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
# LineChecker.py runs over a given line, adjusting the scope accordingly.
#
# Another joyfull Van Rompaey & Du Bois creation

class LineChecker:
	remarkableChars = ["/","*","{","}",";"]
	shortComment = "//"
	longCommentStart = "/*"
	longCommentEnd = "*/"
	
	def __init__(self, scope):
		self.__scope = scope
		self.__line = None
		self.__curChar = None
		self.__prevChar = None
		self.__inShortCommentSection = None
		self.__inScopeCharCache = None
	
	def __clear(self):
		self.__curChar = ""
		self.__prevChar = ""
		self.__inShortCommentSection = False
		self.__inScopeCharCache = ""
	
	def __lastTwoChars(self):
		return self.__prevChar + self.__curChar
	
	def __enterShortComment(self):
		self.__inShortCommentSection = True
	
	def __leaveShortComment(self):
		self.__inShortCommentSection = False
	
	def __shiftChar(self):
		self.__prevChar = self.__curChar
		self.__curChar = ""
	
	def __rememberChar(self):
		charInsideScope = not self.__scope.outOfScope()
		if charInsideScope:
			self.__inScopeCharCache += self.__curChar
	
	def __inCommentSection(self):
		return self.__inShortCommentSection or self.__scope.inLongCommentSection()
	
	def __checkCurrentChar(self):
		if self.__curChar == "{":
			self.__scope.enter()
		elif self.__curChar == "}":
			self.__scope.leave()
	
	def __relevantChar(self):
		return self.__curChar in self.remarkableChars
	
	def check(self, line):
		line = line.rstrip("\n")
		self.__clear()

		self.__line = line
		
		for self.__curChar in self.__line:
			curChar = self.__curChar
			self.__rememberChar()
			
			if not self.__relevantChar():
				continue
			
			if not self.__inCommentSection():
				if self.__lastTwoChars() == self.shortComment:
					self.__enterShortComment()
				elif self.__lastTwoChars() == self.longCommentStart:
					self.__scope.enterLongCommentSection()
				elif self.__curChar == ";" and not self.__scope.entered():
					self.__scope.markAsDeclaration()
			else:
				if self.__lastTwoChars() == self.longCommentEnd:
					self.__scope.leaveLongCommentSection()
			
			if not self.__inCommentSection():
				self.__checkCurrentChar()
	
			self.__shiftChar()
		
		return self.__inScopeCharCache