#
# LAP StarSim Plugin - Version 0.8
#
# Copyright (C) 2006 Jonas Lindemann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import os, sys, string

import Lap.Job

astrophysicsParams = {
	"dist_start":[1000, "Distance, start value", "kpcs", "int"],
	"dist_incr":[1000, "Distance, increment value", "kpcs", "int"], 
	"dist_end":[5000, "Distance, end value", "kpcs", "int"],
	"exp_start":[28800, "Exposure time, start value", "s", "int"],
	"exp_incr":[28800, "Exposure time, increment value", "s", "int"],
	"exp_end":[28800, "Exposure time, end value", "s", "int"],
	"back":[90.0, "Sky background value, scaled to 28800 seconds", "", "float"]
}

astrophysicsParamOrder = [
	"dist_start",
	"dist_incr",
	"dist_end",
	"exp_start",
	"exp_incr",
	"exp_end"
]

telescopeParams = {
	"diam_start":[40, "Aperture diameter, start value", "m", "int"],
	"diam_incr":[5, "Aperture diameter, increment value", "m", "int"],
	"diam_end":[40, "Aperture diameter, end value", "m", "int"]
}

telescopeParamOrder = [
	"diam_start",
	"diam_incr",
	"diam_end"
]

instrumentalParams = {
	"sampling_factor":[2, "Sampling factor", "", "int"],
	"image_size":[2048, "Image size", "pixels", "int"],
	"reduce_int":[0.05, "Scaling factor for intensities in image", "", "float"]
}

instrumentalParamOrder = [
	"sampling_factor",
	"image_size",
	"reduce_int"
]

psfTypeParams = {
	"psfflag":["opd", "psf type opd/analytical", "", "choice", ["opd", "analytical"]  ],
}

psfTypeOrder = [
	"psfflag"
]

psfAnalyticalParams = {
	"psf_wavelength":[2200, "PSF monochromatic wavelength", "nm", "int"],
	"psf_size":[2047, "PSF matrix size", "pixels", "int"],
	"r0":[0.9, "Ro parameter", "", "float"],
	"act_dist":[1.3, "Actuator distance ", "", "float"]
}

psfAnalyticalOrder = [
	"psf_wavelength",
	"psf_size",
	"r0",
	"act_dist"
]

psfOpdParams = {
	"psf":["","PSF file for image creation", "", "file"],
}

psfOpdParamOrder = [
	"psf"
]
		
dataHandlingParams = {
	"name_prefix":["ocopd", "Name prefix for created image files", "", "string"],
	"object_coordfile":["", "Input data file for foregrpund object", "", "file"],
	"back_coordfile":["", "Input data file for background object", "", "file"],
	"images":["OCOPD", "Subdirectory for output images", "", "string"],
	"figs":["OCOPD", "Subdirectory for output diagrams", "", "string"]
}

dataHandlingParamOrder = [
	"name_prefix",
	"object_coordfile",
	"back_coordfile",
	"images",
	"figs"
]

	
starsimInputTemplate = """
# CONTROL PARAMETERS FOR "STARSIM"  - REVISION 1.2 (2006-11-16/PL)

# ------------------ Image creation: astrophysics

DIST_START=%(dist_start)d                 #  Distance, start value (kpcs)
DIST_INCR=%(dist_incr)d                  #  Distance, increment value  (kpcs)
DIST_END=%(dist_end)d                  #  Distance, end value  (kpcs)
EXP_START=%(exp_start)d                 #  Exposure time, start value (seconds)
EXP_INCR=%(exp_incr)d                  #  Exposure time, increment value  (seconds)
EXP_END=%(exp_end)d                   #  Exposure time, end value  (seconds)
BACK=%(back)s                        #  Sky background value, scaled to 28800 seconds

# ------------------ Image creation: telescope

DIAM_START=%(diam_start)d                   #  Aperture diameter, start value (metres)
DIAM_INCR=%(diam_incr)d                     #  Aperture diameter, increment value  (metres)
DIAM_END=%(diam_end)d                     #  Aperture diameter, end value  (metres)

# ------------------ Image creation: instrumental

SAMPLING_FACTOR=%(sampling_factor)d               #  0.5 milliarcsec pixels
IMAGE_SIZE=%(image_size)d                 #  Image size in pixels (square shape)
REDUCE_INT=%(reduce_int)g                 # Scaling factor for intensities in image

# ------------------ Image creation: PSF analytic case

PSFFLAG=%(psfflag)s                     # "opd" or "analytic"

PSF_WAVELENGTH=%(psf_wavelength)d             #  PSF monochromatic wavelength (nm)
PSF_SIZE=%(psf_size)d                   #  PSF matrix size in pixels
R0=%(r0)g                          #  Ro parameter
ACT_DIST=%(act_dist)g                    #  Actuator distance

# ------------------ Image creation: PSF OPD case

PSF=%(psf)s                # PSF file for image creation

# ------------------ Data handling: naming and directory structure

NAME_PREFIX=%(name_prefix)s               # Name prefix for created image files
IN=indata                       # Directory for input data
OUT=outdata                     # Directory for output data

# INPUT DATA
OBJECT_COORDFILE=%(object_coordfile)s  # Coordinate and magnitude input data file for foregrpund object (cluster)
BACK_COORDFILE=%(back_coordfile)s  # Coordinate and magnitude input data file for background object (field)
COORD_DIR=$IN/FIELDS
PSF_DIR=$IN/PSFS

# OUTPUT DATA
IMAGES=%(images)s                    # Subdirectory for output images
FIGS=%(figs)s                      # Subdirectory for output diagrams
IMAGE_DIR=$OUT/$IMAGES
FIGS_DIR=$OUT/$FIGS


# ------------------ Data analysis and display

PSF_ANAL=2.2y.psf               # Point spread function data file for analysis
MIN_GREY=0                      # Min grey level in fits->jpg translation
MAX_GREY=40                     # Max grey level in fits->jpg translation

# ------------------ Miscellaneous parameters

daophot=daophot.exe
allstar=allstar.exe

# ------------------ Program control, debug parameters

DEBUG=no
DAO_CLEAN=no
DAO_INTERACTIVE=no


#------------------- Export environment
export PATH daophot allstar DEBUG
export COORD_DIR PSF_DIR IMAGE_DIR FIGS_DIR
export DAO_CLEAN DAO_INTERACTIVE MIN_GREY MAX_GREY PSF_SIZE
export SAMPLING_FACTOR DIAM STREHL IMAGE_SIZE BACK
export DIST_START DIST_INCR DIST_END
export DIAM_START DIAM_INCR DIAM_END
export EXP_START EXP_INCR EXP_END
export STREHL_START STREHL_INCR STREHL_END
export OBJECT_COORDFILE BACK_COORDFILE  NAME_PREFIX
export PSFFLAG PSF PSF_ANAL
"""

