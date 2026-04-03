
class contraction_scour:
    def __init__(self, edaps, edcs):
        self.edaps = edaps
        self.edcs = edcs

    def calculate_scour(self):
        # Extract necessary values from the dataframes
        Ab = self.edcs["Contracted section main channel flow area (ft^2)"].values[0]
        Aa = self.edaps["Approach section main channel flow area (ft^2)"].values[0]
        Q = self.edaps["Approach section main channel flow (cfs)"].values[0]

        #This line is the equation that calculates the scour depth
        scour_depth = float(Ab) / float(Aa) * (float(Q) / 1000) ** (1/3)

        return scour_depth