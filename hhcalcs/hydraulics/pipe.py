"""
PIPE CLASS OBJECT DEFINITION
"""
from hhcalcs import hydraulics as h

ASSUMED_GRADE = 0.5

class Pipe(object):

    def __init__ (self, cursor=None):

        """
        initialize by passing in a arcpy cursor object
        """
        self.slope = cursor.getValue("Slope")
    	self.length = cursor.shape.length
    	self.diameter = cursor.getValue("Diameter")
    	self.height = cursor.getValue("Height")
    	self.width = cursor.getValue("Width")
        self.shape = cursor.getValue("PIPESHAPE")
    	self.up_elev = cursor.getValue("UpStreamElevation")
    	self.dn_elev = cursor.getValue("DownStreamElevation")
    	self.objectid = cursor.getValue("OBJECTID")
        #self.label = cursor.getValue("LABEL")

        #data quality parameters
        self.calculatedSlope = False
        self.minSlopeAssumed = False


        #calculate values based on attributes
        self.improve_slope() #attempt to fix Null slope values
        self.velocity = h.manningsVelocity(height=self.height,
                                            width=self.width,
                                            slope=self.slope,
                                            shape=self.shape,
                                            diameter=self.diameter)

        self.xarea = h.xarea(self.shape, self.diameter, self.height, self.width)
        self.capacity = self.velocity * self.xarea
        self.travel_time = (self.length / self.velocity) / 60.0 # minutes

    def __str__(self):

        if self.diameter is not None:
            return "{} {}".format(self.diameter, self.shape)
        else:
            return "{}x{} {}".format(self.height, self.width, self.shape)

    def improve_slope(self):

        """
        if slope data is null, try to calculate the slope. if not possible,
        assume a minimum value
        """

        if self.slope is None:
            #NO slope is found in existing table, so try to calculate one
            if (self.up_elev is not None) and (self.dn_elev is not None):
                self.slope = ( (self.up_elev - self.dn_elev) / self.length ) * 100.0 #percent
                #pipe.setValue("Hyd_Study_Notes", "Autocalculated Slope")
                self.calculatedSlope = True
                print 'calculated slope'
            else:
                self.slope = ASSUMED_GRADE
                print 'assumed slope = {}'.format(ASSUMED_GRADE)
                self.minSlopeAssumed = True
                arcpy.AddMessage("\t min slope assumed = " + str(S)  + ", ID = " + str(id))

    def calulate_velocity(self):
        """
        Attempt to calculate the travel time of the full flowing pipe
        """
        # try:
            #compute pipe velocity
        self.velocity = hydraulics.manningsVelocity(height=self.height,
                                                    width=self.width,
                                                    slope=self.slope,
                                                    shape=self.shape,
                                                    diameter=self.diameter)
        # except:
        #     self.velocity = None

    def calculate_capacity(self):
        """
        compute full flow capacity
        """

        self.cross_sectional_area = hydraulics.xarea(self.shape, self.diameter,
                                                     self.height, self.width)

        self.capacity = self.velocity * self.cross_sectional_area

    def calculate_travel_time(self):


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
