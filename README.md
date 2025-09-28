# Kukur-panel
A mc server hosting panel made by me its soo so so simple
to run it (and pull it. It uses python flask and docker)
```
docker pull guacadminad/kukur-panel:latest
```
to run it 
```
docker run -it --rm -p 8080:8080 guacadminad/kukur-panel:latest
```
then it will ask for the start.sh
and bungee.sh directories
make a start.sh using 
```
#!/bin/bash
cd ~/server && java -jar server.jar nogui
```
bungee.sh using
```
#!/bin/bash
cd ~/bungee && java -jar bungee.jar nogui
```
and is your using google cloud and put it in the root directory 
then do this for puttin the sh directories
```
/home/<GMAIL-ACC>/start.sh
/home/<GMAIL-ACC>/bungee.sh
```
then open port 8080
and do start server
and go back on the page and see logs
and i will never add commands support since you should run the server normally onece and op your self
