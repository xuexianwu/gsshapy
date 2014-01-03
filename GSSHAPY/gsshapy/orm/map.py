'''
********************************************************************************
* Name: RaserMapModel
* Author: Nathan Swain
* Created On: August 1, 2013
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
'''

__all__ = ['RasterMapFile']

import subprocess


import xml.etree.ElementTree as ET
import xml.dom.minidom

from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import relationship

from mapkit.sqlatypes import Raster
from mapkit.RasterLoader import RasterLoader

from gsshapy.orm import DeclarativeBase
from gsshapy.orm.file_base import GsshaPyFileObjectBase

from mapkit.RasterConverter import RasterConverter

class RasterMapFile(DeclarativeBase, GsshaPyFileObjectBase):
    '''
    '''
    __tablename__ = 'raster_maps'
    
    tableName = __tablename__ #: Database tablename
    
    # Primary and Foreign Keys
    id = Column(Integer, autoincrement=True, primary_key=True) #: PK
    projectFileID = Column(Integer, ForeignKey('prj_project_files.id')) #: FK
    
    # Value Columns
    fileExtension = Column(String, nullable=False) #: STRING
    raster_text = Column(String) #: STRING
    raster = Column(Raster) #: RASTER
    
    # Relationship Properites
    projectFile = relationship('ProjectFile', back_populates='maps') #: RELATIONSHIP
    
    def __init__(self, directory, filename, session):
        '''
        Constructor
        '''
        GsshaPyFileObjectBase.__init__(self, directory, filename, session)
        
    def __repr__(self):
        return '<RasterMap: FileExtension=%s>' % (self.fileExtension)
    
    def _read(self):
        '''
        Raster Map File Read from File Method
        '''
        # Assign file extension attribute to file object
        self.fileExtension = self.EXTENSION
        
        # Open file and read plain text into text field
        with open(self.PATH, 'r') as f:
            self.raster_text = f.read()
            
        if self.SPATIAL:
            # Get well known binary from the raster file using the MapKit RasterLoader
            wkbRaster = RasterLoader.rasterToWKB(self.PATH, str(self.SRID), '0', self.RASTER2PGSQL_PATH)
            self.raster = wkbRaster         
        
    def _write(self, session, openFile):
        '''
        Raster Map File Write to File Method
        '''
        # If the raster field is not empty, write from this field
#         if self.raster != None:
        if type(self.raster) != type(None):
            '''
            '''
            # Use the ST_AsGDALRaster function of PostGIS to retrieve the 
            # raster as an ascii grid. Function defined as per instructions
            # to make a geoalchemy function from 
            # see: http://www.postgis.org/documentation/manual-svn/RT_ST_AsGDALRaster.html
            # Cast as a string because ST_AsGDALRaster returns as a buffer object
            arcInfoGrid = str(session.scalar(self.raster.ST_AsGDALRaster('AAIGRID'))).splitlines()
            
            ## Convert arcInfoGrid to GRASS ASCII format ##
            # Get values from heaser which look something this:
            # ncols        67
            # nrows        55
            # xllcorner    425802.32143212341
            # yllcorner    44091450.41551345213
            # cellsize     90.0000000
            # ...
            nCols = int(arcInfoGrid[0].split()[1])
            nRows = int(arcInfoGrid[1].split()[1])
            xLLCorner = float(arcInfoGrid[2].split()[1])
            yLLCorner = float(arcInfoGrid[3].split()[1])
            cellSize = float(arcInfoGrid[4].split()[1])
            
            # Remove old headers
            for i in range(0, 5):
                arcInfoGrid.pop(0)
            
            ## Calculate values for GRASS ASCII headers ##
            # These should look like this:
            # north: 4501028.972140
            # south: 4494548.972140
            # east: 460348.288604
            # west: 454318.288604
            # rows: 72
            # cols: 67
            # ...
            
            # xLLCorner and yLLCorner represent the coordinates for the Lower Left corner of the raster
            north = yLLCorner + (cellSize * nRows)
            south = yLLCorner
            east = xLLCorner + (cellSize * nCols)
            west = xLLCorner
            
            # Create header Lines (the first shall be last and the last shall be first)
            grassHeader = ['cols: %s' % nCols,
                           'rows: %s' % nRows,
                           'west: %s' % west,
                           'east: %s' % east,
                           'south: %s' % south,
                           'north: %s' % north]
            
            # Insert grass headers into the grid
            for header in grassHeader:
                arcInfoGrid.insert(0, header)
            
            # Write to file  
            for line in arcInfoGrid:
                openFile.write(line.strip() + '\n')
        else:
            # Write file
            openFile.write(self.raster_text)
            
    def getAsKmlGrid(self, session, path, colorRamp=None, alpha=1.0):
        '''
        Get the raster in KML format
        '''
          
        if type(self.raster) != type(None):
            # Make sure the raster field is valid
            converter = RasterConverter(sqlAlchemySession=session)
            
            # Configure color ramp
            converter.setColorRamp(colorRamp)
            
            kmlString = converter.getAsKmlGrid(tableName=self.tableName,
                                               rasterId=self.id,
                                               rasterIdFieldName='id',
                                               documentName=self.fileExtension,
                                               alpha=alpha)
            
            with open(path, 'w') as f:
#                 pretty = xml.dom.minidom.parseString(kmlString)
#                 f.write(pretty.toprettyxml())
                f.write(kmlString)
            
            

