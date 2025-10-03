# Kukur-panel
![Alt text](Untitled.png)
 # Current Version AND PULLS ( PUlls removed since it dont work ig)!! 
 <p align="center">
  <img src="https://img.shields.io/docker/v/anikthedev/kukur-panel?sort=date&label=Version&color=blue" alt="Docker Image Version">
</p>
<p align="center">
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
  anikthedev/kukur-panel:v1.2.2
```
replace the ```/home/yoiwannajinks/<directory>``` with your files okay?
anyway  if your not using bungee then dont put (for servers that are made for a small groups of friends)
plus the port 8080 is for the panel and port 8081 is for eaglercraft (yes i sometimes play java plus eagler) and 25565 is server and 25577 is bungee
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
# IMPORTANT STUFF(S)
first keep up with the latest build since i make mistakes and i test every build after psuhing if i make an eror i update them immedietly  so watch out thats why i added the latest version checker even if its bloated with python ( not slim image afte 1.1.2)
# Random Changelog 
1. at first i used docker it was unstable and shitty and didnt work
2. then moved to python so basically gave out the code 
3. then right now reused docker and its v1.0.1 for bcuz its a bugfix or some shit since i forgot to add java-17 in it on gonna mkae its code on the git hub but rn if i make it even better i will someday ok?
4. source code avalable oct 7? 6? 8? maybe? currently open-sorcing it
5. yeah this is not going to be open source or shit i hate doing it it takes free time so f it 
6. yeah f it i open sourced it today
7. the buttons is slow............ DONT USE KILLLLLLLLLL!!!!!!!!!!!!!!!!
8. made a autopush function yesterday for you guys agknowledge it please.!! 🥲🥲🥲
9. removed kill and restart they made the whole image bloated and buggy sorry!
10. half moving to a folder half not its ther jsut in case
11. you know what i wont move 
12. umm this [code beutifier](https://codebeautify.org/htmlviewer) just ruined code so the file editor code has been beutified and the home page so ther not speghetti code anymore :) ok?
