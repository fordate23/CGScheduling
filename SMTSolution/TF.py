class TF:

    # list of functions
    def __init__(self, initial_time, transmission_period, payload, delay_req, numberofconf, control_o):
        self.initial_time = initial_time
        self.transmission_period = transmission_period
        self.payload = payload
        self.delay_requirement = delay_req
        self.numberofconfigurations = numberofconf
        self.control_overhead = control_o

    def __str__(self):
        return 'Initial time: %.1f, transmission period: %.1f, payload: %d resource units, delay requirement: %.1f, ' \
               'number of configurations: %d, control overhead: %d resource units' % \
               (self.initial_time,
                self.transmission_period,
                self.payload,
                self.delay_requirement,
                self.numberofconfigurations,
                self.control_overhead)
