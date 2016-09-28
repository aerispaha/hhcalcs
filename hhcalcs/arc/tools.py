from hhcalcs import hydraulics

"""
FUNCTIONS COMPLETED ON A ROW WITHIN A arcpy.UpdateCursor()
"""

ASSUMED_GRADE = 0.1 #percent slope
def travel_time(sewer_cursor_row):
    """
    Attempt to calculate the travel time the current pipe
    """
    try:
        #try to read the inpute values
        L 		= sewer_cursor_row.shape.length
        D 		= pipe.getValue("Diameter")
    	H 		= sewer_cursor_row.getValue("Height")
    	W 		= sewer_cursor_row.getValue("Width")
    	shape 	= sewer_cursor_row.getValue("PIPESHAPE")
        S       = sewer_cursor_row.getValue('Slope')

        #compute pipe velocity
        v = hydraulics.manningVelocity(height=H, width=W, slope=S, shape=shape, diameter=D)

        #compute full flow capacity
        capacity = xarea(shape, D, H, W) * v

        pipe.setValue("Capacity", round(capacity, 3))

        #compute travel time in the pipe segment, be conservative if a min slope was used
        if (minSlopeAssumed):
            v_conservative = (1.49/ getMannings(Shape, D)) * math.pow(hydraulicRadius(Shape, D, H, W), 0.667) * math.pow(default_TC_slope/100, 0.5)
            T = (L / v_conservative) / 60 # minutes
        else:
            T = (L / V) / 60 # minutes

        pipe.setValue("TravelTime_min", round(float(T), 3)) #arcpy.AddMessage("time = " + str(T))try:
            # #compute pipe velocity
            # V = (1.49/ getMannings(Shape, D)) * math.pow(hydraulicRadius(Shape, D, H, W), 0.667) * math.pow(float(S)/100.0, 0.5)
            # pipe.setValue("Velocity", round(float(V), 2))
            #
            # #compute the capacity
            # Qmax = xarea(Shape, D, H, W) * V
            # pipe.setValue("Capacity", round(float(Qmax), 2))
            #
            # #compute travel time in the pipe segment, be conservative if a min slope was used
            # if (minSlopeAssumed):
            #     v_conservative = (1.49/ getMannings(Shape, D)) * math.pow(hydraulicRadius(Shape, D, H, W), 0.667) * math.pow(default_TC_slope/100, 0.5)
            #     T = (L / v_conservative) / 60 # minutes
            # else:
            #     T = (L / V) / 60 # minutes
            #
            # pipe.setValue("TravelTime_min", round(float(T), 3)) #arcpy.AddMessage("time = " + str(T))
    except:
        pass
        
def slope(sewer_cursor_row, slope_col='Slope'):

    """
    Attempt to calculate the slope and update a slope column within a arcpy cursor
    """
    S       = sewer_cursor_row.getValue(slope_col) #original slope from DataConv data
    U_el    = sewer_cursor_row.getValue("UpStreamElevation")
    D_el	= sewer_cursor_row.getValue("DownStreamElevation")

    if S is None:
        #NO slope is found in existing table, so try to calculate one
        if (U_el is not None) and (D_el is not None):
            S = ( (U_el - D_el) / L ) * 100.0 #percent
            #pipe.setValue("Hyd_Study_Notes", "Autocalculated Slope")
            calculatedSlope = True
            arcpy.AddMessage("\t calculated slope = " + str(S) + ", ID = " + str(id))
        else:
            S = ASSUMED_GRADE
            #pipe.setValue("Hyd_Study_Notes", "Minimum " + str(S) +  " slope assumed")
            minSlopeAssumed = True
            arcpy.AddMessage("\t min slope assumed = " + str(S)  + ", ID = " + str(id))

        #update the column to reflect the calculayed or assumed slope
        sewer_cursor_row.setValue(slope_col, round(float(S), 2))



