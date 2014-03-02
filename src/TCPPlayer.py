# -*- coding: utf-8 -*-

'''
Created on 03.06.2011

@author: alexander
'''

import socket
import threading, time, random, math
import sys

class TCPPlayer:
    
    def __init__(self, FlashVars, gui):
        self.FlashVars = FlashVars
        
        self.gui = gui
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((FlashVars["serverIP"], 8080))
        
        self.hero = {}
        self.ships = {}
        self.boxes = {}
        
        self.shipSelected = {"id": -1}
        
        self.busy = False
        
        self._login()
        
    def _login(self):
        print("Login with userID: " + self.FlashVars["userID"])
        self._send("LOGIN|" + self.FlashVars["userID"] + "|" + self.FlashVars["sessionID"] + "|3.1.5")
        self._send("PNG")
        threading._start_new_thread(self._KeepAlive, ())
        
        threading._start_new_thread(self._MoveAround, ())
        
        self._getCMD()
        
        self.sock.close()
        
    def _KeepAlive(self):
        time.sleep(25)
        self._send("PNG")
        print("Ping ok.")
        
    def _MoveAround(self):
        xmin = 3
        ymin = 6
        
        xmax = 200
        ymax = 125
        
        xcenter = xmin + (xmax - xmin) / 2
        ycenter = ymin + (ymax - ymin) / 2
        
        radius = min(xcenter, ycenter) - 10
        
        self.gui.setDesiredPath(xcenter, ycenter, radius)
        
        current_angle = 0
        
        print("Move Around module started.")
        
        while len(self.hero) == 0:
            print("waiting for hero data...")
            time.sleep(15)

        
        while True:
            if len(self.hero) != 0 and self.busy == False:                
                radians = (current_angle / 180) * math.pi
                
                newx = int((xcenter + math.sin(radians) * radius) * 100)
                newy = int((ycenter + math.cos(radians) * radius) * 100)
                
                print("Flying circle, current angle: " + str(current_angle) + "°, coords: " + str(newx) + "|" + str(newy))
            
                self._MoveTo(newx + random.randint(1, 150), newy + random.randint(1, 150))
                
                current_angle += 3
                
                if current_angle >= 360:
                    current_angle = 0
                    
                
                # collect some boxes    
                if len(self.boxes) != 0:
                    
                    print("collecting boxes that where not handled while flying by")
                    max = 5
                    
                    currentBoxes = []
                    for tmp in self.boxes.keys():
                        currentBoxes.append(tmp)
                    
                    for boxID in currentBoxes:
                        
                        if self.boxes.get(boxID, "d") != "d":
                            _tmp = self.boxes[boxID]
                            
                            self._MoveTo(_tmp["x"], _tmp["y"])
                            self._send("x|" + str(boxID))
                            
                            print ("Collected " + str(boxID))
                            
                            max -= 1
                            if max <= 0:
                                break
                        
                # attack some enemies
                if len(self.ships) != 0:
                    
                    print("attacking some npcs")
                    max = 5
                    
                    currentShips = []
                    for tmp in self.ships.keys():
                        currentShips.append(tmp)
                    
                    for shipID in currentShips:
                        print("checking " + shipID)
                        
                        if self.ships.get(shipID, "d") != "d" and self.ships[shipID]["isNPC"] == 1 and self._ShipDist(shipID) <= 10:
                            self._Attack(shipID)
                            
                            max -= 1
                            if max <= 0:
                                break
                        else:
                            print("no NPC!")
                            
                # get repaired
                if (self.hero["hpmax"] - self.hero["hp"]) > 2000:
                    
                    print("Repairing...")
                    
                    self._send("S|ROB")
                    while (self.hero["hpmax"] - self.hero["hp"]) > 2000:
                        time.sleep(5)
                    
                    print("Done")
            else:
                print("Move Around: busy")
        
            time.sleep(random.randint(30, 60))
        
    def _MoveTo(self, x, y):
        
        speed = ((self.hero["speed"] / 100) / 4) # unsure
        
        self.gui.setMovingLine(int(x), int(y), int(self.hero["x"]), int(self.hero["y"]))
        
        self._send("1|" + str(x) + "|" + str(y) + "|" + str(self.hero["x"]) + "|" + str(self.hero["y"]))
        
        dist = math.sqrt(math.pow(int(x)/100 - int(self.hero["x"])/100, 2) + math.pow(int(y)/100 - int(self.hero["y"])/100, 2))
        dist_DarkOrbit = math.sqrt(math.pow(int(x) - int(self.hero["x"]), 2) + math.pow(int(y) - int(self.hero["y"]), 2))
        waitTime = (dist * speed)
        
        print("Moving. Start: " + str(self.hero["x"]) + "|" + str(self.hero["y"]) + " Target: " + str(x) + "|" + str(y) + " Dist: " + str(dist) + " Wait time: " + str(waitTime))
        self.busy = True
        # make a moving ticker
        ticks = 20
        waitTimeSlice = waitTime / ticks
        for i in range(1, ticks):
            
            timePassed = waitTimeSlice * i
            
            # current pos
            d = (timePassed / waitTime) * dist_DarkOrbit
            
            cx = int(self.hero["x"] - (((int(self.hero["x"]) - int(x)) / dist_DarkOrbit) * d))
            cy = int(self.hero["y"] - (((int(self.hero["y"]) - int(y)) / dist_DarkOrbit) * d))
            
            #print("Currently at " + str(cx) + "|" + str(cy))
            
            self.hero["x"] = cx
            self.hero["y"] = cy
            
            self.gui.setPlayerPos(cx, cy)
            
            time.sleep(waitTimeSlice)
        
        #time.sleep(waitTime)
        self.busy = False
        
        self.hero["x"] = int(x)
        self.hero["y"] = int(y)
        
        self.gui.setPlayerPos(self.hero["x"], self.hero["y"])
        self.gui.killMovingLine()
        
    def _Attack(self, targetID):
        
        
        if self.busy == False:
            print("Attacking " + targetID)
            self.busy = True
            
            if self._ShipDist(targetID) != False:
                d = self.ships[targetID]
                
                # fly close to him
                self._MoveTo(d["x"] + random.randint(1, 20), d["y"] + random.randint(1, 20))
                self.busy = True
            
                self._send("SEL|" + str(targetID))
                
                print("waiting for selection")
                
                c = 0
                while self.shipSelected["id"] != str(targetID):
                    time.sleep(0.5) #wait for ship selection
                    c += 1
                    
                    if c > 50:
                        return False
                    
                print("Attack started.")
                    
                self._send("a|" + str(targetID))
                
                time_passed = 0
                
                while self.ships.get(targetID, "d") != "d": # while he exists
                    d = self.ships[targetID]
                    
                    # follow him!!
                    if self._ShipDist(targetID) > 1.2:
                        if self._ShipDist(targetID) < 20:
                            print("He's escaping - i'm following :)")
                            self._MoveTo(d["x"] + random.randint(1, 20), d["y"] + random.randint(1, 20))
                            self.busy = True
                        else:
                            print("He escaped.")
                            break
                        
                    # rocket launch
                    if time_passed >= 6:
                        print("Sending rocket!")
                        self._send("d|1")
                        self._send("v|" + targetID)
                        
                        time_passed = 0
                        
                    time_passed += 0.3
                        
                    time.sleep(0.3)
                    
                print("Attack successfull!!")
                
            else:
                print("too busy!")
                
            
            
            self.busy = False
            
    def _ShipDist(self, shipID):
        if self.ships.get(shipID, "d") != "d":
            d = self.ships[shipID]
            
            dist = math.sqrt(math.pow(int(d["x"])/100 - int(self.hero["x"])/100, 2) + math.pow(int(d["y"])/100 - int(self.hero["y"])/100, 2))
            
            return dist
            
        else:
            return False
            
        
        
    def _getCMD(self):
        while True:
            if self.gui.closed == True:
                print("quitting!")
                self._send("0|l") #logout
                sys.exit()
                return False
            
            d = self.sock.recv(10240)
            d = d.decode('utf-8')
            
            if d != "":
                _parts = d.split('\x00\r\n')
                
                for Part in _parts:
                    if Part != "":
                        Parts = Part.split("|")
                        
                        if len(Parts) >= 2:
                            if Parts[1] == "I":
                                self._saveHeroInfo(Parts)
                            elif Parts[1] == "A":
                                self._saveHeroAttr(Parts)
                                
                            elif Parts[1] == "C":
                                self._saveShipInfo(Parts)
                            elif Parts[1] == "1":
                                self._saveShipPos(Parts)
                            elif Parts[1] == "R":
                                self._removeShip(Parts)
                                
                            elif Parts[1] == "N":
                                self._selectShip(Parts)
                                
                            elif Parts[1] == "r":
                                self._handleResource(Parts)
                            elif Parts[1] == "q":
                                self._removeResource(Parts)
                                
                            elif Parts[1] == "c":
                                self._handleBox(Parts)
                            elif Parts[1] == "2":
                                self._removeBox(Parts)
                                
                            elif Parts[1] == "8":
                                self._send("LAB|UPD|GET")
                            elif Parts[1] == "LAB":
                                self._send("RDY|MAP")
                            elif Parts[1] == "l":
                                print("QUIT. BYE!")
                                break
                    
                        #print(Parts)
                        
            time.sleep(0.1)
            
    def _removeBox(self, list):
        # 2 resourceID
        
        self.gui.deleteBox(str(list[2]))
        
        if self.boxes.get(str(list[2]), "d") != "d":
            del self.boxes[str(list[2])]
            
    def _handleBox(self, list):
        # 0|c|zytks|2|5727|5739.
        # 2 resourceID
        # 3
        # 4 x
        # 5 y
        
        x = int(list[4]) + random.randint(5, 43)
        y = int(list[5]) - random.randint(5, 43)
        
        print("Found Box @ " + str(x) + "|" + str(y))
        
        self.gui.setBox(str(list[2]), int(list[4]), int(list[5]))
        
        if self.busy == False:
            self.busy = True
            
            self._MoveTo(x, y)
            self._send("x|" + str(list[2]))
            print("Picked up box " + str(list[2]))
            
            self.gui.deleteBox(str(list[2]))
            
        else:
            
            self.boxes[str(list[2])] = {'id': str(list[2]), 'x': x, 'y': y}
            
            
    def _removeResource(self, list):
        # 2 resourceID
        
        self.gui.deleteOre(str(list[2]))
            
    def _handleResource(self, list):
        # 2 resourceID
        # 3 ???
        # 4 x
        # 5 y
        
        
        x = int(list[4]) + random.randint(5, 43)
        y = int(list[5]) - random.randint(5, 43)
        
        print("Found resource @ " + str(x) + "|" + str(y))
        
        self.gui.setOre(str(list[2]), int(list[4]), int(list[5]))
        
        if self.busy == False:
            self.busy = True
            
            if int(list[3]) < 10:
                self._MoveTo(x, y)
                self._send("w|" + str(list[2]))
                print("Picked up " + str(list[2]))
                
                self.gui.deleteOre(str(list[2]))
            
            
    def _selectShip(self, list):
        # 2 userID
        # ...
        
        self.shipSelected = {"id": list[2]}
        print("Selected " + list[2])
                
    
    def _removeShip(self, list):
        # 2 userID
        
        if self.ships.get(list[2], "d") != "d":
            del self.ships[list[2]]
            
            self.gui.deleteShip(list[2])
        
    
    def _saveShipPos(self, list):
        # 2 userID
        # 3 x
        # 4 y
        # 5 ??
        
        if self.ships.get(list[2], "d") != "d" and len(list) >= 5 and list[3] != '' and list[4] != '':
            self.ships[list[2]]["x"] = int(list[3])
            self.ships[list[2]]["y"] = int(list[4])
            
            self.gui.setShip(list[2], int(list[3]), int(list[4]))
            
    def _saveShipInfo(self, list):
        #3 typeID
        #2 userID
        #7 xpos
        #8 ypos
        #? speed
        #6 username
        #5 clanTag
        #9 fractionID
        #10 clanID
        #13 clanDiplomacy
        #11 dailyRank
        #4 expansionstage
        #12 warnicononmap
        #14 galaxygatesfinished
        #16 isNPC
        #17 cloaked
        
        userID = list[2]
        
        assigner = {"userID": 2, "typeID": 3, "x": 7, "y": 8, "username": 6, "clantag": 5, "fractionID": 9,
                    "clanID": 10, "clanDiplomacy": 13, "dailyRank": 11, "expansionStage": 4, "warnIconMap": 12,
                    "galaxyGateFinished": 14, "isNPC": 16, "cloaked": 17}
        
        dat = {}
        for item in assigner.keys():
            if len(list)-1 >= assigner[item]:
                if item != "username" and item != "clantag":
                    dat[item] = int(list[assigner[item]])
                else:
                    dat[item] = list[assigner[item]]
                
        self.ships[userID] = dat
        
        self.gui.setShip(userID, dat["x"], dat["y"])
        #print(self.ships)   
        
    def _saveHeroAttr(self, list):
        # 2 -> type, eg. HPT
        # HPT:
        # 3 -> current
        # 4 -> max
        
        if list[2] == "HPT":
            print("Update my hitpoints to " + list[3] +  "/" + list[4])

            self.hero["hp"] = int(list[3])
            self.hero["hpmax"] = int(list[4])
            
            self.gui.SetText(self.hero["username"] + " - " + str(self.hero["hp"]) + "/" + str(self.hero["hpmax"]) + " HP")
            
    def _saveHeroInfo(self, list):
        # 0, 1 -> useless
        # 2 -> userid
        # 3 -> username
        # 4 -> if == 80 then isCubicon
        # 5 -> speed
        # 8 -> hitpoints
        # 9 -> hitpointsmax
        # 10 -> emptycargo
        # 11 -> maxcargo
        # 12, 13 --> x,y
        # 17 -> maxLaser
        # 18 -> maxRocket
        # 20 -> premium
        # 21 -> XP
        # 23 -> level
        # 24 -> creditsAmount
        # 25 -> uridiumAmount
        # 26 -> jackpotAmount
        #        
        
        assigner = {"username": 3, "hp": 8, "hpmax": 9, "emptycargo": 10, "maxcargo": 11, "x": 12, "y": 13,
                    "maxlaser": 17, "maxrocket": 18, "premium": 20, "xp": 21, "level": 23, "credits": 24,
                    "uridium": 25, "jackpot": 26, "speed": 5}
        
        for item in assigner.keys():
            if item == "jackpot":
                self.hero[item] = float(list[assigner[item]])
            elif item == "speed":
                self.hero[item] = float(list[assigner[item]]) * 0.97
            elif item != "username":
                self.hero[item] = int(list[assigner[item]])
            else:
                self.hero[item] = list[assigner[item]]
        
        self.gui.setPlayerPos(self.hero["x"], self.hero["y"])
        
        self.gui.SetText(self.hero["username"] + " - " + str(self.hero["hp"]) + "/" + str(self.hero["hpmax"]) + " HP")
        
        print(self.hero)
        
    def _send(self, data):
        
        data += "\r\n"
        
        self.sock.send(data.encode('utf-8'))