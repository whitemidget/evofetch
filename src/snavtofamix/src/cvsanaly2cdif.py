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
import getopt

from evo.common.output import EvoCdifWriter

from evo.common.processing import ExtractorFactory
from evo.common.processing.VersionBuilder import VersionBuilder

from common.output import cdifWriter

from pycvsanaly2.Database import create_database, statement, AccessDenied, DatabaseNotFound, DatabaseDriverNotSupported
from pycvsanaly2.utils import printerr 

class ProjectNotFound(Exception):
    '''Project not found'''
    
def findRepository(db, cnn, projectName):

    cursor = cnn.cursor()
    cursor.execute(statement("SELECT id FROM repositories WHERE name=?", db.place_holder), (projectName,))
    rep = cursor.fetchone()[0]
    cursor.close()
    
    if rep is None:
        raise ProjectNotFound
    
    return rep

def getRepositoryType(db, cnn, repositoryID):
    
    cursor = cnn.cursor()
    cursor.execute(statement("SELECT type FROM repositories WHERE id=?", db.place_holder), (repositoryID,))
    repositoryType = cursor.fetchone()[0]
    cursor.close()
    
    return repositoryType

def usage():
    print "Usage:",sys.argv[0]," [options] projectName repositoryURI"
    print "\tprojectName    -- name of the project in CVSAnalY database"
    print "\trepositoryURI  -- URI of a source control repository to analyse"
    print ""
    print """
Options:

  -h, --help                     Print this usage message.

Database:

      --db-driver                Output database driver [mysql|sqlite] (mysql)
  -u, --db-user                  Database user name (operator)
  -p, --db-password              Database user password
  -d, --db-database              Database name (cvsanaly)
  -H, --db-hostname              Name of the host where database server is running (localhost)
  
Heuristics:

  -w, --window                   Sliding time window to apply to CVS, in seconds (120)

The following environment variables must be set in order to run EvoFETCH:

FETCH    The root directory of the FETCH installation
           (EvoFETCH requires FETCH)
SN_HOME  Refers to the directory containing both the snavigator and dbdump binaries
           (provided by Source Navigator)
PMC      Refers to the pmccabe binary in fetch/bin that suits your platform
           (required by FETCH)
LDIFF    Refers to the directory containing ldiff.pl for source file differencing

"""

