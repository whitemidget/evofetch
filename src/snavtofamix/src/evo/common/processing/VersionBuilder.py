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

import os
import shutil
import time

import evo.common.globals.Globals

from log4py import Logger
from shared import addLogTarget

from common.dictionaries import Dictionaries
from common.dictionaries.FileDictionary import buildFileDict

from common.infrastructure.Timing import Timer

from common.output import cdifWriter

from cplusplus.dataObjects.AccessEntity import AccessEntity
from cplusplus.dataObjects.AttributeEntity import AttributeEntity
from cplusplus.dataObjects.GlobalVariableEntity import GlobalVariableEntity
from cplusplus.dataObjects.oldArch.NamespaceEntity import NamespaceEntity
from cplusplus.dataObjects.InheritanceEntity import InheritanceEntity
from cplusplus.dataObjects.pmcMetricEntity import PmcMetricEntity
from cplusplus.dataObjects.Scope import Scope
from cplusplus.dataObjects.TypeDefEntity import TypeDefEntity

from cplusplus.dictionaries import newArch
from cplusplus.dictionaries.AccessDictionary import AccessDictionary
from cplusplus.dictionaries.includeDict import TransitiveIncludeDictionary
from cplusplus.dictionaries.InheritanceDictionary import InheritanceDictionary, \
                                                  TransitiveInheritanceDictionary
from cplusplus.dictionaries.TypedefDictionary import TypedefDictionary

from cplusplus.input import snavTableReader

from cplusplus.linkingAndRules.oldArch.ClassSelector import ClassSelector
from cplusplus.linkingAndRules.oldArch.ClassUsageChecker import ClassUsageChecker
from cplusplus.linkingAndRules.oldArch.NamespaceContainmentChecker import \
                                       NamespaceContainmentChecker

from evo.common.dictionaries.EvoAccessibleEntityDictionary import EvoAccessibleEntityDictionary
from evo.common.dictionaries.EvoClassDictionary import EvoClassDictionary
from evo.common.dictionaries.EvoCppDictionary import EvoCppDictionary
from evo.common.dictionaries.EvoFileDictionary import EvoFileDictionary
from evo.common.dictionaries.EvoIncludeDictionary import EvoIncludeDictionary
from evo.common.dictionaries.EvoInvokableEntityDictionary import EvoInvokableEntityDictionary                                       
from evo.common.output.CdifWriterAdapter import CdifWriterAdapter
from evo.common.processing.SourceBackup import SourceBackup

from repositoryhandler.backends.cvs import CVSRepository
from repositoryhandler.backends.git import GitRepository

from repositoryhandler.Command import Command
from repositoryhandler.backends import (create_repository, RepositoryInvalidWorkingCopy)

from repositoryhandler.backends.watchers import *
from pycvsanaly2.Command import CommandError
from evo.common.output import EvoCdifWriter

