# Kukur-panel
![Alt text](Untitled.png)
 # Current Version!! <p align="center">
  <img src="https://img.shields.io/docker/v/anikthedev/kukur-panel?sort=date&label=Version&color=blue" alt="Docker Image Version">
</p>
A mc server hosting panel made by me its soo so so simple
to run it (and pull it. It uses python flask, java (ofc) and docker and no hasty things about users, database and etc. just straight to the point)
```
docker run -d \
  -p 8080:8080 \
  -p 8081:8081 \
  -p 25565:25565 \
  -p 25577:25577 \
  -v /home/yoiwannajinksbegam/server:/app/server \
  -v /home/yoiwannajinksbegam/bungee:/app/bungee \
  -v /home/yoiwannajinksbegam/server.sh:/app/server.sh \
  -v /home/yoiwannajinksbegam/bungee.sh:/app/bungee.sh \
  --name kukur-panel-container \
  anikthedev/kukur-panel:v1.0.3

```
replace the ```/home/yoiwannajinks/<directory>``` with your files okay?
make a start.sh using 
```
#!/bin/bash
cd /app/server
java -Xmx1G -Xms1G -jar server.jar nogui

```
bungee.sh using
```
#!/bin/bash
cd /app/bungee
java -Xmx512M -Xms512M -jar bungee.jar nogui

```
and is your using google cloud and put it in the root directory 
then do this for putting the sh directories
```
/home/<GMAIL-ACC>/start.sh
/home/<GMAIL-ACC>/bungee.sh
```
then open port 8080
and do start server
and go back on the page and see logs
and i will never add commands support since you should run the server normally onece and op your self
# Random Changelog 
1. at first i used docker it was unstable and shitty and didnt work
2. then moved to python so basically gave out the code 
3. then right now reused docker and its v1.0.1 for bcuz its a bugfix or some shit since i forgot to add java-17 in it on gonna mkae its code on the git hub but rn if i make it even better i will someday ok?
4. source code avalable oct 7? 6? 8? maybe?