class CustomTask(Lap.Job.Task):
	def __init__(self):
		Lap.Job.Task.__init__(self)

		self.setDescription("StarSim")
		self.setTaskEditPage("CustomJobPage")

		# Task specific attributes

		attribs = self.getAttributes()
				
		for key in astrophysicsParams.keys():
			attribs[key] = astrophysicsParams[key][0]
		for key in telescopeParams.keys():
			attribs[key] = telescopeParams[key][0]
		for key in instrumentalParams.keys():
			attribs[key] = instrumentalParams[key][0]
		for key in psfTypeParams.keys():
			attribs[key] = psfTypeParams[key][0]
		for key in psfAnalyticalParams.keys():
			attribs[key] = psfAnalyticalParams[key][0]
		for key in psfOpdParams.keys():
			attribs[key] = psfOpdParams[key][0]
		for key in dataHandlingParams.keys():
			attribs[key] = dataHandlingParams[key][0]
							
		attribs["psf_default"] = "PSF.psf"
		attribs["object_coordfile_default"] = "ngc6192-field"
		attribs["back_coordfile_default"] = "backr_field-200"

		# XRSL specific attributes		

		xrslAttribs = self.getXRSLAttributes()
		xrslAttribs["count"] = 1
		xrslAttribs["executable"] = "/bin/sh"
		xrslAttribs["arguments"] = "./run.sh"
		xrslAttribs["runTimeEnvironment"] = "APPS/ASTRO/STARSIM"

		self.addInputFile("run.sh")

		self.addOutputFile("/")
		
	def setMainFile(self, filename):
	
		self.getAttributes()["mainFile"] = filename
		
	def setPSFFilename(self, filename):
		self.getAttributes()["psf"] = filename
		
	def setObjectCoordFilename(self, filename):
		self.getAttributes()["object_coordfile"] = filename
		
	def setBackCoordFilename(self, filename):
		self.getAttributes()["back_coordfile"] = filename
				
	def setup(self):
		
		# Get directory and attributes	
		
		taskDir = self.getDir()
		attribs = self.getAttributes().copy()
		
		# Add input files
		
		self.clearInputFiles()
		
		if attribs["psf"] == "":
			attribs["psf"] = attribs["psf_default"]
		else:
			self.addInputFile(attribs["psf"])

		if attribs["object_coordfile"] == "":
			attribs["object_coordfile"] = attribs["object_coordfile_default"]
		else:
			self.addInputFile(attribs["object_coordfile"])
			
		if attribs["back_coordfile"] == "":
			attribs["back_coordfile"] = attribs["back_coordfile_default"]
		else:
			self.addInputFile(attribs["back_coordfile"])
			
		# Create StarSim input file

		inputFile = file(taskDir+"/starsim_input.sh", "w")
		inputFile.write(starsimInputTemplate % attribs)
		inputFile.close()
		
		self.addInputFile("starsim_input.sh")
		
		# Create shell script
			
		shellFile = file(taskDir+"/run.sh", "w")
		shellFile.write("#!/bin/sh\n")
		shellFile.write("mkdir outdata\n")
		shellFile.write("STARSIM ./starsim_input.sh\n")
		shellFile.close()

		self.addInputFile("run.sh")

		# Create XRSL file
		
		print self.getXRSLAttributes().copy()

		xrslFile = Lap.Job.XRSLFile(self)
		xrslFile.setFilename(taskDir+"/job.xrsl")
		xrslFile.write()

	def clean(self):
		if self.getDir()!="":
			for filename in os.listdir(self.getDir()):
				os.remove(os.path.join(self.getDir(), filename))