class VersionBuilder:
    def __init__(self):
        self.extractor = None
        self.repositoryUri = None
        self.repositoryType = None
        self.folderName = None
        self.checkOutByDate = True
        self.cleanProjectFolder = False
        self.log = Logger().get_instance(self)
        self.saveCdifCounter = 0
        self.reprocess = False
        self.firstTransaction = False
        self.fullMacroDict = {}
        self.fullClassDict = EvoClassDictionary(None)
        self.fullClassDict.restricting = False
        self.fullAttrDict = EvoAccessibleEntityDictionary(None)
        self.fullAttrDict.restricting = False
        self.fullInvokableEntityDict = EvoInvokableEntityDictionary(None)
        self.fullInvokableEntityDict.restricting = False
        addLogTarget(self.log)
        
    def getExtractor(self):
        return self.extractor
    
    def setExtractor(self, extractor):
        self.extractor = extractor
        
    def getRepositoryUri(self):
        return self.repositoryUri
        
    def setRepositoryUri(self, repositoryUri):
        self.repositoryUri = repositoryUri
        
    def getReposityType(self):
        return self.repositoryType
    
    def setRepositoryType(self, repositoryType):
        self.repositoryType = repositoryType
        
    def getFolderName(self):
        return self.folderName
    
    def setFolderName(self, folderName):
        self.folderName = folderName
        
    def isCheckOutByDate(self):
        return self.checkOutByDate
    
    def setCheckOutByDate(self, checkOutByDate):
        self.checkOutByDate = checkOutByDate
        
    def isCleanProjectFolder(self):
        return self.cleanProjectFolder
    
    def setCleanProjectFolder(self, cleanProjectFolder):
        self.cleanProjectFolder = cleanProjectFolder
        
    def build(self):

        options = BuilderOptions()        
        options.setWorkFolder(self.folderName + os.sep + 'work')
        options.setDataFolder(self.folderName + os.sep + 'data')
        
        if self.cleanProjectFolder or (not os.path.exists(self.folderName)):
            shutil.rmtree(self.folderName, True)
            os.mkdir(self.folderName)
            os.mkdir(options.getWorkFolder())
            os.mkdir(options.getDataFolder())
            os.mkdir(options.getBackupFolder())
        
        separator = '/'
        paths = self.repositoryUri.split(separator)
        repositoryProjectName = paths.pop()
        options.setRepositoryRoot(repositoryProjectName)
        options.setRepositoryProjectName(repositoryProjectName)
        shortenedRepositoryUri = separator.join(paths)

        if self.repositoryType == "cvs":
            repo = ExtendedCVSRepository(shortenedRepositoryUri)
        elif self.repositoryType == "git":
            repo = ExtendedGitRepository(shortenedRepositoryUri)
        else:
            repo = create_repository(self.repositoryType, shortenedRepositoryUri)
        uri = repo.get_uri()
        if uri != shortenedRepositoryUri:
            newRoot = shortenedRepositoryUri[len(uri):] + separator + options.getRepositoryRoot()
            if newRoot[0] == separator:
                newRoot = newRoot[1:]
            options.setRepositoryRoot(newRoot)
        options.setRepository(repo)
        
        transactionDict = self.extractor.getTransactionDictionary()
        
        self.firstTransaction = True
        firstTransactionToProcess = True
        priorTransaction = None
        
        transactionList = transactionDict.dictByNumber.keys()
        transactionList.sort()
        
        for transactionNumber in transactionList:
            
            transaction = transactionDict.getEntityByNumber(transactionNumber)
            cdifFile = options.getDataFolder() + os.sep + options.getRepositoryProjectName() + '_' + transaction.getUniqueName() + '.cdif'

            if self.transactionHasSourceChanges(transaction):
                if (not firstTransactionToProcess) or (not os.path.exists(cdifFile)):
                
                    if firstTransactionToProcess and (not (priorTransaction is None)):
                        self.reprocess = True
                        self.processTransaction(priorTransaction, options)
                        self.reprocess = False
                    self.processTransaction(transaction, options)
            
                    firstTransactionToProcess = False

                priorTransaction = transaction
                self.firstTransaction = False

    def processTransaction(self, transaction, options):
                
        revisions = transaction.getRevisions()
        
        if self.reprocess:
            print "Reprocessing existing transaction " + transaction.getUniqueName()
            cdifFile = options.getDataFolder() + os.sep + options.getRepositoryProjectName() + '_' + transaction.getUniqueName() + '.reprocess'
        else:
            cdifFile = options.getDataFolder() + os.sep + options.getRepositoryProjectName() + '_' + transaction.getUniqueName() + '.cdif'

        dummyFile = options.getDataFolder() + os.sep + options.getRepositoryProjectName() + '_' + transaction.getUniqueName() + '.dummy'
        repo = options.getRepository()
        separator = '/'
        
        if not self.reprocess:
            backup = SourceBackup(options, options.getWorkFolder())
            if not self.firstTransaction:
                backup.performBackup(transaction)
        
        if self.reprocess or transaction.hasRevisions():
            print "Checking out transaction " + transaction.getUniqueName()
        
            retries = 0
            while retries < 10:
                try:
                    if self.checkOutByDate:
                        if self.repositoryType == "cvs":
                            timeStamp = transaction.getLatestTime().isoformat().replace('T', ' ') + 'Z'
                            repo.checkout(options.getRepositoryRoot(), options.getWorkFolder(), None, None, None, timeStamp)
                            break
                        elif self.repositoryType == "git":
                            transactionRevisionId = transaction.getUniqueName()
                            repo.checkout(options.getRepositoryRoot(), options.getWorkFolder(), None, transactionRevisionId, transactionRevisionId)
                            break
                        else:
                            transactionRevisionId = transaction.getUniqueName()
                            repo.checkout(options.getRepositoryRoot(), options.getWorkFolder(), None, None, transactionRevisionId)
                            break
                    else:
                        for revision in revisions.values():
                            sourceFile = revision.getSourceFile()
                            sourceParts = sourceFile.getUniqueName().split(separator)
                            del sourceParts[0]
                            fullName = separator.join(sourceParts)
                            repo.checkout(fullName, options.getWorkFolder(), None, None, revision.getName().split('|')[0])
                        break
                except:
                    if retries >= 10:
                        raise
                    else:
                        retries += 1;
                        time.sleep(5)
                        continue
            
            print "Invoking FETCH on transaction " + transaction.getUniqueName()
            print "*** Entering FETCH ***"
            
            runFetchInFolder = options.getWorkFolder()
            
            fetchPath = os.getenv("FETCH")
            
            if self.reprocess:
                cmd = fetchPath + os.sep + "scripts/cpp2snavdb.sh %s" % runFetchInFolder
                result = os.system(cmd)        
            else:
                filesList = self.folderName + os.sep + 'files.txt'
                self.writeTransactionFilesToFile(transaction, filesList)                    
                cmd = fetchPath + os.sep + "scripts/cpp2snavdb.sh %s --files=%s" % (runFetchInFolder, filesList)
                result = os.system(cmd)
                os.remove(filesList)        

            if result != 0:
                raise CommandError(cmd, result)
                
            print "*** Leaving FETCH ***"

        output_file = cdifFile
        output_handle = open(output_file, "w")
        output_handle.close()
        output_handle = open(output_file, "a+")
                
        cdifAdapter = CdifWriterAdapter()
        cdifAdapter.setOutputHandle(output_handle)
                
        cdifWriter.set_outputhandle(cdifAdapter)
        EvoCdifWriter.setOutputHandle(output_handle)
        
        evoFileDict = EvoFileDictionary()
        evoFileDict.restrictToTransaction(transaction)
        cdifAdapter.addDecorator(evoFileDict)
        Dictionaries.file_dict = evoFileDict

        evoIncludeDict = EvoIncludeDictionary(evoFileDict)
        Dictionaries.include_dict = evoIncludeDict
        Dictionaries.trans_include_dict = TransitiveIncludeDictionary()
        
        if not self.reprocess:
            classDict = EvoClassDictionary(evoFileDict)
            invokeableEntityDict = EvoInvokableEntityDictionary(evoFileDict)
            attrDict = EvoAccessibleEntityDictionary(evoFileDict)

        if self.reprocess or transaction.hasRevisions():
        
            dbdumpPath = options.getWorkFolder() + os.sep + 'dbdump'
            dbLoc = dbdumpPath + os.sep + 'work'
        
            fileDbLoc = dbLoc + ".files"
            includeDbLoc = dbLoc + ".includes2"
            condCompDbLoc = dbLoc + ".condcomp"
        
            print "Parsing files ..."
            self.log.info("    Parsing files ...")
            buildFileDict(fileDbLoc)
            cdifWriter.generateFileEntityInfo(Dictionaries.file_dict)
        
            print "Parsing includes..."
            self.log.info("  Parsing includes...")
            snavTableReader.parseIncludes(includeDbLoc)

            if self.reprocess:
                self.log.info("Parsing all macro definition directives ...")
                # We need all the macros, but we don't need the CDIF, so we're going to write to a temporary file
                dummyHandle = self.setupDummyFile(dummyFile)
                snavTableReader.parseMacroDefDirectives(condCompDbLoc, self.fullMacroDict)
                self.destroyDummyFile(dummyFile, dummyHandle, cdifAdapter)

            print "Filtering preprocessor statements..."
            self.log.info("  Filtering preprocessor statements...")
            self.filterConditionalCompilation(condCompDbLoc, evoFileDict)
        
            print "Parsing conditional compilation directives ..."
            self.log.info("    Parsing conditional compilation directives ...")
            condCompDict = EvoCppDictionary(evoFileDict)
            snavTableReader.parseConditionalCompilationDirectives(condCompDbLoc, condCompDict)
            cdifWriter.setCppDict(condCompDict)

            print "Parsing macro definition directives ..."
            self.log.info("    Parsing macro definition directives ...")
            maDict = {}
            snavTableReader.parseMacroDefDirectives(condCompDbLoc, maDict)
            if not self.reprocess:
                self.fullMacroDict.update(maDict)

            print "Entering FAMIX Level 1"
            self.log.info("Entering famix Level 1")
            namespaceDbLoc = dbLoc + ".namespaces"
            clDbLoc = dbLoc + ".classes"
            miDbLoc = dbLoc + ".methods"
            mdDbLoc = dbLoc + ".methoddefs"
            inDbLoc = dbLoc + ".inheritance"
            fuDbLoc = dbLoc + ".functions"
            fdDbLoc = dbLoc + ".functiondefs"
            unionDbLoc = dbLoc + ".unions"
            typedefDbLoc = dbLoc + ".typedef"
            metrics_file = dbLoc + ".pmcmetrics"
        
            if os.path.exists(namespaceDbLoc):
                print "Filtering namespaces..."
                self.log.info("    Filtering namespaces...")
                self.filterNamespaces(namespaceDbLoc, evoFileDict)
                print "Parsing namespaces..."
                self.log.info("    Parsing namespaces...")
                namespaceDict = snavTableReader.parseNamespaces(namespaceDbLoc)
                print "Parsed " + `namespaceDict.getNumberOfEntities()` + " namespaces"
                self.log.info("Parsed " + `namespaceDict.getNumberOfEntities()` + " namespaces")
        
                print "Parsing namespace usages..."
                self.log.info("    Parsing namespace usages...")
                namespaceUsageDict = snavTableReader.parseNamespaceUsages(namespaceDbLoc)
                print "Parsed " + `namespaceUsageDict.getNumberOfEntities()` + " namespace usages"
                self.log.info("Parsed " + `namespaceUsageDict.getNumberOfEntities()` + " namespace usages")
            else:
                Dictionaries.namespace_dict = newArch.NamespaceDictionary.NamespaceDictionary()
                Dictionaries.namespace_using_directive_dict = newArch.UsingDirectiveDictionary.UsingDirectiveDictionary()

            namespaceContainmentChecker = NamespaceContainmentChecker(namespaceDict)
            namespaceUsageContainmentChecker = NamespaceContainmentChecker(namespaceUsageDict)

            print "Parsing classes ...."
            self.log.info("    Parsing classes ...")
            if self.reprocess:
                # We need all the classes, but we don't need the CDIF, so we're going to write to a temporary file
                dummyHandle = self.setupDummyFile(dummyFile)
                snavTableReader.parseClasses(clDbLoc, self.fullClassDict, namespaceContainmentChecker)
                if os.path.exists(unionDbLoc):
                    print "Parsing unions..."
                    self.log.info("    Parsing unions...")
                    snavTableReader.parseClasses(unionDbLoc, self.fullClassDict, namespaceContainmentChecker)
                    self.destroyDummyFile(dummyFile, dummyHandle, cdifAdapter)
            else:
                snavTableReader.parseClasses(clDbLoc, classDict, namespaceContainmentChecker)
                if os.path.exists(unionDbLoc):
                    print "Parsing unions..."
                    self.log.info("    Parsing unions...")
                    snavTableReader.parseClasses(unionDbLoc, classDict, namespaceContainmentChecker)
                classDict.mergeInto(self.fullClassDict)
                
            if os.path.exists(namespaceDbLoc):
                print "Parsing class usages..."            
                self.log.info("    Parsing class usages...")
                classUsageDict = snavTableReader.parseClassUsages(namespaceDbLoc, namespaceContainmentChecker)
                print "Parsed " + `classUsageDict.getNumberOfEntities()` + " class usages"
                self.log.info("Parsed " + `classUsageDict.getNumberOfEntities()` + " class usages")
            else:
                Dictionaries.class_using_directive_dict = newArch.UsingDirectiveDictionary.UsingDirectiveDictionary()

            classUsageContainmentChecker = ClassUsageChecker(classUsageDict)
        
            self.log.info("    Filtering typedefs...")
            self.filterTypedefs(typedefDbLoc, evoFileDict)
            self.log.info("    Parsing typedefs ...")
            typedefDict = TypedefDictionary()

            scope = Scope(namespaceContainmentChecker, namespaceUsageContainmentChecker,classUsageContainmentChecker)
            classSelector = ClassSelector(self.fullClassDict, scope, typedefDict)
            snavTableReader.parseTypedefs(typedefDbLoc, typedefDict, classSelector, namespaceContainmentChecker)
        
            self.log.info("    Filtering inheritance relations ...")
            self.filterInheritance(inDbLoc, evoFileDict)
            self.log.info("    Parsing inheritance relations ...")
            inhDict = InheritanceDictionary()
            snavTableReader.parseInheritance(inDbLoc, self.fullClassDict, inhDict, classSelector, classUsageDict)
        
            transInhDict=TransitiveInheritanceDictionary(inhDict)

            scope.setTransitiveInheritanceDict(transInhDict)
    
            print "Parsing methods ..."
            self.log.info("    Parsing methods ...")
            if self.reprocess:
                snavTableReader.parseMethodTables(miDbLoc, mdDbLoc, classSelector, namespaceContainmentChecker, typedefDict, self.fullInvokableEntityDict)
            else:
                invokeableEntityDict.setRestricting(False)
                snavTableReader.parseMethodTables(miDbLoc, mdDbLoc, classSelector, namespaceContainmentChecker,typedefDict,invokeableEntityDict)

            print "Parsing functions ..."
            self.log.info("    Parsing functions ...")
            if self.reprocess:
                snavTableReader.parseFunctionTables(fuDbLoc, fdDbLoc, typedefDict, namespaceContainmentChecker, classSelector, self.fullInvokableEntityDict)
            else:
                snavTableReader.parseFunctionTables(fuDbLoc, fdDbLoc, typedefDict, namespaceContainmentChecker, classSelector, invokeableEntityDict)            

            if not self.reprocess:  
                print "Generating invokable entities ..."      
                self.log.info("    Generating invokable entities ...")
                invokeableEntityDict.setRestricting(True)
                references = invokeableEntityDict.retrieveAllMultiLocReferences()
                for reference in references:
                    cdifWriter.generateInvocationEntityReference(reference,scope)
                invokeableEntityDict.mergeInto(self.fullInvokableEntityDict, classDict, backup)
                invokeableEntityDict.setRestricting(False)

            # DataReqs.checkPmcmetricReqsSatisfied(argv[1] + "/" + argv[2])
            self.log.info("Filtering pmccabe metrics ...")
            self.filterPmcMetrics(metrics_file, evoFileDict)
            self.log.info("Parsing pmccabe metrics ...")
            if os.path.exists(metrics_file):
                snavTableReader.parsePmcmetrics(metrics_file, self.fullInvokableEntityDict)
            else:
                self.log.error("Metrics file " + metrics_file + " not found.")

            # famix level 2
            print "Entering FAMIX Level 2"
            self.log.info("Entering famix Level 2")
            attrDbLoc = dbLoc + ".attributes"
            gvDbLoc = dbLoc + ".globalvar"
            conDbLoc = dbLoc + ".constants"
            # DataReqs.checkfamixL2Reqs(argv[1] + "/" + argv[2])

            if self.reprocess:
                print "Parsing all attributes ..."
                self.log.info("Parsing all attributes ...")
                # We need all the attributes, but we don't need the CDIF, so we're going to write to a temporary file
                dummyHandle = self.setupDummyFile(dummyFile)
                cdifAdapter.addDecorator(self.fullAttrDict)
                snavTableReader.parseAttributes(attrDbLoc, classSelector, self.fullAttrDict, namespaceContainmentChecker)
                cdifAdapter.removeDecorator(self.fullAttrDict)
                self.destroyDummyFile(dummyFile, dummyHandle, cdifAdapter)
        
                print "Parsing all global variables ..."
                self.log.info("Parsing all global variables ...")
                # We need all the global variables, but we don't need the CDIF, so we're going to write to a temporary file
                dummyHandle = self.setupDummyFile(dummyFile)
                snavTableReader.parseGlobalVars(gvDbLoc, namespaceContainmentChecker, classSelector, self.fullAttrDict)
                snavTableReader.parseGlobalVars(conDbLoc, namespaceContainmentChecker, classSelector, self.fullAttrDict)
                self.destroyDummyFile(dummyFile, dummyHandle, cdifAdapter)
            else:
                print "Filtering attributes ..."
                self.log.info("Filtering attributes ...")
                self.filterAttributes(attrDbLoc, evoFileDict)
                print "Parsing attributes ..."
                self.log.info("Parsing attributes ...")
                cdifAdapter.addDecorator(attrDict)
                snavTableReader.parseAttributes(attrDbLoc, classSelector, attrDict, namespaceContainmentChecker)
                cdifAdapter.removeDecorator(attrDict)

                print "Filtering global variables ..."
                self.log.info("Filtering global variables ...")
                self.filterGlobalVars(gvDbLoc, evoFileDict)
                self.filterGlobalVars(conDbLoc, evoFileDict)
                print "Parsing global variables ..."
                self.log.info("Parsing global variables ...")
                snavTableReader.parseGlobalVars(gvDbLoc, namespaceContainmentChecker, classSelector, attrDict)
                snavTableReader.parseGlobalVars(conDbLoc, namespaceContainmentChecker, classSelector, attrDict)

                attrDict.mergeInto(self.fullAttrDict, classDict, backup)

            # famix level 3
            if options.getFamixLevel() > 2:
                print "Entering FAMIX Level 3"
                self.log.info("Entering famix Level 3")
                referencesDbLoc = dbLoc + ".references"
                # DataReqs.checkfamixL3Reqs(argv[1] + "/" + argv[2])

                #  list of line numbers of the referencesDbLoc which are already
                # processed as accesses
                referenceLinesRecognizedAsAccesses = []

                print "Filtering accesses, invocations and macro uses ..."
                self.log.info("Filtering accesses, invocations and macro uses ...")
                self.filterAccesses(referencesDbLoc, evoFileDict)
                print "Parsing accesses ..."  
                self.log.info("Parsing accesses ...")
                accessDict = AccessDictionary()
                timer = Timer("Parsing accesses")
                timer.start()
                nrOfItems = snavTableReader.parseAccesses(referencesDbLoc, accessDict, self.fullInvokableEntityDict, self.fullAttrDict, typedefDict, transInhDict, scope, referenceLinesRecognizedAsAccesses)
                timer.stop()
                timer.log(nrOfItems)

                print "Parsing invocations ..."
                self.log.info("Parsing invocations ...")
                timer = Timer("Parsing invocations")
                timer.start()
                nrOfItems = snavTableReader.parseInvocations(referencesDbLoc, accessDict, \
                                                             self.fullInvokableEntityDict, typedefDict, \
                                                             transInhDict, scope, \
                                                             referenceLinesRecognizedAsAccesses)
                timer.stop()
                timer.log(nrOfItems)

                print "Parsing macro uses ..."
                self.log.info("Parsing macro uses ...")
                timer = Timer("Parsing macro uses")
                timer.start()

                nrOfItems = snavTableReader.parseMacroUses(referencesDbLoc, self.fullMacroDict, self.fullInvokableEntityDict)

                timer.stop()
                timer.log(nrOfItems)

        if not self.reprocess:

            if transaction.hasDeletedRevisions():
                print("Applying deleted transactions")
                deletedRevisions = transaction.getDeletedRevisions().values()
                for revision in deletedRevisions:
                    sourceFile = revision.getSourceFile().getUniqueName()
                    revisionId = revision.getUniqueName()
                    self.fullClassDict.removeSourceFile(revisionId, sourceFile, classDict)
                    self.fullInvokableEntityDict.removeSourceFile(revisionId, sourceFile, invokeableEntityDict, classDict)
                    self.fullAttrDict.removeSourceFile(revisionId, sourceFile, attrDict, classDict)
                
            print("Writing class version data to CDIF")
            EvoCdifWriter.generateClassVersionEntityInfo(classDict.versionDict)
            print("Writing invokable entity version data to CDIF")
            EvoCdifWriter.generateMethodVersionEntityInfo(invokeableEntityDict.methodVersionDict)
            EvoCdifWriter.generateFunctionVersionEntityInfo(invokeableEntityDict.functionVersionDict)
            print("Writing accessible entity version data to CDIF")
            EvoCdifWriter.generateAttributeVersionEntityInfo(attrDict.attributeVersionDict)
            EvoCdifWriter.generateGlobalVariableVersionEntityInfo(attrDict.globalVarVersionDict)        
        
        output_handle.close()
        
        if self.reprocess:
            os.remove(cdifFile)
        else:
            backup.discardBackup()
            
    def getCodeFolder(self, options):
        folder = options.getWorkFolder()
        if self.repositoryType == "git":
            folder += os.sep + options.getRepositoryRoot()
        return folder            
            
    def transactionHasSourceChanges(self, transaction):

        revisionList = transaction.getRevisions().values()
        deletedList = transaction.getDeletedRevisions().values()
        return self.revisionsHaveSourceChanges(revisionList) or \
               self.revisionsHaveSourceChanges(deletedList)
    
    def revisionsHaveSourceChanges(self, revisionList):

        sourceExtensions = evo.common.globals.Globals.sourceExtensions
        
        result = False
        
        for revision in revisionList:
            sourceFile = revision.getSourceFile()
            if sourceFile.getExtension() in sourceExtensions:
                result = True
                break           
            
        return result
    
    def filterConditionalCompilation(self, condCompDbLoc, fileDictionary):
        
        newFileName = condCompDbLoc + '.new'
        newFile = open(newFileName, "w")
        dumpFile = open(condCompDbLoc, "r")        

        fileList = fileDictionary.getFileList()

        for line in dumpFile:
            dumpLine = line.strip()
            sourceFile = '/' + dumpLine.split(":")[0]           
            if sourceFile in fileList:
                newFile.write(line)
                
        dumpFile.close()
        newFile.close()

        os.remove(condCompDbLoc)
        os.rename(newFileName, condCompDbLoc)
        
    def filterNamespaces(self, namespaceDbLoc, fileDictionary):

        newFileName = namespaceDbLoc + '.new'
        newFile = open(newFileName, "w")
        dumpFile = open(namespaceDbLoc, "r")        

        fileList = fileDictionary.getFileList()

        for line in dumpFile:
            dummyEntity = NamespaceEntity(line.strip())
            if len(dummyEntity.cols) == 4:
                sourceFile = '/' + dummyEntity.getDeclaringFileName()           
                if sourceFile in fileList:
                    newFile.write(line)
                
        dumpFile.close()
        newFile.close()

        os.remove(namespaceDbLoc)
        os.rename(newFileName, namespaceDbLoc)        

    def filterTypedefs(self, typedefDbLoc, fileDictionary):

        newFileName = typedefDbLoc + '.new'
        newFile = open(newFileName, "w")
        dumpFile = open(typedefDbLoc, "r")        

        fileList = fileDictionary.getFileList()

        for line in dumpFile:
            dummyEntity = TypeDefEntity(line)
            sourceFile = '/' + dummyEntity.sourceFile           
            if sourceFile in fileList:
                newFile.write(line)
                
        dumpFile.close()
        newFile.close()

        os.remove(typedefDbLoc)
        os.rename(newFileName, typedefDbLoc)        

    def filterInheritance(self, inDbLoc, fileDictionary):

        newFileName = inDbLoc + '.new'
        newFile = open(newFileName, "w")
        dumpFile = open(inDbLoc, "r")        

        fileList = fileDictionary.getFileList()

        for line in dumpFile:
            dummyEntity = InheritanceEntity(line)
            sourceFile = '/' + dummyEntity.sourceFile           
            if sourceFile in fileList:
                newFile.write(line)
                
        dumpFile.close()
        newFile.close()

        os.remove(inDbLoc)
        os.rename(newFileName, inDbLoc)        
            
    def filterPmcMetrics(self, metrics_file, fileDictionary):

        newFileName = metrics_file + '.new'
        newFile = open(newFileName, "w")
        dumpFile = open(metrics_file, "r")        

        fileList = fileDictionary.getFileList()

        for line in dumpFile:
            pmcEnt = PmcMetricEntity(line)
            sourceFile = '/' + pmcEnt.filename           
            if sourceFile in fileList:
                newFile.write(line)
                
        dumpFile.close()
        newFile.close()

        os.remove(metrics_file)
        os.rename(newFileName, metrics_file)
        
    def filterAttributes(self, attrDbLoc, fileDictionary):
        
        newFileName = attrDbLoc + '.new'
        newFile = open(newFileName, "w")
        dumpFile = open(attrDbLoc, "r")        

        fileList = fileDictionary.getFileList()

        for line in dumpFile:
            attribute = AttributeEntity(line)
            attrRef = attribute.getReference()
            sourceFile = '/' + attrRef.getSourceFile()           
            if sourceFile in fileList:
                newFile.write(line)
                
        dumpFile.close()
        newFile.close()

        os.remove(attrDbLoc)
        os.rename(newFileName, attrDbLoc)
            
    def filterGlobalVars(self, gvDbLoc, fileDictionary):
        
        newFileName = gvDbLoc + '.new'
        newFile = open(newFileName, "w")
        dumpFile = open(gvDbLoc, "r")        

        fileList = fileDictionary.getFileList()

        for line in dumpFile:
            gv = GlobalVariableEntity(line)
            gvRef = gv.getReference()
            sourceFile = '/' + gvRef.getSourceFile()           
            if sourceFile in fileList:
                newFile.write(line)
                
        dumpFile.close()
        newFile.close()

        os.remove(gvDbLoc)
        os.rename(newFileName, gvDbLoc)
        
    def filterAccesses(self, referencesDbLoc, fileDictionary):
            
        newFileName = referencesDbLoc + '.new'
        newFile = open(newFileName, "w")
        dumpFile = open(referencesDbLoc, "r")        

        fileList = fileDictionary.getFileList()

        for line in dumpFile:
            access = AccessEntity(line)
            access.determineSourceLocation()
            sourceFile = '/' + access.sourceFile           
            if sourceFile in fileList:
                newFile.write(line)
                
        dumpFile.close()
        newFile.close()

        os.remove(referencesDbLoc)
        os.rename(newFileName, referencesDbLoc)
        
    def writeTransactionFilesToFile(self, transaction, outputFileName):
        sourceExtensions = evo.common.globals.Globals.sourceExtensions
        outputFile = open(outputFileName, "w")
        outputFile.close()
        outputFile = open(outputFileName, "a+")
        revisions = transaction.getRevisions()
        for revision in revisions.values():
            sourceFile = revision.getSourceFile()
            if sourceFile.getExtension() in sourceExtensions:
                outputFile.write(sourceFile.getUniqueName()[1:])
                outputFile.write("\n")
        outputFile.close()        

    def setupDummyFile(self, dummyFile):
        dummyHandle = open(dummyFile, "w")
        dummyHandle.close()
        dummyHandle = open(dummyFile, "a+")
        cdifWriter.set_outputhandle(dummyHandle)
        self.saveCdifCounter = cdifWriter.IDCounter
        return dummyHandle
        
    def destroyDummyFile(self, dummyFile, dummyHandle, outputHandle):
        dummyHandle.close()
        os.remove(dummyFile)
        cdifWriter.set_outputhandle(outputHandle)
        cdifWriter.IDCounter = self.saveCdifCounter
        
