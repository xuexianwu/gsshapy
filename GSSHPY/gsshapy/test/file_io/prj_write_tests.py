'''
********************************************************************************
* Name: Project File Write Tests
* Author: Nathan Swain
* Created On: June 5, 2013
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
'''

from sqlalchemy import create_engine
from gsshapy.orm import *

# Define the session
engine = create_engine('postgresql://swainn:(|w@ter@localhost:5432/gsshapy_testing')
maker = sessionmaker(bind=engine)
DBSession = maker()

# Write entire project
scenario = DBSession.query(Scenario).filter(Scenario.id == 1).one()
scenario.write(DBSession, '/Users/swainn/testing/write/')


# # Write one at a time
# name = 'parkcity'
# # Get project file from the database and write it out to file
# prjFile = DBSession.query(ProjectFile).filter(ProjectFile.id == 1).one()
# prjFile.write(DBSession, '/Users/swainn/testing/write/', name)
# 
# # Get the mapping table belonging to the project file and write it out to file
# cmtFile = DBSession.query(MapTableFile).filter(MapTableFile.projectFile == prjFile).one()
# cmtFile.write(DBSession, '/Users/swainn/testing/write/', name)

