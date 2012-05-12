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

from os import EX_OK

from datetime import datetime

from cdif2rsf.writeFiles import addFileEntity

from common.output.cdifWriter import requestNewCdifId

from evo.common.dictionaries.SourceFileDict import SourceFileDictionary
from evo.common.objects.SourceFileEntity import SourceFileEntity
from evo.common.processing.Utils import convertTimeToUNIX, setRSFCounter

def buildFileDict(cdifFile, fileDict, control):
    """ Reads files from a CDIF file into a dictionary """
    for line in cdifFile:
        line = line.strip()
        
        # if the line is the start of an entity
        if line.startswith("(SourceFile FM"):
            fileEntity = SourceFileEntity()
            
            fileEntity.setCdifId(int(line.split("M")[1]))
            setRSFCounter(fileEntity.getCdifId())
            
            for line in cdifFile:
                line = line.strip()
                if line.startswith("(uniqueName "):
                    fileEntity.setUniqueName(line.split("\"")[1])
                elif line.startswith("(creationTime "):
                    timeString = line.split("\"")[1]
                    fileEntity.setCreationTime(datetime.strptime(timeString, '%Y-%m-%dT%H:%M:%S'))
                elif line.startswith(")"):
                    if control.isTimeValid(fileEntity.getCreationTime()): 
                        fileDict.addPrepared(fileEntity)
                    break

def writeSourceFiles(inputFile, control):
    # initialise IDCounter to 1
    requestNewCdifId()
    
    inputFile = open(inputFile, 'r')
    fileDict = SourceFileDictionary()
    buildFileDict(inputFile, fileDict, control)
    inputFile.close()

    # first build up the relations
    modules=[]            # moduleName    (moduleId = index(moduleName)+1)
    fileBelongsToModule={}         # fileId x moduleId
    moduleBelongsToModule={}     # childModuleId x parentModuleId
    
    for fileEntity in fileDict.entityDict.values():
        addFileEntity(fileEntity, modules, fileBelongsToModule, moduleBelongsToModule)

    # then write everything to file
    modules_file = open("modulesWithIDs.txt", 'w')    
    for moduleName in modules:
        moduleId = "M" + `modules.index(moduleName)+1`
        moduleInfo = moduleId + "\t\"" + moduleName + "\"\n";
        modules_file.write(moduleInfo)
    modules_file.close()

    moduleBelongsToModule_file=open("moduleBelongsToModule.txt", 'w')
    moduleIndices = moduleBelongsToModule.keys()
    moduleIndices.sort()
    for childModuleId in moduleIndices:
        parentModuleId = "M" + `moduleBelongsToModule[childModuleId]`
        moduleBelongsToModuleInfo = "M" + `childModuleId` + "\t" + parentModuleId + "\n"
        moduleBelongsToModule_file.write(moduleBelongsToModuleInfo)
    moduleBelongsToModule_file.close()

    files_file = open("filesWithIDs.txt", 'w')
    timeFile = open("artefactTime.txt", 'a')
    for fileEntity in fileDict.entityDict.values():
        fileId = fileEntity.getCdifId()
        uniqueName = fileEntity.getUniqueName()
        fileInfo = str(fileId) + "\t\"" + uniqueName + "\"\n";
        files_file.write(fileInfo)
        fileCreationTime = convertTimeToUNIX(fileEntity.getCreationTime())
        timeInfo = str(fileId) + "\t\"" + str(fileCreationTime)
        timeFile.write(timeInfo)
    files_file.close()
    timeFile.close()
    
    fileBelongsToModule_file=open("fileBelongsToModule.txt", 'w')
    fileIndices = fileBelongsToModule.keys()
    fileIndices.sort()
    for fileId in fileIndices:
        parentModuleId = "M" + `fileBelongsToModule[fileId]`
        fileBelongsToModuleInfo = str(fileId) + "\t" + parentModuleId + "\n"
        fileBelongsToModule_file.write(fileBelongsToModuleInfo)
    fileBelongsToModule_file.close()
    
    return EX_OK
