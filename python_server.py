import time, socket, json, threading

RECEIVE_BUF = 1024*1024

conn = None
callbacksThread = None

def waitForConnection():
    global conn, callbacksThread
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.bind(("127.0.0.1", 81))
    s.listen(1)
    s.setblocking(1)
    print("Waiting connection from emulator...")
    conn, addr = s.accept()
    conn.setblocking(1)
    conn.settimeout(0.001)
    print("Connected: ", conn)
    callbacksThread = startCallbacksThread()
    print("Thread for listening callbacks from emulator started")

class callbacks:
    functions = {}
    
    callbackList = [
        "emu.registerbefore_callback",
        "emu.registerafter_callback",
        "memory.registerexecute_callback",
        "memory.registerwrite_callback",
    ]
    
    @classmethod
    def registerfunction(cls, func):
        if func == None:
            return 0
        hfunc = hash(func)
        callbacks.functions[hfunc] = func
        return hfunc
        
    @classmethod 
    def error(cls, e):
        emu.message("Python error: " + str(e))
    
    @classmethod
    def checkAllCallbacks(cls, cmd):
        #print("check:", cmd)
        for callbackName in callbacks.callbackList:
            if cmd[0] == callbackName:
                hfunc = cmd[1]
                #print("hfunc:", hfunc)
                func = callbacks.functions.get(hfunc)
                #print("func:", func)
                if func:
                    try:
                        func(*cmd[2:]) #skip function name and function hash and save others arguments
                    except Exception as e:
                        callbacks.error(e)
                        pass
                    #TODO: thread locking
                    sender.send(callbackName + "_finished")

                
class asyncCall:
    @classmethod
    def waitAnswer(cls):
        buf = None
        try:
            buf = conn.recv(RECEIVE_BUF)
        except socket.timeout:
            pass
        return buf
        
class syncCall:
    @classmethod
    def waitUntil(cls, messageName):
        """cycle for reading data from socket until needed message was read from it. All other messages will added in message queue"""
        while True:
            cmd = messages.parseMessages(asyncCall.waitAnswer(), [messageName])
            #print(cmd)
            if cmd != None:
                if len(cmd)>1:
                    return cmd[1]
                return
               
    @classmethod
    def call(cls, *params):
        """wrapper for sending [functionName, [param1, param2, ...]] to socket and wait until client return [functionName_finished, [result1,...]] answer"""
        sender.send(*params)
        funcName = params[0]
        return syncCall.waitUntil(funcName + "_finished")

class sender:
    @classmethod
    def send(cls, *params):
        j = json.dumps(params)
        #print(j)
        return conn.send(j.encode("utf-8"))
    
    
class emu:
    @classmethod
    def poweron(cls):
        return syncCall.call("emu.poweron")
        
    @classmethod
    def pause(cls):
        return syncCall.call("emu.pause")
        
    @classmethod
    def unpause(cls):
        return syncCall.call("emu.unpause")
        
    @classmethod
    def message(cls, str):
        return syncCall.call("emu.message", str)
        
    @classmethod
    def softreset(cls):
        return syncCall.call("emu.softreset")
        
    @classmethod
    def speedmode(cls, str):
        return syncCall.call("emu.speedmode", str)
        
    @classmethod
    def setrenderplanes(cls, sprites, background):
        return syncCall.call("emu.setrenderplanes", sprites, background)
        
    @classmethod
    def framecount(cls):
        return syncCall.call("emu.framecount")
        
    @classmethod
    def lagged(cls):
        return syncCall.call("emu.lagged")
        
    @classmethod
    def lagcount(cls):
        return syncCall.call("emu.lagcount")
     
    @classmethod
    def setlagflag(cls, flag):
        return syncCall.call("emu.setlagflag", flag)
        
    @classmethod
    def emulating(cls):
        return syncCall.call("emu.emulating")
    
    @classmethod
    def paused(cls):
        return syncCall.call("emu.paused")
        
    @classmethod
    def readonly(cls):
        return syncCall.call("emu.readonly")
        
    @classmethod
    def setreadonly(cls, flag):
        return syncCall.call("emu.setreadonly", flag)
        
    @classmethod
    def getdir(cls):
        return syncCall.call("emu.getdir")
        
    @classmethod
    def loadrom(cls, str):
        return syncCall.call("emu.loadrom", str)
        
    @classmethod
    def addgamegenie(cls, str):
        return syncCall.call("emu.addgamegenie", str)
        
    @classmethod
    def delgamegenie(cls, str):
        return syncCall.call("emu.delgamegenie", str)
        
    @classmethod
    def print(cls, str):
        return syncCall.call("emu.print", str)
        
    @classmethod
    def getscreenpixel(cls, x, y, getemuscreen):
        return syncCall.call("emu.getscreenpixel", x, y, getemuscreen)
        
    @classmethod  
    def registerbefore(cls, func):
        hfunc = callbacks.registerfunction(func)
        return syncCall.call("emu.registerbefore", hfunc)
        
    @classmethod  
    def registerafter(cls, func):
        hfunc = callbacks.registerfunction(func)
        return syncCall.call("emu.registerafter", hfunc)

