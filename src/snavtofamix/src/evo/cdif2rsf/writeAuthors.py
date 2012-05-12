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

from evo.common.objects.AuthorEntity import AuthorEntity
from evo.common.processing.Utils import setRSFCounter

def writeAuthors(inputFile, control):
    
    inputFile = open(inputFile, 'r')
    
    authorsFile = open("authorsWithIDs.txt", 'w')
    nameFile = open("authorsFullNames.txt", 'w')
    emailFile = open("authorsEmailAddresses.txt", 'w') 
    
    for line in inputFile:
        line = line.strip()
        
        # if the line is the start of an entity
        if line.startswith("(Author FM"):
            authorEntity = AuthorEntity()
            
            authorEntity.setCdifId(int(line.split("M")[1]))
            setRSFCounter(authorEntity.getCdifId())
            
            for line in inputFile:
                line = line.strip()
                if line.startswith("(identifier "):
                    authorEntity.setIdentifier(line.split("\"")[1])
                elif line.startswith("(fullName "):
                    authorEntity.setFullName(line.split("\"")[1])
                elif line.startswith("(emailAddress "):
                    authorEntity.setEmailAddress(line.split("\"")[1])
                elif line.startswith(")"):
                    authorId = authorEntity.getCdifId()
                    authorIdentifier = authorEntity.getIdentifier()
                    authorName = authorEntity.getFullName()
                    authorEmail = authorEntity.getEmailAddress()
                    lineToWrite = str(authorId) + "\t\"" + authorIdentifier + "\"\n";
                    authorsFile.write(lineToWrite)
                    if authorName != authorIdentifier:
                        lineToWrite = str(authorId) + "\t\"" + authorName + "\"\n";
                        nameFile.write(lineToWrite)
                    if authorEmail != "":
                        lineToWrite = str(authorId) + "\t\"" + authorEmail + "\"\n";
                        emailFile.write(lineToWrite)
                    break
            
    authorsFile.close()
    nameFile.close()
    emailFile.close()
    
    inputFile.close()
    
    return EX_OK
