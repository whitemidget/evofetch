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

from time import mktime

# globals
RSFCounter = 0
MaximumRSFCounter = 0

def convertTimeToUNIX(dateTime):
    t = mktime(dateTime.timetuple())
    return t  

def getRSFCounter():
    global RSFCounter
    return RSFCounter

def getMaximumRSFCounter():
    global MaximumRSFCounter
    return MaximumRSFCounter

def setRSFCounter(value):
    global RSFCounter
    global MaximumRSFCounter
    RSFCounter = int(value)
    if RSFCounter > MaximumRSFCounter:
        MaximumRSFCounter = RSFCounter
        
def requestNewRSFId():
    setRSFCounter(getMaximumRSFCounter() + 1)
    return getMaximumRSFCounter()
        
  
    