class memory:
    @classmethod
    def readbyte(cls, addr):
        return syncCall.call("memory.readbyte", addr)
        
    @classmethod
    def readbytesigned(cls, addr):
        return syncCall.call("memory.readbytesigned", addr)
        
    @classmethod
    def readword(cls, addr):
        return syncCall.call("memory.readword", addr)
        
    @classmethod
    def readwordsigned(cls, addr):
        return syncCall.call("memory.readwordsigned", addr)
        
    @classmethod
    def writebyte(cls, addr, val):
        return syncCall.call("memory.writebyte", addr, val)
        
    @classmethod
    def readbyterange(cls, addr, size):
        return syncCall.call("memory.readbyterange", addr, size)
    
    @classmethod
    def getregister(cls, name):
        return syncCall.call("memory.getregister", name)
        
    @classmethod
    def setregister(cls, name, value):
        return syncCall.call("memory.setregister", name, value)
        
    @classmethod  
    def registerexecute(cls, addr, size, func):
        hfunc = callbacks.registerfunction(func)
        return syncCall.call("memory.registerexecute", addr, size, hfunc)
        
    @classmethod  
    def registerwrite(cls, addr, size, func):
        hfunc = callbacks.registerfunction(func)
        return syncCall.call("memory.registerwrite", addr, size, hfunc)
        
class rom:
    @classmethod
    def readbyte(cls, addr):
        return syncCall.call("rom.readbyte", addr)
        
    @classmethod
    def readbytesigned(cls, addr):
        return syncCall.call("rom.readbytesigned", addr)
        
    @classmethod
    def writebyte(cls, addr, val):
        return syncCall.call("rom.writebyte", addr, val)
        
class debugger:
    @classmethod
    def hitbreakpoint(cls):
        return syncCall.call("debugger.hitbreakpoint")
        
    @classmethod
    def getcyclescount(cls):
        return syncCall.call("debugger.getcyclescount")
        
    @classmethod
    def getinstructionscount(cls):
        return syncCall.call("debugger.getinstructionscount")
        
    @classmethod
    def resetcyclescount(cls):
        return syncCall.call("debugger.resetcyclescount")
        
    @classmethod
    def resetinstructionscount(cls):
        return syncCall.call("debugger.resetinstructionscount")
        
class joypad:
    @classmethod
    def read(cls, player):
        return syncCall.call("joypad.read", player)
        
    @classmethod
    def readimmediate(cls, player):
        return syncCall.call("joypad.readimmediate", player)
        
    @classmethod
    def readdown(cls, player):
        return syncCall.call("joypad.readdown", player)
        
    @classmethod
    def readup(cls, player):
        return syncCall.call("joypad.readup", player)
       
    @classmethod       
    def write(cls, player, table):
        return syncCall.call("joypad.write", player, table)
        
class zapper:
    @classmethod
    def read(cls):
        return syncCall.call("zapper.read")
        
