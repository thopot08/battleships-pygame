# first line to create the file if it doesn't already exist
try:
    f = open("playerdata.txt","r")
    f.read()
    f.close()
    print("nothing bad happened")
except FileNotFoundError:
    with open("playerdata.txt","w") as file:
        for i in range(1,5):
            file.write(f"p{i}name:player {i}\n")
            file.write(f"p{i}ownedskins:placeholder,\n")
            file.write(f"p{i}currency:100\n")
    print("player data file was created")

def changeMoney(player,increment): # for player use p1,p2,p3,p4
    with open("playerdata.txt","r") as file:
        lines = file.readlines()
        for line in lines:
            data = line.split(":")
            if data[0] == f"{player}currency":
                data[1] = int(data[1]) + increment
                newcurrency = data[1]

    with open("playerdata.txt","w") as file:
        for line in lines:
            data = line.split(":")
            if data[0] == f"{player}currency":
                file.write(f"{player}currency:{newcurrency}\n")
            else:
                file.write(line)

def changeName(player,newname):
    with open("playerdata.txt","r") as file:
        lines = file.readlines()
        
    with open("playerdata.txt","w") as file:
        for line in lines:
            data = line.split(":")
            if data[0] == f"{player}name":
                file.write(f"{player}name:{newname}\n")
            else:
                file.write(line)

def fetchData(wanted):
    with open("playerdata.txt","r") as file:
        lines = file.readlines()
        for line in lines:
            data = line.split(":")
            if data[0] == wanted:
                return data[1].strip() # .strip to remove the \n on the end of the text (this was making a weird box on the pygame gui)

def printdata():
    with open("playerdata.txt","r") as file:
        print(file.read())
