from flask import Flask, render_template_string, jsonify, request, redirect, url_for, send_from_directory
import subprocess, threading, os, shutil
import requests


app = Flask(__name__)

# ===== Working directory =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ===== Server and Bungee folders =====
SERVER_FOLDER = os.path.join(BASE_DIR, "server")
BUNGEE_FOLDER = os.path.join(BASE_DIR, "bungee")
os.makedirs(SERVER_FOLDER, exist_ok=True)
os.makedirs(BUNGEE_FOLDER, exist_ok=True)

# ===== Server and Bungee scripts =====
SERVER_SCRIPT = os.path.join(BASE_DIR, "server.sh")
BUNGEE_SCRIPT = os.path.join(BASE_DIR, "bungee.sh")

# ===== Processes and logs =====
server_process = None
bungee_process = None
server_log = []
bungee_log = []

# ===== Version check =====
CURRENT_VERSION = "v1.2.5"  # or read from a file if you prefer
DOCKER_HUB_REPO = "anikthedev/kukur-panel"

def get_latest_dockerhub_version():
    try:
        url = f"https://hub.docker.com/v2/repositories/{DOCKER_HUB_REPO}/tags?page_size=1&ordering=last_updated"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        latest_tag = data['results'][0]['name']
        return latest_tag
    except Exception as e:
        print("Error fetching latest version:", e)
        return None

LATEST_VERSION = get_latest_dockerhub_version()
IS_OLD = LATEST_VERSION and (LATEST_VERSION != CURRENT_VERSION)

# ===== Helper =====
def stream_output(process, log_list):
    for line in iter(process.stdout.readline, ''):
        log_list.append(line)
    process.stdout.close()

def safe_join(base, *paths):
    path = os.path.abspath(os.path.join(base, *paths))
    if not path.startswith(base):
        raise ValueError("Unsafe path")
    return path

# ===== Main Panel =====
@app.route("/")
def home():
    template = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kukur Panel</title>
