class dat:
    def __init__(self, name):
        self.filename = name
        self.d = {}

        with open(self.filename, 'r') as file:
            f = file.readlines()

            self.col = f[0].split(',')
            
            for line in f[1:]:
                temp = line.split(',')
                self.d[temp[0]] = temp[1:]
            

    def GetDict(self):
        return self.d
    
    def GetCol(self):
        return self.col
    


d = dat("catalog.csv")

#print(d.GetDict())
#print(d.GetCol())