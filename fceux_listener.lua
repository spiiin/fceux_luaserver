local socket = require("socket.core")
local json = require("json")

function connect(address, port, laddress, lport)
    local sock, err = socket.tcp()
    if not sock then return nil, err end
    if laddress then
        local res, err = sock:bind(laddress, lport, -1)
        if not res then return nil, err end
    end
    local res, err = sock:connect(address, port)
    if not res then return nil, err end
    return sock
end

function bind(host, port, backlog)
    local sock, err = socket.tcp()
    if not sock then return nil, err end
    sock:setoption("reuseaddr", true)
    local res, err = sock:bind(host, port)
    if not res then return nil, err end
    res, err = sock:listen(backlog)
    if not res then return nil, err end
    return sock
end

--sock, err = bind("127.0.0.1", 80, -1)
--print(sock, err)

sock2, err2 = connect("127.0.0.1", 81)
sock2:settimeout(0)
print("Connected", sock2, err2)

function parseEndCallbackCommand(cmd, callbackName)
    if cmd[1] == callbackName then
        return true
    end
    return false
end

function waitUntilCallbackFinished(callbackName)
    --print("waitToEndCallback", callbackName)
    while true do
        local message, err, part = sock2:receive("*all")
        if not message then
            message = part
        end
        if message and string.len(message)>0 then
            --print(message)
            local recCommand = json.decode(message)
            if parseEndCallbackCommand(recCommand, callbackName) then
                return
            else
                --!!! if this is other command, not we are waiting, just send it to global parseCommand coroutine
                table.insert(commandsQueue, recCommand)
                coroutine.resume(parseCommandCoroutine)
            end
        end
    end
end

function emu_registerbeforewrapper(hfunc)
    sendToHost({"emu.registerbefore_callback", hfunc})
    waitUntilCallbackFinished("emu.registerbefore_callback_finished")
end

function emu_registerbefore(hfunc)
    if hfunc == 0 then
        emu.registerbefore(nil)
        return
    end
    emu.registerbefore(function() emu_registerbeforewrapper(hfunc) end)
end

function emu_registerafterwrapper(hfunc)
    sendToHost({"emu.registerafter_callback", hfunc})
    waitUntilCallbackFinished("emu.registerafter_callback_finished")
end

function emu_registerafter(hfunc)
    if hfunc == 0 then
        emu.registerafter(nil)
        return
    end
    emu.registerafter(function() emu_registerafterwrapper(hfunc) end)
end


function memory_registerexecutewrapper(hfunc, addr, size)
    sendToHost({"memory.registerexecute_callback", hfunc, addr, size})
    waitUntilCallbackFinished("memory.registerexecute_callback_finished")
end

function memory_registerexecute(addr, size, hfunc)
    if hfunc == 0 then
        memory.registerexecute(addr, size, nil)
        return
    end
    memory.registerexecute(addr, size, function(addr, size) memory_registerexecutewrapper(hfunc, addr, size) end)
end


function memory_registerwritewrapper(hfunc, addr, size)
    sendToHost({"memory.registerwrite_callback", hfunc, addr, size})
    waitUntilCallbackFinished("memory.registerwrite_callback_finished")
end

function memory_registerwrite(addr, size, hfunc)
    if hfunc == 0 then
        memory.memory_registerwrite(addr, size, nil)
        return
    end
    memory.registerwrite(addr, size, function(addr, size) memory_registerwritewrapper(hfunc, addr, size) end)
end


function sendToHost(cmd)
    local command = json.encode(cmd)
    sock2:send("json"..command) --json prefix for easy splitting group of commands
end

commandTable = {}

