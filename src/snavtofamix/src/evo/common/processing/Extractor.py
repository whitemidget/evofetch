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

from evo.common.objects.AuthorEntity import AuthorEntity
from evo.common.objects.RevisionEntity import RevisionEntity, CommitEntity, ActionEntity
from evo.common.objects.SourceFileEntity import SourceFileEntity, FileLinksEntity
from evo.common.objects.TransactionEntity import TransactionEntity
from evo.common.objects.SystemVersionEntity import SystemVersionEntity
from evo.common.objects.ReleaseEntity import ReleaseEntity
from evo.common.objects.ReleaseRevisionEntity import ReleaseRevisionEntity

from evo.common.dictionaries.AuthorDict import AuthorDictionary
from evo.common.dictionaries.RevisionDict import RevisionDictionary
from evo.common.dictionaries.SourceFileDict import SourceFileDictionary
from evo.common.dictionaries.TransactionDict import TransactionDictionary
from evo.common.dictionaries.SystemVersionDict import SystemVersionDictionary
from evo.common.dictionaries.ReleaseDict import ReleaseDictionary
from evo.common.dictionaries.ReleaseRevisionDict import ReleaseRevisionDictionary 

from pycvsanaly2.Database import statement

class Extractor:
    def __init__(self):
        self.db = None;
        self.connection = None
        self.repositoryId = None
        self.projectName = None
        self.slidingTimeWindow = 0
        self.authorDict = AuthorDictionary()
        self.revisionDict = RevisionDictionary()
        self.filesDict = SourceFileDictionary()
        self.transactionDict = TransactionDictionary()
        self.systemVersionDict = SystemVersionDictionary()
        self.releaseDict = ReleaseDictionary()
        self.releaseRevisionDict = ReleaseRevisionDictionary()
        
    def getDb(self):
        return self.db
    
    def setDb(self, db):
        self.db = db
        
    def getConnection(self):
        return self.connection
    
    def setConnection(self, connection):
        self.connection = connection
        
    def getRepositoryId(self):
        return self.repositoryId
    
    def setRepositoryId(self, repositoryId):
        self.repositoryId = repositoryId
        
    def getProjectName(self):
        return self.projectName
    
    def setProjectName(self, projectName):
        self.projectName = projectName
    
    def getSlidingTimeWindow(self):
        return self.slidingTimeWindow
    
    def setSlidingTimeWindow(self, slidingTimeWindow):
        self.slidingTimeWindow = slidingTimeWindow
                
    def getAuthorDictionary(self):
        return self.authorDict
    
    def getRevisionDictionary(self):
        return self.revisionDict
    
    def getFilesDictionary(self):
        return self.filesDict
    
    def getTransactionDictionary(self):
        return self.transactionDict
    
    def getSystemVersionDictionary(self):
        return self.systemVersionDict
    
    def getReleaseDictionary(self):
        return self.releaseDict
    
    def getReleaseRevisionDictionary(self):
        return self.releaseRevisionDict

    def fetchAuthors(self):

        cursor = self.connection.cursor()
        sql = "SELECT id, name, email FROM people " + \
              "WHERE id IN " + \
              "(SELECT DISTINCT committer_id FROM scmlog WHERE repository_id=?)"
        cursor.execute(statement(sql, self.db.place_holder), (self.repositoryId,))
    
        rs = cursor.fetchmany()

        while rs:
            for row in rs:
                author = AuthorEntity()
                author.setDbId(row[0])
                author.setIdentifier(row[1])
                author.setFullName(row[1])
                author.setEmailAddress(row[2])
                self.authorDict.add(author)
            
            rs = cursor.fetchmany()
            
        cursor.close()

    def fetchRevisions(self):
    
        cursor = self.connection.cursor()
        cursor.execute(statement("SELECT id, rev, message, date, committer_id from scmlog WHERE repository_id=?", self.db.place_holder), (self.repositoryId,))
    
        rs = cursor.fetchmany()
    
        while rs:
            for row in rs:
                commit = CommitEntity()
                commit.setDbId(row[0])
                commit.setName(row[1])
                commit.setMessage(row[2])
                commit.setCreationTime(row[3])
                commit.setAuthorDbId(row[4])
                self.revisionDict.addCommit(commit)
            
            rs = cursor.fetchmany()
        
        cursor.close()
    
        cursor = self.connection.cursor()
        sql = "SELECT actions.id, actions.file_id, actions.commit_id, actions.type " + \
              "FROM actions, files " + \
              "WHERE actions.file_id = files.id " + \
              "AND actions.type IN ('A', 'M', 'D') " + \
              "AND actions.branch_id = 1 " + \
              "AND files.repository_id=?"
        cursor.execute(statement(sql, self.db.place_holder), (self.repositoryId,))
    
        rs = cursor.fetchmany()
        
        while rs:
            for row in rs:
                action = ActionEntity()
                action.setDbId(row[0])
                action.setFileId(row[1])
                action.setCommitId(row[2])
                action.setDeletion(row[3] == 'D')
                commit = self.revisionDict.getCommit(row[2])
                commit.addAction(action)
                self.revisionDict.addAction(action);
            
            rs = cursor.fetchmany()
        
        cursor.close()
    
        for action in self.revisionDict.actionDict.values():
            commit = self.revisionDict.getCommit(action.getCommitId())
            author = self.authorDict.getEntity(commit.getAuthorDbId())
            revision = RevisionEntity()
            revision.setDbId(action.getDbId())
            revision.setFileDbId(action.getFileId())
            revision.setCommitId(action.getCommitId())
            revision.setName(commit.getName())
            revision.setMessage(commit.getMessage().strip())
            revision.setCreationTime(commit.getCreationTime())
            revision.setAuthor(author)
            revision.setDeletion(action.isDeletion())
            self.revisionDict.add(revision)
            action.setRevision(revision)
            
    def fetchFiles(self):
    
        cursor = self.connection.cursor()
        cursor.execute(statement("SELECT id, file_name FROM files WHERE repository_id=?", self.db.place_holder), (self.repositoryId,))
    
        rs = cursor.fetchmany()
    
        while rs:
            for row in rs:
                sourceFile = SourceFileEntity()
                sourceFile.setDbId(row[0])
                sourceFile.setName(row[1])
                self.filesDict.addNew(sourceFile)
            
            rs = cursor.fetchmany()
            
        cursor.close()
    
        cursor = self.connection.cursor()
        sql = "SELECT file_links.file_id, file_links.parent_id, file_links.commit_id " + \
              "FROM file_links, files " + \
              "WHERE file_links.file_id = files.id " + \
              "AND files.repository_id=?"
        cursor.execute(statement(sql, self.db.place_holder), (self.repositoryId,))
    
        rs = cursor.fetchmany()
    
        linksDict = {}
    
        while rs:
            for row in rs:
                fileId = row[0]
                link = FileLinksEntity()
                link.setFileId(fileId)
                link.setParentId(row[1])
                link.setCommitId(row[2])
                if not (fileId in linksDict):
                    linksDict[fileId] = []
                linksDict[fileId].append(link)
            
            rs = cursor.fetchmany()
        
        cursor.close()
    
        for sourceFileList in self.filesDict.entityDict.values():
            sourceFile = sourceFileList[0]
            links = linksDict[sourceFile.getDbId()]
            i = 0
            for link in links:
                if i == 0:
                    thisFile = sourceFile
                else:
                    thisFile = self.filesDict.cloneEntity(sourceFile)
                commitId = link.getCommitId()
                if not (commitId is None):
                    commit = self.revisionDict.getCommit(commitId)
                    thisFile.setCreationTime(commit.getCreationTime())
                thisFile.setCreationCommitId(commitId)
                aLink = link
                while aLink.getParentId() != -1:
                    parentFile = self.filesDict.getEntity(aLink.getParentId(), commitId)
                    thisFile.addParent(parentFile.getName())
                    linkList = linksDict[parentFile.getDbId()]
                    aLink = None
                    for parentLink in linkList:
                        parentCommit = parentLink.getCommitId()
                        if (parentCommit is None) or (commitId is None) or parentCommit <= commitId:
                            aLink = parentLink
                addRoot = self.getRootToAddtoPath()
                if addRoot != "":
                    thisFile.addParent(addRoot)
                self.filesDict.addCompleted(thisFile)
                i += 1
                
    def fetchTransactions(self):
        
        keyList = sorted(self.revisionDict.dictByTime.keys())
        
        for timeKey in keyList:
        
            revision = self.revisionDict.getEntity(timeKey[1])
            action = self.revisionDict.getAction(revision.getDbId())
            commit = self.revisionDict.getCommit(action.getCommitId())
            transaction = commit.getTransaction()
            if revision.isDeletion():
                sourceFile = revision.getSourceFile()
                deletedRevision = sourceFile.getRevisionPriorTo(revision)
                if deletedRevision is None:
                    continue
                if not (deletedRevision.getDeletingTransaction() is None):
                    continue
                if transaction is None:
                    transaction = self.newTransaction(commit.getName())
                    commit.setTransaction(transaction)
                transaction.addDeletedRevision(deletedRevision, revision)
            else:
                if transaction is None:
                    transaction = self.newTransaction(commit.getName())
                    commit.setTransaction(transaction)
                transaction.addRevision(revision)
            
    def linkRevisionsAndFiles(self):
    
        revisionList = sorted(self.revisionDict.dictByTime.keys())
        
        for timeKey in revisionList:
            revision = self.revisionDict.getEntity(timeKey[1])
            fileId = revision.getFileDbId()
            commitId = revision.getCommitId()        
            sourceFile = self.filesDict.getEntity(fileId, commitId)
            revision.setSourceFile(sourceFile)
            self.setRevisionName(revision)
            if not revision.isDeletion():
                sourceFile.addRevision(revision)
                
    def setRevisionName(self, revision):
        newName = revision.getName() + '|' + revision.getSourceFile().getUniqueName()
        revision.setName(newName)
            
    def newTransaction(self, transactionName):
        transaction = TransactionEntity()
        if not (transactionName is None):
            transaction.setName(transactionName)
        self.transactionDict.add(transaction)
        return transaction
    
    def buildSystemVersions(self):
        
        currentFiles = {}
        
        for transaction in self.transactionDict.dictByNumber.values():
            
            for revision in transaction.getRevisions().values():
                
                fileName = revision.getSourceFile().getUniqueName()
                currentFiles[fileName] = revision
            
            for fileRevision in currentFiles.values():
                systemVersion = SystemVersionEntity()
                systemVersion.setTransaction(transaction)
                systemVersion.setRevision(fileRevision)
                self.systemVersionDict.add(systemVersion)

    def fetchReleases(self):
        
        cursor = self.connection.cursor()
        sql = "SELECT id, name " +\
              "FROM tags " + \
              "WHERE id IN (SELECT DISTINCT tag_revisions.tag_id " + \
              "FROM tag_revisions, scmlog, actions " + \
              "WHERE tag_revisions.commit_id = scmlog.id " + \
              "AND actions.commit_id = scmlog.id " + \
              "AND actions.branch_id = 1 " + \
              "AND scmlog.repository_id=?)"
        cursor.execute(statement(sql, self.db.place_holder), (self.repositoryId,))
    
        rs = cursor.fetchmany()
    
        while rs:
            for row in rs:
                release = ReleaseEntity()
                release.setDbId(row[0])
                release.setName(row[1])
                self.releaseDict.add(release)
            
            rs = cursor.fetchmany()
        
        cursor.close()
        
    def fetchReleaseRevisions(self):
        
        cursor = self.connection.cursor()
        sql = "SELECT file_copies.from_id, file_copies.from_commit_id, tag_revisions.tag_id " + \
              "FROM tag_revisions, scmlog, actions, file_copies " + \
              "WHERE scmlog.id = tag_revisions.commit_id " + \
              "AND actions.commit_id = scmlog.id " + \
              "AND file_copies.action_id = actions.id " + \
              "AND actions.branch_id = 1 " + \
              "AND actions.type = 'C' " + \
              "AND scmlog.repository_id=?"
        cursor.execute(statement(sql, self.db.place_holder), (self.repositoryId,))
        
        fileLinks = []
        
        rs = cursor.fetchmany()
        
        while rs:
            for row in rs:
                fileLinks.append([row[0], row[1], row[2]])
                
            rs = cursor.fetchmany()
            
        cursor.close()
        
        resolvedFileLinks = []
        
        for fileLink in fileLinks:
            self.__buildReleaseRevision(fileLink[0], fileLink[1], fileLink[2], resolvedFileLinks)
            
        for resolved in resolvedFileLinks:
            fileId = resolved[0]
            commitId = resolved[1]
            releaseId = resolved[2]

            sourceFile = self.filesDict.getEntity(fileId, commitId)
            revision = sourceFile.getLastRevisionPriorToCommit(commitId)
            if not (revision is None):
                release = self.releaseDict.getEntity(releaseId)
                releaseRevision = ReleaseRevisionEntity()
                releaseRevision.setRelease(release)
                releaseRevision.setRevision(revision)
                self.releaseRevisionDict.add(releaseRevision)
                
    def getRootToAddtoPath(self):
        return "" 

    def __buildReleaseRevision(self, fileId, commitId, releaseId, resolvedFiles):
        
        cursor = self.connection.cursor()
        sql = "SELECT file_id " + \
              "FROM file_links " + \
              "WHERE parent_id=? " + \
              "AND commit_id<=?";
        cursor.execute(statement(sql, self.db.place_holder), (fileId, commitId))
        
        fileLinks = []
        
        rs = cursor.fetchmany()
        
        while rs:
            for row in rs:
                fileLinks.append(row[0])
                
            rs = cursor.fetchmany()
            
        cursor.close()
        
        if len(fileLinks) == 0:
            resolvedFiles.append([fileId, commitId, releaseId])
        else:
            for fileLink in fileLinks:
                self.__buildReleaseRevision(fileLink, commitId, releaseId, resolvedFiles)
        
        
        
