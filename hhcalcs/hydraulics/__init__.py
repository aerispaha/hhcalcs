import math
#define default hydraulic params
default_min_slope = 0.01 # percent - assumed when slope is null
default_TC_slope = 5.0 # percent - conservatively assumed for travel time calculation when slope
pipeSizesAvailable = [18,21,24,27,30,36,42,48,54,60,66,72,78,84] #circular pipe sizes in inches



def getMannings( shape, diameter ):
	n = 0.015 #default value
	if ((shape == "CIR" or shape == "CIRCULAR") and (diameter <= 24) ):
		n = 0.015
	elif ((shape == "CIR" or shape == "CIRCULAR") and (diameter > 24) ):
		n = 0.013
	return n

def xarea( shape, diameter, height, width ):
	#calculate cross sectional area of pipe
	#supports circular, egg, and box shape
	if (shape == "CIR" or shape == "CIRCULAR"):
		return 3.1415 * (math.pow((diameter/12.0),2.0 ))/4.0
	elif (shape == "EGG" or shape == "EGG SHAPE"):
		return 0.5105* math.pow((height/12.0),2.0 )
	elif (shape == "BOX" or shape == "BOX SHAPE"):
		return height*width/144.0

def  minSlope( slope ):
	#replaces null slope value with the assumed minimum 0.01%
	if slope == None:
		return 0.01
	else:
		return slope

def hydraulicRadius(shape, diameter, height, width ):
	#calculate full flow hydraulic radius of pipe
	#supports circular, egg, and box shape
	if (shape == "CIR" or shape == "CIRCULAR"):
		return (diameter/12.0)/4.0
	elif (shape == "EGG" or shape == "EGG SHAPE"):
		return 0.1931* (height/12.0)
	elif (shape == "BOX" or shape == "BOX SHAPE"):
		return (height*width) / (2.0*height + 2.0*width) /12.0

def minSlopeRequired (shape, diameter, height, width, peakQ) :

	minV = 2.5 #ft/s
	maxV = 15.0 #ft/s

	try:
		n = getMannings(shape, diameter)
		A = xarea(shape, diameter, height, width)
		Rh = hydraulicRadius(shape, diameter, height, width )

		s =  math.pow( (n * peakQ) / ( 1.49 * A * math.pow(Rh, 0.667) ), 2)
		s = math.ceil(s*10000.0)/10000.0 #round up to nearest 100th of a percent

		s_min_v = math.pow( (n*minV) / (1.49 * math.pow(Rh, 0.667) ) , 2) #lower bound slope based on minimum pipe velocity
		s_max_v = math.pow( (n*maxV) / (1.49 * math.pow(Rh, 0.667) ) , 2) #upper bound slope based on maximum pipe velocity

		#limit slope to bounds based on settling and scouring velocities
		s = max(s, s_min_v)
		s = min(s, s_max_v)

		return round(s*100.0, 2) #percent, round here to fix weird floating point inaccuracy

	except TypeError:
		arcpy.AddWarning("Type error on pipe ")
		return 0.0

def manningsVelocity(diameter=None, slope=None, height=None, width=None, shape="CIR"):

	"""
	returns the velocity of flow in a pipe flowing full
	"""

	#compute mannings flow in full pipe
	A = xarea(shape, diameter, height, width)
	Rh = hydraulicRadius(shape, diameter, height, width)
	n = getMannings(shape, diameter)

	V = (1.49/ n) * math.pow(Rh, 0.667) * math.pow(float(slope)/100.0, 0.5)

	return V


def manningsCapacity(diameter=None, slope=None, height=None, width=None, shape="CIR"):

	#if shape is not CIR, EGG, or BOX, make assumption based on geom provided
	if shape and shape not in ['CIR', 'EGG', 'BOX']:
		if diameter is not None:
			shape = 'CIR'
		elif height is not None:

			if height > 42:
				shape ='BOX' #assume this is a big box
			else:
				shape = 'EGG' #assume egg shape
	# if slope is None:
	# 	slope = 0.5

	#compute mannings flow in full pipe
	A = xarea(shape, diameter, height, width)
	Rh = hydraulicRadius(shape, diameter, height, width)
	n = getMannings(shape, diameter)
	k = (1.49 / n) * math.pow(Rh, 0.667) * A

	Q = k * math.pow(slope/100.0, 0.5)

	return Q

def minimumEquivalentCircularPipe(peakQ, slope):

	#return the minimum ciruclar pipe diameter required to convey a given Q peak
	for D in pipeSizesAvailable:
		q = manningsCapacity(diameter=D, slope=slope, shape="CIR")
		if q > peakQ: return D