class BuilderOptions:
    def __init__(self):
        self.workFolder = None
        self.dataFolder = None
        self.repository = None
        self.repositoryRoot = None
        self.repositoryProjectName = None
        self.famixLevel = 2
        
    def getWorkFolder(self):
        return self.workFolder
    
    def setWorkFolder(self, workFolder):
        self.workFolder = workFolder
        
    def getDataFolder(self):
        return self.dataFolder
    
    def setDataFolder(self, dataFolder):
        self.dataFolder = dataFolder
        
    def getBackupFolder(self):
        return self.workFolder + os.sep + 'backup'
        
    def getRepository(self):
        return self.repository
    
    def setRepository(self, repository):
        self.repository = repository

    def getRepositoryRoot(self):
        return self.repositoryRoot
    
    def setRepositoryRoot(self, repositoryRoot):
        self.repositoryRoot = repositoryRoot
        
    def getRepositoryProjectName(self):
        return self.repositoryProjectName
    
    def setRepositoryProjectName(self, repositoryProjectName):
        self.repositoryProjectName = repositoryProjectName
        
    def getFamixLevel(self):
        return self.famixLevel
    
    def setFamixLevel(self, famixLevel):
        if famixLevel < 2 or famixLevel > 3:
            raise Exception('Only FAMIX levels 2 and 3 are supported')
        else:
            self.famixLevel = famixLevel
            
        
