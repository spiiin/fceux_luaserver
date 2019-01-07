# Fceux_luaserver
Fceux lua socket server and Jupyter Python client

This is proof-of-concept of remote controlling of [Fceux](http://www.fceux.com/web/home.html) NES emulator with Python via sockets.
I use [Jupyter Notebook](https://jupyter.org/) as interactive python environment for controlling emulator. This is also good environment for running examples. 

For checking example:

1. You must have working Python 3 and Jupyter Notebook. Run jupyter with command:
```
jupyter notebook
```

2. Open *FceuxPythonServer.py.ipynb* notebook and run first cell:
![jupyter_1](https://user-images.githubusercontent.com/1622049/50794230-a52f7780-12db-11e9-87b7-7c88b140198c.png)

3. Now you must run fceux emulator with ROM (I used **Castlevania (U) (PRG0) [!].nes** for my examples)
Next, start lua script *fceux_listener.lua*. It must connect to running jupyter python server.
I run emulator, load ROM to it and start lua script with command:
```
fceux.exe -lua fceux_listener.lua "Castlevania (U) (PRG0) [!].nes"
```

4. Now go back to Jupyter Notebook and you must see message about successfull connection:
![jupyter_2](https://user-images.githubusercontent.com/1622049/50794478-461e3280-12dc-11e9-9f33-b0579772130c.png)

You are able to send commands from Jupyter to Fceux (you can execute Notebook cells one by one and see results).
Additionally, I recommend to install some software to pin fceux window on top, so you can see command results in emulator window immediatly. For example, it can be done with [Dexpot](https://www.dexpot.de/index.php?id=features).

Video with results:
https://www.youtube.com/watch?v=c3D5gljbkO0