methodsNoArgs = {
  ["emu.poweron"] = emu.poweron,
  ["emu.pause"]   = emu.pause,
  ["emu.unpause"] = emu.unpause,
  ["emu.message"] = emu.message,
  ["emu.softreset"] = emu.softreset,
  ["emu.speedmode"] = emu.speedmode,
  --["emu.frameadvance"] = emu.frameadvance, --we can't call it via socket anyway
  ["emu.setrenderplanes"] = emu.setrenderplanes,
  ["emu.framecount"] = emu.framecount,
  ["emu.lagcount"] = emu.lagcount,
  ["emu.lagged"] = emu.lagged,
  ["emu.setlagflag"] = emu.setlagflag,
  ["emu.paused"] = emu.paused,
  ["emu.emulating"] = emu.emulating,
  ["emu.readonly"] = emu.readonly,
  ["emu.setreadonly"] = emu.setreadonly,
  ["emu.getdir"] = emu.getdir,
  ["emu.loadrom"] = emu.loadrom,
  ["emu.registerafter"] = emu_registerafter,
  ["emu.registerbefore"] = emu_registerbefore,
  ["emu.addgamegenie"] = emu.addgamegenie,
  ["emu.delgamegenie"] = emu.delgamegenie,
  ["emu.print"] = emu.print,
  --["emu.getscreenpixel"] = emu.getscreenpixel, --add this manually
  
  ["rom.readbyte"] = rom.readbyte,
  ["rom.readbytesigned"] = rom.readbytesigned,
  ["rom.writebyte"] = rom.writebyte,
  
  ["memory.readbyte"] = memory.readbyte,
  ["memory.readbytesigned"] = memory.readbytesigned,
  ["memory.readword"] = memory.readword,
  ["memory.readwordsigned"] = memory.readwordsigned,
  --["memory.readbyterange"] = memory.readbyterange, --need to encode string to byte values
  ["memory.writebyte"] = memory.writebyte,
  ["memory.registerexecute"] = memory_registerexecute,
  ["memory.registerwrite"] = memory_registerwrite,
  ["memory.getregister"] = memory.getregister,
  ["memory.setregister"] = memory.setregister,
  
  ["joypad.read"] = joypad.read,
  ["joypad.readimmediate"] = joypad.readimmediate,
  ["joypad.readdown"] = joypad.readdown,
  ["joypad.readup"] = joypad.readup,
  ["joypad.write"] = joypad.write,
  
  ["zapper.read"] = zapper.read,
  
  ["input.read"] = input.read,
  
  ["sound.get"] = sound.get,
  
  ["gui.pixel"] = gui.pixel,
  ["gui.getpixel"] = gui.getpixel,
  ["gui.line"] = gui.line,
  ["gui.box"] = gui.box,
  ["gui.text"] = gui.text,
  --["gui.parsecolor"] = gui.parsecolor,
  ["gui.savescreenshot"] = gui.savescreenshot,
  ["gui.savescreenshotas"] = gui.savescreenshotas,
  --["gui.gdscreenshot"] = gui.gdscreenshot,
  --[gui.gdoverlay] = gui.gdoverlay,
  ["gui.opacity"] = gui.opacity,
  ["gui.transparency"] = gui.transparency,
  --["gui.popup"] = gui.popup
  
  ["debugger.hitbreakpoint"] = debugger.hitbreakpoint,
  ["debugger.getcyclescount"] = debugger.getcyclescount,
  ["debugger.getinstructionscount"] = debugger.getinstructionscount,
  ["debugger.resetcyclescount"] = debugger.resetcyclescount,
  ["debugger.resetinstructionscount"] = debugger.resetinstructionscount,
  
  ["movie.active"] = movie.active,
  ["movie.mode"] = movie.mode,
  ["movie.rerecordcounting"] = movie.rerecordcounting,
  ["movie.stop"] = movie.stop,
  ["movie.length"] = movie.length,
  ["movie.name"] = movie.name,
  ["movie.getfilename"] = movie.getfilename,
  ["movie.rerecordcount"] = movie.rerecordcount,
  ["movie.replay"] = movie.replay,
  ["movie.readonly"] = movie.readonly,
  ["movie.setreadonly"] = movie.setreadonly,
  ["movie.recording"] = movie.recording,
  ["movie.playing"] = movie.ispoweron,
  ["movie.isfromsavestate"] = movie.isfromsavestate,
  
}

--for avoiding copypaste, really we can call methods by loadstring(methodName), by it's slower
for methodName, method in pairs(methodsNoArgs) do
    commandTable[methodName] = function(currentCmd)
        --print("cmd:", currentCmd)
        table.remove(currentCmd, 1) -- now currentCmd is argument list
        local result = method(unpack(currentCmd))
        --print("result:", result)
        sendToHost({methodName.."_finished", result})
    end
end

--special case for method that return several values
--emu.getscreenpixel
commandTable["emu.getscreenpixel"] = function(currentCmd)
    --print("cmd:", currentCmd)
    table.remove(currentCmd, 1) -- now currentCmd is argument list
    local r,g,b,pal = emu.getscreenpixel(unpack(currentCmd))
    --print("result:", {r,g,b,pal})
    sendToHost({"emu.getscreenpixel".."_finished", {r,g,b,pal}})
end

--special case for method that return string, need to reencoding it to array, as json can't encode string with non ascii characters
--memory.readbyterange
commandTable["memory.readbyterange"] = function(currentCmd)
    --print("cmd:", currentCmd)
    table.remove(currentCmd, 1) -- now currentCmd is argument list
    local str = memory.readbyterange(unpack(currentCmd))
    arrayWithData = {}
    --reencoode string to table
    str:gsub(".",function(c) table.insert(arrayWithData, string.byte(c)) end)
    --print("result:", arrayWithData)
    sendToHost({"memory.readbyterange".."_finished", arrayWithData})
end

commandsQueue = {}
function parseCommand()
    while true do
        if commandsQueue[1] then
            currentCmd = table.remove(commandsQueue, 1)
            --print("parseCommand:", currentCmd)
            local cmdFunction = commandTable[currentCmd[1]]
            if cmdFunction then cmdFunction(currentCmd) end
        end
        coroutine.yield()
        
    end
end

parseCommandCoroutine = coroutine.create(parseCommand)

function passiveUpdate()
    local message, err, part = sock2:receive("*all")
    if not message then
        message = part
    end
    if message and string.len(message)>0 then
        --print(message)
        local recCommand = json.decode(message)
        table.insert(commandsQueue, recCommand)
        coroutine.resume(parseCommandCoroutine)
    end
end

function main()
    while true do
        passiveUpdate()
        emu.frameadvance()
    end
end

gui.register(passiveUpdate) --undocumented. this function will call even if emulator paused

main()
