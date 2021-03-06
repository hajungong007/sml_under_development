#!/usr/bin/python

import numpy

import json

from .. import double_integrator_controller as dic

class ComponentWise3DDIC(dic.DoubleIntegratorController):


    @classmethod
    def description(cls):
        return "Double-integrator bounded and component-wise controller" 


    # The class "constructor" - It's actually an initializer
    def __init__(self,
            natural_frequency       = 0.5,
            damping                 = numpy.sqrt(2.0)/2.0,
            proportional_gain       = None,
            derivative_gain         = None,
            position_saturation     = 1.0,
            velocity_saturation     = 1.0
            ):
        
        if proportional_gain is None or derivative_gain is None:
            
            dic.DoubleIntegratorController.__init__(self,
                proportional_gain=natural_frequency**2,
                derivative_gain=2.0*damping*natural_frequency
                )
        
        else:
        
            dic.DoubleIntegratorController.__init__(self,
                proportional_gain=proportional_gain,
                derivative_gain=derivative_gain
                )
            
        self.__position_saturation = position_saturation
        self.__velocity_saturation = velocity_saturation


    def output(self, position, velocity):
        return self._DI_Bounded_Component(position, velocity)


    def __str__(self):
        string = dic.DoubleIntegratorController.__str__(self)
        string += "\nPosition saturation: " + str(self.__position_saturation)
        string += "\nVelocity saturation: " + str(self.__velocity_saturation)
        return string
        
#        description = "Bounded Double Integrator Controller u(p,v) = -sigma(p) - ro(v): simple control law, complicated Lyapunov function\n"
#        controller  = "Parameters: sat(x) = k x/sqrt(1 + x**2), with sigma(p) = kp*sat(p/sigma_p) and ro(p) = kv*sat(v/sigma_v)\n"  
#        parameters  = "kp = " + str(self.kp) + " and kv = " + str(self.kv) + " and sigma_p = " +  str(self.sigma_p) + "and sigma_v = " +  str(self.sigma_v) +"\n\n"
#        return description + controller + parameters


    def _sat(self,x):

        sat     =  x/numpy.sqrt(1.0 + x**2)
        Dsat    =  (1.0 + x**2)**(-3.0/2.0)
        D2sat   =  -3.0*x*(1.0 + x**2)**(-5.0/2.0)
        # primitive of saturation function
        sat_Int =  numpy.sqrt(1.0 + x**2) - 1.0

        return (sat,Dsat,D2sat,sat_Int)


    def _fGain(self,x):

        fgain      =  1.0
        Dfgain     =  0.0
        D2fgain    =  0.0
        # integral of x/fgain(x) from 0 to in
        fgain_int  =  1.0/2.0*x**2
        # integral of sat(x)*Dsat(x)/fgain(x) from 0 to in    
        # fgain_int2 = 1/2*sat(x)**2
        fgain_int2 = 1.0/2.0*x**2/(1.0 + x**2)   

        return (fgain,Dfgain,D2fgain,fgain_int,fgain_int2)

    # print sat(2.0)
    # print fGain(2.0)

    def  _DI_Bounded_Component(self,p,v):

        # gains
        kp = self.get_proportional_gain()
        kv = self.get_derivative_gain()

        sigma_p  = self.__position_saturation
        sigma_v  = self.__velocity_saturation


        sat_p,Dsat_p,D2sat_p,sat_Int_p = self._sat(p/sigma_p)
        sat_v,Dsat_v,D2sat_v,sat_Int_v = self._sat(v/sigma_v)

        fgain,Dfgain,D2fgain,fgain_int,fgain_int2   = self._fGain(v/sigma_v)


        h1     = kp*sigma_p*sat_p
        h1_p   = kp*Dsat_p
        h1_p_p = kp*D2sat_p/sigma_p

        h2     = kv*sigma_v*sat_v
        h2_v   = kv*Dsat_v
        h2_v_v = kv*D2sat_v/sigma_v

        f      = fgain
        f_v    = Dfgain/sigma_v
        f_v_v  = D2fgain/sigma_v**2


        u     = -f*h1 - h2

        u_p   = -f*h1_p
        u_p_p = -f*h1_p_p

        u_v   = -f_v*h1  - h2_v
        u_v_v = -f_v_v*h1 - h2_v_v

        u_p_v = -f_v*h1_p


        beta   = 1.0/(2.0*kp)
        h1_int = kp*(sigma_p**2)*sat_Int_p

        V  = beta*kv**2*h1_int    + \
             beta*h1*h2           + \
             sigma_v**2*fgain_int + \
             h1_int               + \
             beta*kv**2*sigma_v**2*(fgain_int - fgain_int2)

        VD = (-1)*(                    \
                   beta*h2_v*f*h1**2 + \
                   v*h2*(1.0/f - beta*h1_p) + beta/f*h2*(kv**2*v - h2*h2_v)\
                  )
              
        V_p   = beta*kv**2*h1 + beta*h2*h1_p + h1  

        V_v   = beta*h1*h2_v + v/f + beta/f*(kv**2*v - h2*h2_v)

        V_v_p = beta*h1_p*h2_v

        V_v_v = beta*h1*h2_v_v +\
                1.0/f - v/f**2*f_v +\
                (-1.0)*beta/f**2*f_v*(kv**2*v - h2*h2_v) +\
                beta/f*(kv**2 - h2_v*h2_v - h2*h2_v_v)     

        return u,u_p,u_v,u_p_p,u_v_v,u_p_v,V,VD,V_p,V_v,V_v_p,V_v_v


    def  _DI_Bounded_NOT_Component(self,p,v):

        u      = numpy.zeros(3)
        u_p    = numpy.zeros((3,3))
        u_v    = numpy.zeros((3,3))
        u_p_p  = numpy.zeros((3,3,3))
        u_v_v  = numpy.zeros((3,3,3))
        u_p_v  = numpy.zeros((3,3,3))

        # V     = numpy.zeros(1)
        # VD    = numpy.zeros(1)

        V_p   = numpy.zeros(3)
        V_v   = numpy.zeros(3)
        V_v_p = numpy.zeros((3,3))
        V_v_v = numpy.zeros((3,3))

        u[0],u_p[0,0],u_v[0,0],u_p_p[0,0,0],u_v_v[0,0,0],u_p_v[0,0,0],V0,VD0,V_p[0],V_v[0],V_v_p[0,0],V_v_v[0,0] =  \
            self._DI_Bounded_Component(p[0],v[0])

        u[1],u_p[1,1],u_v[1,1],u_p_p[1,1,1],u_v_v[1,1,1],u_p_v[1,1,1],V1,VD1,V_p[1],V_v[1],V_v_p[1,1],V_v_v[1,1] =  \
            self._DI_Bounded_Component(p[1],v[1])

        u[2],u_p[2,2],u_v[2,2],u_p_p[2,2,2],u_v_v[2,2,2],u_p_v[2,2,2],V2,VD2,V_p[2],V_v[2],V_v_p[2,2],V_v_v[2,2] =  \
            self._DI_Bounded_Component(p[2],v[2])

        V  = V0  + V1  + V2
        VD = VD0 + VD1 + VD2

        return u,u_p,u_v,u_p_p,u_v_v,u_p_v,V,VD,V_p,V_v,V_v_p,V_v_v
        
        
       
# Test
#string = DoubleIntegratorBoundedAndComponentWiseController.to_string()
#print string
#con = DoubleIntegratorBoundedAndComponentWiseController.from_string(string)
#print con
#print con.output(zeros(3), zeros(3))
