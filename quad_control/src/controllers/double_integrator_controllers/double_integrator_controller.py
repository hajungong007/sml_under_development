#!/usr/bin/env python
# this line is just used to define the type of document

# from .. import controller
from controllers import controller

class DoubleIntegratorController(controller.Controller):

    
    @classmethod
    def description(cls):
        return "Abstract Double Integrator Controller"


    #TODO do these have special parameters?
    def __init__(self, proportional_gain=1.0, derivative_gain=1.0):
        self.__proportional_gain = proportional_gain
        self.__derivative_gain   = derivative_gain
        
        
    def __str__(self):
        string = controller.Controller.__str__(self)
        string += "\nProportional gain: " + str(self.__proportional_gain)
        string += "\nDerivative gain: " + str(self.__derivative_gain)
        return string
    
    
    def get_proportional_gain(self):
        return self.__proportional_gain
        
    
    def get_derivative_gain(self):
        return self.__derivative_gain

        
    #TODO adjust with the special parameters
#    def __str__(self):
#        string = self.description()
#        string += "\nProportional gain: " + self.__proportional_gain
#        string += "\nDerivative gain: " + self.__derivative_gain
#        return string
        
    
    def output(self, position, velocity): 
        raise NotImplementedError()