<style>
body { font-family:'Segoe UI', sans-serif; background:#1e1e2f; color:#eee; padding:20px; }
h1,h2{color:#61dafb;} h1{text-align:center;}
button{background:#3a3f58; border:none; padding:10px 20px; margin:5px; color:#eee; cursor:pointer; border-radius:5px; font-size:1rem; transition:0.3s;}
button:hover{background:#61dafb;color:#1e1e2f;}
pre{background:#2d2d44; padding:15px; border-radius:8px; max-height:300px; overflow:auto;}
#FUCK_CODING { text-align:center; }
div { text-align:center; }
</style>
</head>
<body>
  <h1>Kukur Panel</h1>
<p id="FUCK_CODING">
  {% if latest_version %}
      Running {{ current_version }}{% if is_old %}, latest is {{ latest_version }} ⚠️{% endif %}
  {% else %}
      Running {{ current_version }}, unable to fetch latest version.
  {% endif %}
</p>

<div>
<button onclick="startServers()">Start Server(s)</button>
<button onclick="restartServers()">Restart Server(s)</button>
<button onclick="stopServers()">Stop Server(s)</button>
<button onclick="kill_it()">Kill Server(s)</button>
<button onclick="window.open('/files?type=server','_blank')">Open Server Files</button>
<button onclick="window.open('/files?type=bungee','_blank')">Open Bungee Files</button>
</div>
<h2>Main Server Logs</h2>
<pre id="server-log"></pre>
<h2>BungeeCord Proxy Logs</h2>
<pre id="bungee-log"></pre>
<h1> LINKS!!!</h1>
<div>
<a href="https://github.com/Anikthedev-Official/Kukur-panel" target="_blank">
  <img src="https://img.shields.io/badge/GitHub-Kukur%20Panel-blue?style=for-the-badge&logo=github" alt="GitHub Repo">
</a>
<a href="https://hub.docker.com/r/anikthedev/kukur-panel" target="_blank">
  <img src="https://img.shields.io/badge/Docker-Kukur%20Panel-blue?style=for-the-badge&logo=docker" alt="Docker Hub">
</a>
</div>
<script>
function fetchLogs() {
    fetch('/logs').then(r=>r.json()).then(data=>{
        document.getElementById('server-log').textContent=data.server_log;
        document.getElementById('bungee-log').textContent=data.bungee_log;
    });
}
setInterval(fetchLogs,1);
function startServers(){ fetch('/start').then(r=>r.text()).then(msg=>alert(msg)); }
function restartServers(){ fetch('/restart').then(r=>r.text()).then(msg=>alert(msg)); }
function stopServers(){ fetch('/stop').then(r=>r.text()).then(msg=>alert(msg)); }
function kill_it(){ fetch('/kill').then(r=>r.text()).then(msg=>alert(msg)); }
</script>
</body>
</html>
'''
    return render_template_string(template,
                                  current_version=CURRENT_VERSION,
                                  latest_version=LATEST_VERSION,
                                  is_old=IS_OLD)
@app.route("/logs")
def logs():
    return jsonify({'server_log': ''.join(server_log[-50:]), 'bungee_log': ''.join(bungee_log[-50:])})

# ===== Start/Stop =====
@app.route("/start")
def start():
    global server_process, bungee_process
    if server_process is None or server_process.poll() is not None:
        server_process = subprocess.Popen([SERVER_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, text=True)
        threading.Thread(target=stream_output, args=(server_process, server_log), daemon=True).start()
    if bungee_process is None or bungee_process.poll() is not None:
        bungee_process = subprocess.Popen([BUNGEE_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, text=True)
        threading.Thread(target=stream_output, args=(bungee_process, bungee_log), daemon=True).start()
    return "Server and BungeeCord started. (issues? hit me up on github ill respond i fix bugs and codes every day!)"

@app.route("/stop")
def stop_servers():
    global server_process, bungee_process
    # Stop server
    if server_process and server_process.poll() is None:
        server_process.terminate()  # or server_process.kill()
        server_process.wait()
        server_process = None

    # Stop bungee
    if bungee_process and bungee_process.poll() is None:
        bungee_process.terminate()  # or bungee_process.kill()
        bungee_process.wait()
        bungee_process = None

    return "Servers stopped successfully. (issues? hit me up on github ill respond i fix bugs and codes every day!)"
@app.route("/restart")
def restart():
    global server_process, bungee_process

    # Stop server
    if server_process and server_process.poll() is None:
        server_process.terminate()  # or server_process.kill()
        server_process.wait()
        server_process = None

    # Stop bungee
    if bungee_process and bungee_process.poll() is None:
        bungee_process.terminate()  # or bungee_process.kill()
        bungee_process.wait()
        bungee_process = None

    # Restart server
    if server_process is None or server_process.poll() is not None:
        server_process = subprocess.Popen([SERVER_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, text=True)
        threading.Thread(target=stream_output, args=(server_process, server_log), daemon=True).start()

    # Restart bungee
    if bungee_process is None or bungee_process.poll() is not None:
        bungee_process = subprocess.Popen([BUNGEE_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, text=True)
        threading.Thread(target=stream_output, args=(bungee_process, bungee_log), daemon=True).start()

    return "Server and BungeeCord restarted. (issues? hit me up on github, I fix bugs and codes every day!)"
# kill it
@app.route("/kill")
def kill_servers():
    global server_process, bungee_process
    # Stop server
    if server_process and server_process.poll() is None:
        server_process.kill()  # or server_process.kill() doing it kills it basically
        server_process.wait()
        server_process = None

    # Stop bungee
    if bungee_process and bungee_process.poll() is None:
        bungee_process.terminate()  # or bungee_process.kill()
        bungee_process.wait()
        bungee_process = None
    return "Server and BungeeCord KILLED!!. (issues? hit me up on github, I fix bugs and codes every day!)"
# ===== File Manager =====
@app.route("/files")
def files_page():
    folder_type = request.args.get("type","server")
    base_folder = SERVER_FOLDER if folder_type=="server" else BUNGEE_FOLDER
    relpath = request.args.get("path","")
    abs_path = safe_join(base_folder, relpath)
    parent_path = os.path.relpath(os.path.dirname(abs_path), base_folder) if relpath else None

    items=[]
    for name in os.listdir(abs_path):
        full=os.path.join(abs_path,name)
        items.append({"name":name,"is_dir":os.path.isdir(full),"relpath":os.path.relpath(full, base_folder)})

    template='''<!DOCTYPE html>
<html>
<head><title>File Manager</title>
<style>
body{font-family:'Segoe UI';background:#1e1e2f;color:#eee;padding:20px;}
h2{color:#61dafb;}
form{margin-bottom:10px;}
input,button{padding:5px;border-radius:4px;border:none;}
input[type=file],input[type=text]{background:#2d2d44;color:#eee;border:1px solid #3a3f58;}
button{background:#3a3f58;color:#eee;cursor:pointer;margin-left:5px;}
button:hover{background:#61dafb;color:#1e1e2f;}
a{color:#61dafb;text-decoration:none;}a:hover{text-decoration:underline;}
table{width:100%;border-collapse:collapse;margin-top:10px;}
th,td{border:1px solid #3a3f58;padding:8px;}
th{background:#2d2d44;}
tr:nth-child(even){background:#252539;} tr:nth-child(odd){background:#1e1e2f;}
</style>
</head>
<body>
<h2>File Manager - {{ current_path }}</h2>
<form action="/upload?path={{ current_path }}&type={{ folder_type }}" method="post" enctype="multipart/form-data">
<input type="file" name="file"><button type="submit">Upload</button>
</form>
<form action="/new_folder" method="post">
<input type="text" name="folder_name" placeholder="New Folder Name">
<input type="hidden" name="path" value="{{ current_path }}">
<input type="hidden" name="type" value="{{ folder_type }}">
<button type="submit">Create Folder</button>
</form>
{% if parent_path %}
<p><a href="/files?path={{ parent_path }}&type={{ folder_type }}">⬅ Back</a></p>
{% endif %}
<table><tr><th>Name</th><th>Actions</th></tr>
{% for item in items %}
<tr>
<td>{% if item.is_dir %}📁 <a href="/files?path={{ item.relpath }}&type={{ folder_type }}">{{ item.name }}</a>{% else %}📄 {{ item.name }}{% endif %}</td>
<td>{% if not item.is_dir %}
<a href="/download?path={{ item.relpath }}&type={{ folder_type }}">Download</a>
<a href="#" onclick="openEditor('{{ item.relpath }}','{{ folder_type }}')">Edit</a>
<a href="/delete?path={{ item.relpath }}&type={{ folder_type }}">Delete</a>
{% else %}
<a href="/delete?path={{ item.relpath }}&type={{ folder_type }}">Delete Folder</a>
{% endif %}</td>
</tr>
{% endfor %}
</table>
<script>
function openEditor(path,type){ window.open('/edit?path='+encodeURIComponent(path)+'&type='+encodeURIComponent(type),'editorWindow','width=800,height=600,resizable=yes,scrollbars=yes'); }
</script>
</body>
</html>
'''
    return render_template_string(template, items=items, current_path=relpath, parent_path=None if relpath=="" else os.path.dirname(relpath), folder_type=folder_type)

@app.route("/upload", methods=["POST"])
def upload_file():
    folder_type = request.args.get("type","server")
    base_folder = SERVER_FOLDER if folder_type=="server" else BUNGEE_FOLDER
    relpath = request.args.get("path","")
    abs_path = safe_join(base_folder, relpath)
    file = request.files["file"]
    if file:
        file.save(os.path.join(abs_path, file.filename))
    return redirect(url_for("files_page", path=relpath, type=folder_type))

@app.route("/new_folder", methods=["POST"])
def new_folder():
    folder_type=request.form.get("type","server")
    base_folder=SERVER_FOLDER if folder_type=="server" else BUNGEE_FOLDER
    relpath=request.form.get("path","")
    folder_name=request.form.get("folder_name","NewFolder")
    abs_path=safe_join(base_folder,relpath)
    os.makedirs(os.path.join(abs_path,folder_name),exist_ok=True)
    return redirect(url_for("files_page", path=relpath, type=folder_type))

@app.route("/download")
def download_file():
    folder_type=request.args.get("type","server")
    base_folder=SERVER_FOLDER if folder_type=="server" else BUNGEE_FOLDER
    relpath=request.args.get("path")
    abs_path=safe_join(base_folder,relpath)
    return send_from_directory(os.path.dirname(abs_path), os.path.basename(abs_path), as_attachment=True)

@app.route("/delete")
def delete_file():
    folder_type=request.args.get("type","server")
    base_folder=SERVER_FOLDER if folder_type=="server" else BUNGEE_FOLDER
    relpath=request.args.get("path")
    abs_path=safe_join(base_folder,relpath)
    if os.path.isdir(abs_path):
        shutil.rmtree(abs_path)
    else:
        os.remove(abs_path)
    return redirect(url_for("files_page", path=os.path.dirname(relpath), type=folder_type))

# ===== Ace Editor =====
@app.route("/edit", methods=["GET","POST"])
def edit_file():
    folder_type = request.args.get("type","server")
    base_folder = SERVER_FOLDER if folder_type=="server" else BUNGEE_FOLDER
    relpath = request.args.get("path")
    abs_path = safe_join(base_folder, relpath)
    if request.method=="POST":
        with open(abs_path,"w") as f:
            f.write(request.form["content"])
        return "<script>window.close();</script>Saved!"
    try:
        with open(abs_path,"r") as f:
            content=f.read()
    except:
        content="⚠️ Cannot display binary file."
    ext=relpath.split(".")[-1]
    modes={"yml":"yaml","yaml":"yaml","json":"json","sh":"sh","conf":"ini","properties":"ini","txt":"text"}
    mode=modes.get(ext,"text")
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Editing {relpath}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.12/ace.js"></script>
<style>
body{{margin:0;background:#1e1e2f;color:#eee;font-family:sans-serif;}}
#editor{{position:absolute;top:50px;bottom:0;left:0;right:0;}}
h3{{padding:10px;margin:0;background:#2d2d44;}}
button{{position:absolute;top:10px;right:10px;padding:5px 10px;border:none;border-radius:5px;cursor:pointer;background:#61dafb;color:#1e1e2f;}}
</style>
</head>
<body>
<h3>Editing: {relpath}</h3>
<form method="post" onsubmit="return saveContent();">
<div id="editor">{content}</div>
<textarea name="content" id="hiddenContent" style="display:none;"></textarea>
<button type="submit">Save</button>
</form>
<script>
var editor=ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/{mode}");
editor.session.setValue(`{content}`);
editor.setOptions({{fontSize:"14pt",showPrintMargin:false}});
function saveContent(){{document.getElementById("hiddenContent").value=editor.getValue();return true;}}
</script>
</body>
</html>
"""

if __name__=="__main__":
    app.run(host="0.0.0.0", port=8080)
