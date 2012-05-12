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
import sys

from os import EX_OK, EX_USAGE, EX_UNAVAILABLE, EX_IOERR

from evo.cdif2rsf.Dictionaries import Dictionaries, TransactionControl
from evo.cdif2rsf.makeRsf import makeRsf
from evo.cdif2rsf.writeAttributes import writeAttributes, writeAttributeEntities
from evo.cdif2rsf.writeAuthors import writeAuthors
from evo.cdif2rsf.writeClasses import writeClasses, writeClassEntities
from evo.cdif2rsf.writeFunctions import writeFunctions, writeFunctionEntities
from evo.cdif2rsf.writeGlobalVariables import writeGlobalVariables, writeGlobalVariableEntities
from evo.cdif2rsf.writeMethods import writeMethods, writeMethodEntities
from evo.cdif2rsf.writeReleaseRevisions import writeReleaseRevisions
from evo.cdif2rsf.writeReleases import writeReleases
from evo.cdif2rsf.writeRevisions import importRevisions, writeRevisions
from evo.cdif2rsf.writeSourceFiles import writeSourceFiles
from evo.cdif2rsf.writeSystemVersions import writeSystemVersions
from evo.cdif2rsf.writeTransactions import importTransactions, writeTransactions

def executeFunctionDictionary(functionDictionary, cdifInputFileName, control, dictionaries):

    if cdifInputFileName != "": 
        print "Reading from file", cdifInputFileName + "..."

    for functionName in functionDictionary.keys():
        functionDescr = functionDictionary.get(functionName)
        functionName = functionDescr[0]
        function = functionDescr[1]
        if callable(function):
            print "\t" + functionName + "...",
            if cdifInputFileName == "":
                return_code = function(dictionaries)
            elif dictionaries is None:
                return_code = function(cdifInputFileName, control)
            else:
                return_code = function(cdifInputFileName, dictionaries)
            if return_code == EX_OK:
                print "[ok]"
            else:
                print "[failed]"
                return EX_UNAVAILABLE 
            
    return EX_OK   

def convertToRsf(cdifInputFileName, rsfOutputFileName, workingFolder, control):
        
    dotSeparatedItems = cdifInputFileName.split(".")
    dotSeparatedItems.pop()
    projectFile = '.'.join(dotSeparatedItems)

    functionDictionary = {
        1: ["Authors", writeAuthors],
        2: ["Transactions", writeTransactions],
        3: ["Source files", writeSourceFiles],
        4: ["Revisions", writeRevisions],
        5: ["Releases", writeReleases],
        6: ["Release revisions", writeReleaseRevisions],
        7: ["System versions", writeSystemVersions]
    }
    
    versionFunctionDictionary = {
        1: ["Classes", writeClasses],
        2: ["Methods", writeMethods],
        3: ["Functions", writeFunctions],
        4: ["Attributes", writeAttributes],
        5: ["Global variables", writeGlobalVariables]
    }
    
    entityFunctionDictionary = {
        1: ["Classes", writeClassEntities],
        2: ["Methods", writeMethodEntities],
        3: ["Functions", writeFunctionEntities],
        4: ["Attributes", writeAttributeEntities],
        5: ["Global variables", writeGlobalVariableEntities]
    }
        
    print "(1/6) Generating SCM data"

    progressResult = executeFunctionDictionary(functionDictionary, cdifInputFileName, \
                                               control, None)
    if progressResult <> EX_OK:
        return progressResult    
    
    print "(2/6) Reading transaction information...",
    transactions = {}
    importTransactions(transactions, True)
    transactionIDList = transactions.keys()
    transactionIDList.sort()
    print "[ok]"
    
    print "(3/6) Reading revision information...",
    dictionaries = Dictionaries()
    importRevisions(dictionaries.revisionDict)
    print "[ok]"
    
    print "(4/6) Generating data for software versions" 
       
    for transactionId in transactionIDList:
        transactionName = transactions[transactionId]
        transactionFile = workingFolder + os.sep + "data" + os.sep + projectFile + \
                          '_' + transactionName + '.cdif'
        if os.path.exists(transactionFile):
            progressResult = executeFunctionDictionary(versionFunctionDictionary, \
                                                       transactionFile, \
                                                       None, \
                                                       dictionaries)
            if progressResult <> EX_OK:
                return progressResult
            
    print "(5/6) Generating data for software entities"
    progressResult = executeFunctionDictionary(entityFunctionDictionary, "", None, \
                                               dictionaries)    
    if progressResult <> EX_OK:
        return progressResult    

    print "(6/6) Merging output...",
    return_code = makeRsf(rsf_output_file_name)
    if return_code == EX_OK:
        print "[ok]"
    else:
        print "[failed]"
        return EX_UNAVAILABLE
    
    return_code = cleanup()
    if return_code != EX_OK:
        print "Error cleaning up."
        return EX_IOERR
        
    print "Output written to", rsf_output_file_name
    
    return EX_OK
    

def cleanup():
    remove_command = "rm -f *.txt"
    return os.system(remove_command)

# main                        
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage:",sys.argv[0],"cdif-input-file-name rsf-output-file-name working-folder-name [transaction-limit]"
        print "cdif-input-file       The name of the CDIF file containing the SCM data"
        print "rsf-output-file-name  The name of the RSF file to produce"
        print "working-folder-name   The folder containing the CDIF files for each transaction"
        print "transaction-limit     An optional transaction limit to keep the RSF file small" 
        sys.exit(EX_USAGE)
      
    return_code = cleanup()
    if return_code != EX_OK:
        print "Error cleaning up."
        sys.exit( EX_IOERR )
    
    input_file=sys.argv[1]
    
    cdif_input_file_name = sys.argv[1]
    rsf_output_file_name = sys.argv[2]
    working_folder = sys.argv[3]
    
    if len(sys.argv) > 4:
        max_transactions = int(sys.argv[4])
    else:
        max_transactions = 0;
        
    control = TransactionControl(max_transactions)
    
    exitCode = convertToRsf(cdif_input_file_name, rsf_output_file_name, \
                            working_folder, control)
    
    sys.exit(exitCode)

