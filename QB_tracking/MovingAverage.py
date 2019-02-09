class MovingAverageClass(object):
    def __init__(self,max_terms):
        self.max_terms = max_terms
        self.numbers = [None for n in range(self.max_terms)]
    def add_number(self,number):
        self.numbers[0] = number
    def shift_terms(self):
        #shifts terms at least 1
        self.numbers = [None] + self.numbers[:-1]
    def get_last_term(self):
        for entry in self.numbers :
            if entry is not None:
                return entry
        #otherwise nothing is found
        return None
    def is_list_empty(self):
        return (get_last_term(self) is None)
    def get_moving_average(self):
        simplified_list = []
        for entry in self.numbers :
            if entry is not None:
                simplified_list.append(entry)
        if len(simplified_list)==0:
            return None
        else:
            try:
                return sum(simplified_list)/len(simplified_list)
            except TypeError:
                raise ValueError("Cannot take average of non-float data types. Make sure a add_number is not a truple")
