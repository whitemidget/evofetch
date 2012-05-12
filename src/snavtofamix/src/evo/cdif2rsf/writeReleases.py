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

from evo.common.objects.ReleaseEntity import ReleaseEntity
from evo.common.processing.Utils import convertTimeToUNIX, setRSFCounter

def writeReleases(inputFile, control):
    
    inputFile = open(inputFile, 'r')
    
    releasesFile = open("releasesWithIDs.txt", 'w')
    timeFile = open("artefactTime.txt", 'a')

    for line in inputFile:
        line = line.strip()
        
        # if the line is the start of an entity
        if line.startswith("(Release FM"):
            releaseEntity = ReleaseEntity()
            
            releaseEntity.setCdifId(int(line.split("M")[1]))
            setRSFCounter(releaseEntity.getCdifId())
            
            for line in inputFile:
                line = line.strip()
                if line.startswith("(name "):
                    releaseEntity.setName(line.split("\"")[1])
                elif line.startswith("(creationTime "):
                    timeString = line.split("\"")[1]
                    if timeString != "":
                        releaseEntity.setCreationTime(datetime.strptime(timeString, '%Y-%m-%dT%H:%M:%S'))
                elif line.startswith(")"):
                    releaseId = releaseEntity.getCdifId()
                    releaseName = releaseEntity.getName()
                    lineToWrite = str(releaseId) + "\t\"" + releaseName + "\"\n";
                    releasesFile.write(lineToWrite)
                    if not (releaseEntity.getCreationTime() is None):
                        releaseTime = convertTimeToUNIX(releaseEntity.getCreationTime())
                        timeInfo = str(releaseId) + "\t\"" + str(releaseTime) + "\"\n";
                        timeFile.write(timeInfo)
                    break
            
    releasesFile.close()
    timeFile.close()
    
    inputFile.close()
    
    return EX_OK
