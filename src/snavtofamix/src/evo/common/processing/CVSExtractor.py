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

from evo.common.processing.Extractor import Extractor

from evo.common.objects.ReleaseRevisionEntity import ReleaseRevisionEntity

from pycvsanaly2.Database import statement

class CVSExtractor(Extractor):
    
    def fetchTransactions(self):
        
        if self.slidingTimeWindow == 0:
            Extractor.fetchTransactions()
        else:
            revisionList = sorted(self.revisionDict.dictByTime.keys())
            
            priorTimeStamp = None
            priorAuthor = None
            priorMessage = None
            transaction = None
            
            for timeKey in revisionList:
                revision = self.revisionDict.getEntity(timeKey[1])
                if revision.isDeletion():
                    sourceFile = revision.getSourceFile()
                    deletedRevision = sourceFile.getRevisionPriorTo(revision)
                    if deletedRevision is None:
                        continue
                    if not (deletedRevision.getDeletingTransaction() is None):
                        continue
                if priorTimeStamp == None:
                    priorTimeStamp = revision.getCreationTime()
                    priorAuthor = revision.getAuthor()
                    priorMessage = revision.getMessage()
                    transaction = self.newTransaction(None)
                currentTimeStamp = revision.getCreationTime()
                if revision.getAuthor() != priorAuthor:
                    transaction = self.newTransaction(None)
                elif revision.getMessage() != priorMessage:
                    transaction = self.newTransaction(None)
                else:
                    delta = currentTimeStamp - priorTimeStamp
                    totalSeconds = delta.seconds + delta.days * 24 * 3600
                    if totalSeconds > self.slidingTimeWindow:
                        transaction = self.newTransaction(None)
                if revision.isDeletion():
                    sourceFile = revision.getSourceFile()
                    deletedRevision = sourceFile.getRevisionPriorTo(revision)
                    transaction.addDeletedRevision(deletedRevision, revision)
                else:
                    transaction.addRevision(revision)
                priorTimeStamp = currentTimeStamp
                priorAuthor = revision.getAuthor()
                priorMessage = revision.getMessage()
                                
    def fetchReleaseRevisions(self):
        
        cursor = self.connection.cursor()
        sql = "SELECT scmlog.id, tag_revisions.tag_id " + \
              "FROM scmlog, tag_revisions, actions " + \
              "WHERE scmlog.id = tag_revisions.commit_id " + \
              "AND actions.commit_id = scmlog.id " + \
              "AND actions.branch_id = 1 " + \
              "AND scmlog.repository_id=? " + \
              "ORDER BY tag_revisions.tag_id, scmlog.id"
        cursor.execute(statement(sql, self.db.place_holder), (self.repositoryId,))
        
        rs = cursor.fetchmany()
        
        while rs:
            for row in rs:
                releaseRevision = ReleaseRevisionEntity()
                release = self.releaseDict.getEntity(row[1])
                commit = self.revisionDict.getCommit(row[0])
                action = commit.getActions().values()[0]
                revision = self.revisionDict.getEntity(action.getDbId())
                releaseRevision.setRelease(release)
                releaseRevision.setRevision(revision)
                self.releaseRevisionDict.add(releaseRevision)
                
            rs = cursor.fetchmany()
            
        cursor.close()
        
    def setRevisionName(self, revision):
        revision.setName(revision.getName())
    