def runCalcs (study_pipes_cursor):

    for pipe in study_pipes_cursor:

    	#Grab pipe parameters
    	#S 		= pipe.getValue("Slope_Used") #slope used in calculations
    	S_orig = S = pipe.getValue("Slope") #original slope from DataConv data
    	L 		= pipe.shape.length #access geometry directly to avoid bug where DA perimeter is read after join
    	D 		= pipe.getValue("Diameter")
    	H 		= pipe.getValue("Height")
    	W 		= pipe.getValue("Width")
    	Shape 	= pipe.getValue("PIPESHAPE")
    	U_el	= pipe.getValue("UpStreamElevation")
    	D_el	= pipe.getValue("DownStreamElevation")
    	id 		= pipe.getValue("OBJECTID")
    	#TC		= pipe.getValue("TC_Path")
    	#ss		= pipe.getValue("StudySewer")
    	#tag 	= pipe.getValue("Tag")

    	#boolean flags for symbology
    	missingData = False #boolean representing whether the pipe is missing important data
    	# isTC = checkPipeYN(TC) #False
    	# isSS = checkPipeYN(ss) #False
    	calculatedSlope = False
    	minSlopeAssumed = False

    	#check if slope is Null, try to compute a slope or asssume a minimum value
    	arcpy.AddMessage("checking  pipe "  + str(id))
    	if S_orig is None:
    		if (U_el is not None) and (D_el is not None):
    			S = ( (U_el - D_el) / L ) * 100.0 #percent
    			#pipe.setValue("Hyd_Study_Notes", "Autocalculated Slope")
    			calculatedSlope = True
    			arcpy.AddMessage("\t calculated slope = " + str(S) + ", ID = " + str(id))
    		else:
    			S = default_min_slope
    			#pipe.setValue("Hyd_Study_Notes", "Minimum " + str(S) +  " slope assumed")
    			minSlopeAssumed = True
    			arcpy.AddMessage("\t min slope assumed = " + str(S)  + ", ID = " + str(id))

    	else: S = S_orig #use DataConv slope if provided

    	#pipe.setValue("Slope_Used", round(float(S), 2))



    	# check if any required data points are null, and skip accordingly
    	#logic -> if (diameter or height exists) and (if Shape is not UNK), then enough data for calcs
    	if ((D != None) or (H != None)) and (Shape != "UNK" or Shape != None):

    		try:
    			#compute pipe velocity
    			V = (1.49/ getMannings(Shape, D)) * math.pow(hydraulicRadius(Shape, D, H, W), 0.667) * math.pow(float(S)/100.0, 0.5)
    			pipe.setValue("Velocity", round(float(V), 2))

    			#compute the capacity
    			Qmax = xarea(Shape, D, H, W) * V
    			pipe.setValue("Capacity", round(float(Qmax), 2))

    			#compute travel time in the pipe segment, be conservative if a min slope was used
    			if (minSlopeAssumed):
    				v_conservative = (1.49/ getMannings(Shape, D)) * math.pow(hydraulicRadius(Shape, D, H, W), 0.667) * math.pow(default_TC_slope/100, 0.5)
    				T = (L / v_conservative) / 60 # minutes
    			else:
    				T = (L / V) / 60 # minutes

    			pipe.setValue("TravelTime_min", round(float(T), 3)) #arcpy.AddMessage("time = " + str(T))

    		except TypeError:
    			arcpy.AddWarning("Type error on pipe " + str(pipe.getValue("OBJECTID")))

    	else:
    		missingData = True #not enough data for calcs
    		arcpy.AddMessage("skipped pipe " + str(pipe.getValue("OBJECTID")))


    	#apply symbology tag
    	# theflag = determineSymbologyTag(missingData, isTC, isSS, calculatedSlope, minSlopeAssumed)
    	# pipe.setValue("Tag", str(theflag))

    	study_pipes_cursor.updateRow(pipe)

	del study_pipes_cursor