def main(argv):
    # Short (one letter) options. Those requiring argument followed by :
    short_opts = "hu:p:d:H:w:"
    # Long options (all started by --). Those requiring argument followed by =
    long_opts = ["help", "db-user=", "db-password=",
                 "db-hostname=", "db-database=", "db-driver=", "window="]

    # Default options
    user = "operator"
    passwd = None
    hostname = "localhost"
    database = "cvsanaly"
    driver = "mysql"
    slidingTimeWindow = 120
    projectName = None
    repositoryUri = None
    
    fetchPath = os.getenv("FETCH")
    if fetchPath is None:
        printerr("FETCH environment variable not set")
        printerr("Use " + sys.argv[0] + " --help for details")
        return 1
        
    snavPath = os.getenv("SN_HOME")
    if snavPath is None:
        printerr("SN_HOME environment variable not set")
        printerr("Use " + sys.argv[0] + " --help for details")
        return 1
        
    pmcPath = os.getenv("PMC")
    if pmcPath is None:
        printerr("PMC environment variable not set")
        printerr("Use " + sys.argv[0] + " --help for details")
        return 1
        
    ldiffPath = os.getenv("LDIFF")
    if ldiffPath is None:
        printerr("LDIFF environment variable not set")
        printerr("Use " + sys.argv[0] + " --help for details")
        return 1

    try:
        opts, args = getopt.getopt (argv[1:], short_opts, long_opts)
    except getopt.GetoptError, e:
        printerr (str (e))
        return 1

    for opt, value in opts:
        if opt in ("-h", "--help", "-help"):
            usage()
            return 0
        elif opt in ("-u", "--db-user"):
            user = value
        elif opt in ("-p", "--db-password"):
            passwd = value
        elif opt in ("-H", "--db-hostname"):
            hostname = value
        elif opt in ("-d", "--db-database"):
            database = value
        elif opt in ("-w", "--window"):
            slidingTimeWindow = int(value)
        elif opt in ("--db-driver"):
            driver = value

    if len (args) <= 1:
        usage()
        return 0
    else:
        projectName = args[0]
        repositoryUri = args[1]
        
    outputFile = projectName + '.cdif'
    
    # Configuration & initialisation of output
    cdifWriter.writeMooseCompliantCdif()
    outputHandle = open(outputFile, "w")
    outputHandle.close()
    outputHandle = open(outputFile, "a+")
    
    EvoCdifWriter.setOutputHandle(outputHandle)
    cdifWriter.set_outputhandle(outputHandle)
    cdifWriter.initializeIDCounter()
    cdifWriter.generateHeader(True, "evofetch", projectName, "4", "C++", "ISO98")

    try:
        db = create_database(driver, database, user, passwd, hostname)
    except AccessDenied, e:
        printerr("Error creating database: %s", (e.message))
        return 1
    except DatabaseNotFound:
        printerr("Database %s doesn't exist. It must be created before running cvsanaly", (database))
        return 1
    except DatabaseDriverNotSupported:
        printerr("Database driver %s is not supported by cvsanaly", (driver))
        return 1
    
    cnn = db.connect()
        
    try:
        repositoryID = findRepository(db, cnn, projectName)
    except ProjectNotFound:
        printerr("Project %s does not exist in the %s database", (projectName, database))
        return 1
    except:
        raise
    
    repositoryType = getRepositoryType(db, cnn, repositoryID);
    
    extractor = ExtractorFactory.createExtractor(repositoryType)
    extractor.setDb(db)
    extractor.setConnection(cnn)
    extractor.setRepositoryId(repositoryID)
    extractor.setProjectName(projectName)
    extractor.setSlidingTimeWindow(slidingTimeWindow)
    
    print "Extracting authors from CVSAnalY database"
    extractor.fetchAuthors()
    print "Extracting revisions from CVSAnalY database"
    extractor.fetchRevisions()
    print "Extracting source files from CVSAnalY database"
    extractor.fetchFiles()
    print "Linking revisions with source files"
    extractor.linkRevisionsAndFiles()
    print "Computing transaction information"
    extractor.fetchTransactions()
    print "Extracting releases from CVSAnalY database"
    extractor.fetchReleases()
    print "Extracting release revisions from CVSAnalY database"
    extractor.fetchReleaseRevisions()
    # extractor.buildSystemVersions()
       
    cnn.close()

    EvoCdifWriter.setExtractor(extractor)
    print "Writing author data to CDIF"
    EvoCdifWriter.generateAuthorEntityInfo()
    print "Writing revision data to CDIF"
    EvoCdifWriter.generateRevisionEntityInfo()
    print "Writing source file data to CDIF"
    EvoCdifWriter.generateFileEntityInfo()
    print "Writing transaction data to CDIF"
    EvoCdifWriter.generateTransactionEntityInfo()
    print "Writing release data to CDIF"
    EvoCdifWriter.generateReleaseEntityInfo()
    print "Writing release revision data to CDIF"
    EvoCdifWriter.generateReleaseRevisionEntityInfo()
    # EvoCdifWriter.generateSystemVersionEntityInfo()
        
    cdifWriter.generatePostamble()
    outputHandle.close()
    
    print "Starting modelling of system versions"

    builder = VersionBuilder()
    builder.setExtractor(extractor)
    builder.setRepositoryUri(repositoryUri)
    builder.setRepositoryType(repositoryType)
    builder.setFolderName(projectName)
    builder.build()

    print "Completed modelling of system versions"
    
if __name__ == "__main__":
    main(sys.argv)

    