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

from evo.cdif2rsf.writeRevisions import importRevisions
from evo.common.dictionaries.ReleaseRevisionDict import ReleaseRevisionDictionary
from evo.common.objects.ReleaseRevisionEntity import ReleaseRevisionEntity
from evo.common.processing.Utils import setRSFCounter
from common.output.cdifWriter import requestNewCdifId

def buildReleaseRevisionDict(cdifFile, releaseRevisionDict):
    
    """ Reads release revisions from a CDIF file into a dictionary """
    for line in cdifFile:
        line = line.strip()
        
        # if the line is the start of an entity
        if line.startswith("(ReleaseRevision FM"):
            releaseRevisionEntity = ReleaseRevisionEntity()
            
            releaseRevisionEntity.setCdifId(int(line.split("M")[1]))
            setRSFCounter(releaseRevisionEntity.getCdifId())
            
            for line in cdifFile:
                line = line.strip()
                if line.startswith("(release "):
                    releaseRevisionEntity.setRelease(line.split("\"")[1])
                elif line.startswith("(revision "):
                    releaseRevisionEntity.setRevision(line.split("\"")[1])
                elif line.startswith(")"):
                    releaseRevisionDict.add(releaseRevisionEntity)
                    break    

def importReleases(releaseDict):

    importReleaseFile = open("releasesWithIDs.txt", 'r')
 
    for line in importReleaseFile:
        line = line.strip()
        lineSplittedInTabs = line.split("\t")
        releaseId = int(lineSplittedInTabs[0])
        releaseName = lineSplittedInTabs[1].split("\"")[1]
   
        if not (releaseName in releaseDict):
            releaseDict[releaseName] = releaseId
    
    importReleaseFile.close()
    
def addReleaseRevisionEntity(releaseRevisionEntity, revisionBelongsToRelease, \
                             releases, revisions):

    releaseName = releaseRevisionEntity.getRelease()
    revisionUniqueName = releaseRevisionEntity.getRevision()
    
    if revisionUniqueName in revisions:
        releaseId = releases[releaseName]
        revisionId = revisions[revisionUniqueName]
    
        if not (revisionId in revisionBelongsToRelease):
            revisionBelongsToRelease[revisionId] = []
        releaseList = revisionBelongsToRelease[revisionId]
        releaseList.append(releaseId)
        
def writeReleaseRevisions(inputFile, control):
    # initialise IDCounter to 1
    requestNewCdifId()

    inputFile = open(inputFile, 'r')
    releaseRevisionDict = ReleaseRevisionDictionary()
    buildReleaseRevisionDict(inputFile, releaseRevisionDict)
    inputFile.close()

    revisionReleaseFile = open("revisionBelongsToRelease.txt", 'w')    
        
    # first build up the relations
    revisionBelongsToRelease = {}
    releases = {}
    revisions = {}

    importReleases(releases)  
    importRevisions(revisions)  
        
    for releaseRevisionEntity in releaseRevisionDict.entityDict.values():
        addReleaseRevisionEntity(releaseRevisionEntity, revisionBelongsToRelease, \
                                 releases, revisions)
    
    indices = revisionBelongsToRelease.keys()
    indices.sort()
    for revisionId in indices:
        releaseList = revisionBelongsToRelease[revisionId]
        releaseList.sort()
        for releaseId in releaseList:
            info = str(revisionId) + "\t" + str(releaseId) + "\n"
            revisionReleaseFile.write(info)
    revisionReleaseFile.close()
                
    return EX_OK