class ExtendedCVSRepository(CVSRepository):

    def checkout (self, uri, rootdir, newdir = None, branch = None, rev = None, dateStamp = None):
        '''Checkout a module or path from repository

        @param uri: Module or path to check out. When using as a path
            it should be relative to the module being the module name
            the root. modulename/path/to/file
        '''
        
        # TODO: In CVS branch and rev are incompatible, we should 
        # raise an exception if both parameters are provided and 
        # use them, it doesn't matter which, when only one is provided.
        if newdir is not None:
            srcdir = os.path.join (rootdir, newdir)
        elif newdir == '.' or uri == '.':
            srcdir = rootdir
        else:
            srcdir = os.path.join (rootdir, uri)
        if os.path.exists (srcdir):
            try:
                self.update (srcdir, rev, dateStamp)
                return
            except RepositoryInvalidWorkingCopy:
                # If srcdir is not a valid working copy,
                # continue with the checkout
                pass

        cmd = ['cvs', '-z3', '-q', '-d', self.uri, 'checkout', '-P']

        if rev is not None:
            cmd.extend (['-r', rev])

        if newdir is not None:
            cmd.extend (['-d', newdir])
            
        if dateStamp is not None:
            cmd.extend (['-D', dateStamp])
        
        cmd.append (uri)
        command = Command (cmd, rootdir)
        self._run_command (command, CHECKOUT)

    def update (self, uri, rev = None, dateStamp = None):
        self._check_srcdir (uri)

        cmd = ['cvs', '-z3', '-q', '-d', self.uri, 'update', '-P', '-d']

        if rev is not None:
            cmd.extend (['-r', rev])

        if dateStamp is not None:
            cmd.extend (['-D', dateStamp])

        if os.path.isfile (uri):
            directory = os.path.dirname (uri)
            cmd.append (os.path.basename (uri))
        else:
            directory = uri
            cmd.append ('.')
            
        command = Command (cmd,directory)
        self._run_command (command, UPDATE)
        
class ExtendedGitRepository(GitRepository):
    
    def _checkout_branch (self, path, branch):
        self._check_uri (path)

        current, branches = self._get_branches (path)

        if branch in branches:
            if branches.index (branch) == current:
                return

            cmd = ['git', 'checkout', '-b', branch, 'origin/%s' % (branch)]
        else:
            cmd = ['git', 'checkout', branch]
            
        command = Command (cmd, path)
        command.run ()

    def update (self, uri, rev = None):
        self._check_uri (uri)

        branch = rev
        if branch is not None:
            self._checkout_branch (uri, branch)
        
        cmd = ['git', 'fetch']

        if os.path.isfile (uri):
            directory = os.path.dirname (uri)
        else:
            directory = uri

        command = Command (cmd, directory)
        self._run_command (command, UPDATE)