class input:
    @classmethod
    def read(cls):
        return syncCall.call("input.read")
        
class sound:
    @classmethod
    def get(cls):
        return syncCall.call("sound.get")
        
class movie:

    @classmethod
    def active(cls):
        return syncCall.call("movie.active")
        
    @classmethod
    def mode(cls):
        return syncCall.call("movie.mode")
        
    @classmethod
    def rerecordcounting(cls, counting):
        return syncCall.call("movie.rerecordcounting", counting)

    @classmethod
    def stop(cls):
        return syncCall.call("movie.stop")
        
    @classmethod
    def length(cls):
        return syncCall.call("movie.length")

    @classmethod
    def name(cls):
        return syncCall.call("movie.name")
        
    @classmethod
    def getfilename(cls):
        return syncCall.call("movie.getfilename")

    @classmethod
    def rerecordcount(cls):
        return syncCall.call("movie.rerecordcount")
        
    @classmethod
    def replay(cls):
        return syncCall.call("movie.replay")

    @classmethod
    def readonly(cls):
        return syncCall.call("movie.readonly")
        
    @classmethod
    def setreadonly(cls, readonly):
        return syncCall.call("movie.setreadonly", readonly)
        
    @classmethod
    def recording(cls):
        return syncCall.call("movie.recording")
      
    @classmethod
    def plaing(cls):
        return syncCall.call("movie.plaing")
        
    @classmethod
    def isfromsavestate(cls):
        return syncCall.call("movie.isfromsavestate")
        
class gui:
    @classmethod
    def pixel(cls, x, y, color):
        return syncCall.call("gui.pixel", x, y, color)
        
    @classmethod
    def getpixel(cls, x, y):
        return syncCall.call("gui.getpixel", x, y)
        
    @classmethod
    def line(cls, x1, y1, x2, y2, color, firstskip):
        return syncCall.call("gui.line", x1, y1, x2, y2, color, firstskip)
        
    @classmethod
    def box(cls, x1, y1, x2, y2, fillcolor, outlinecolor):
        return syncCall.call("gui.box", x1, y1, x2, y2, fillcolor, outlinecolor)
     
    @classmethod     
    def text(cls, x, y, str, textcolor, backcolor):
        return syncCall.call("gui.text", x, y, str, textcolor, backcolor)
     
    #@classmethod
    #def parsecolor(cls, col):
    #    return syncCall.call("gui.parsecolor", col)
        
    @classmethod
    def savescreenshot(cls):
        return syncCall.call("gui.savescreenshot") 
        
    @classmethod
    def savescreenshotas(cls, fname):
        return syncCall.call("gui.savescreenshotas", fname)
        
    @classmethod
    def opacity(cls, alpha):
        return syncCall.call("gui.opacity", alpha)
        
    @classmethod
    def transparency(cls, trans):
        return syncCall.call("gui.transparency", trans)


class messages:
    queue = []
    
    @classmethod
    def parseMessages(cls, buf, nameFilterList):
        if buf != None:
            #print(buf, nameFilterList)
            splited = buf.split(b"json")
            for b in splited[1:]:
                try:
                    val = json.loads(b)
                except json.JSONDecodeError as e:
                    print("Can't decode json:", b)
                    raise e
                messages.queue.append(val)
            
        for message in messages.queue:
            if nameFilterList == None or message[0] in nameFilterList:
                messages.queue.remove(message)
                return message
        return None
    

def callbacksThread():
    cycle = 0
    while True:
        cycle += 1
        try:
            cmd = messages.parseMessages(asyncCall.waitAnswer(), callbacks.callbackList)
            if cmd:
                #print("Callback received:", cmd)
                callbacks.checkAllCallbacks(cmd)
            pass
        except socket.timeout:
            pass
        time.sleep(0.001)
    
def startCallbacksThread():
    t = threading.Thread(target = callbacksThread)
    t.daemon = True
    t.start()
    return t
    
if __name__=="__main__":
    waitForConnection()
    while True:
        time.sleep(60)