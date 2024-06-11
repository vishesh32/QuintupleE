import csv

def compare():
    exact = [ [float(line[0]), int(line[1])] for line in csv.reader(open("exact.csv"))]
    polling = [ [float(line[0]), int(line[1])]  for line in csv.reader(open("polling.csv"))]

    del exact[0]

    totalError = 0
    for i in range(min(len(exact), len(polling))):
        totalError += abs(exact[i][0] - polling[i][0])
    
    return totalError / len(exact)

if __name__ == "__main__":
    print(compare())
    