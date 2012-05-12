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

from common.output.cdifWriter import requestNewCdifId

# global variables
transactionCounter = 0

class TransactionDictionary:
    def __init__(self):
        self.dictByName = {}
        self.dictByNumber = {}
        self.lastTransaction = None
        
    def add(self, transactionEntity):
        self.addPreBuiltEntity(transactionEntity)
        if self.lastTransaction is not None:
            self.lastTransaction.setNextTransaction(transactionEntity)
        transactionEntity.setPreviousTransaction(self.lastTransaction)
        self.lastTransaction = transactionEntity
        
    def addPreBuiltEntity(self, transactionEntity):
        if transactionEntity.getCdifId() == None:
            transactionEntity.setCdifId(requestNewCdifId())
        if transactionEntity.getTransactionNumber() == None:
            transactionEntity.setTransactionNumber(self.requestNewTransaction())
        self.dictByName[transactionEntity.getUniqueName()] = transactionEntity
        self.dictByNumber[transactionEntity.getTransactionNumber()] = transactionEntity
        
    def getEntityByName(self, transactionName):
        return self.dictByName[transactionName]
    
    def getEntityByNumber(self, transactionNumber):
        return self.dictByNumber[transactionNumber]
    
    def requestNewTransaction(self):
        global transactionCounter
        transactionCounter += 1
        return transactionCounter
        
        