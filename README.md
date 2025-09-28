# Kukur-panel
A mc server hosting panel made by me its soo so so simple
to run it (and pull it. It uses python flask and)
```
from flask import Flask, render_template_string, jsonify, request, redirect, url_for, send_from_directory
import subprocess, threading, os, shutil

app = Flask(__name__)

# ===== Server processes and logs ===== #
server_process = None
bungee_process = None
server_log = []
bungee_log = []

# ===== Server and Bungee folders ===== #
SERVER_FOLDER = "/home/yoiwannajinksbegam/server"
BUNGEE_FOLDER = "/home/yoiwannajinksbegam/bungee"
os.makedirs(SERVER_FOLDER, exist_ok=True)
os.makedirs(BUNGEE_FOLDER, exist_ok=True)

# ===== Helper for logs ===== #
def stream_output(process, log_list):
    for line in iter(process.stdout.readline, ''):
        log_list.append(line)
    process.stdout.close()

# ===== Safe join helper ===== #
def safe_join(base, *paths):
    path = os.path.abspath(os.path.join(base, *paths))
    if not path.startswith(base):
        raise ValueError("Unsafe path")
    return path

# ===== Main Panel ===== #
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
    body { font-family: 'Segoe UI', sans-serif; background:#1e1e2f; color:#eee; padding:20px; }
    h1,h2 { color:#61dafb; }
    h1 { text-align:center; }
    button { background:#3a3f58; border:none; padding:10px 20px; margin:5px; color:#eee; cursor:pointer; border-radius:5px; font-size:1rem; transition:0.3s; }
    button:hover { background:#61dafb; color:#1e1e2f; }
    pre { background:#2d2d44; padding:15px; border-radius:8px; max-height:300px; overflow-y:auto; }
</style>
</head>
<body>
<h1>Kukur Panel</h1>
<div>
    <button onclick="startServers()">Start Servers</button>
    <button onclick="stopServers()">Stop Servers</button>
    <button onclick="window.open('/files?type=server','_blank')">Open Server Files</button>
    <button onclick="window.open('/files?type=bungee','_blank')">Open Bungee Files</button>
</div>

<h2>Main Server Console</h2>
<pre id="server-log"></pre>

<h2>BungeeCord Console</h2>
<pre id="bungee-log"></pre>

<script>
function fetchLogs() {
    fetch('/logs')
    .then(r => r.json())
    .then(data => {
        document.getElementById('server-log').textContent = data.server_log;
        document.getElementById('bungee-log').textContent = data.bungee_log;
    });
}
setInterval(fetchLogs, 2000);

function startServers() {
    fetch('/start').then(r => r.text()).then(msg => alert(msg));
}
function stopServers() {
    fetch('/stop').then(r => r.text()).then(msg => alert(msg));
}
</script>
</body>
</html>
    '''
    return render_template_string(template)

@app.route("/logs")
def get_logs():
    return jsonify({'server_log': ''.join(server_log[-50:]), 'bungee_log': ''.join(bungee_log[-50:])})

@app.route("/start")
def start_servers():
    global server_process, bungee_process
    if server_process is None or server_process.poll() is not None:
        server_process = subprocess.Popen(
            ["/home/yoiwannajinksbegam/server.sh"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, text=True
        )
        threading.Thread(target=stream_output, args=(server_process, server_log), daemon=True).start()
    if bungee_process is None or bungee_process.poll() is not None:
        bungee_process = subprocess.Popen(
            ["/home/yoiwannajinksbegam/bungee.sh"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, text=True
        )
        threading.Thread(target=stream_output, args=(bungee_process, bungee_log), daemon=True).start()
    return "Server and BungeeCord started."

@app.route("/stop")
def stop_servers():
    global server_process, bungee_process
    subprocess.Popen(["pkill", "-9", "java"])
    server_process = None
    bungee_process = None
    return "All Java processes killed."

# ===== File Manager ===== #
@app.route("/files")
def files_page():
    folder_type = request.args.get("type","server")
    base_folder = SERVER_FOLDER if folder_type=="server" else BUNGEE_FOLDER
    relpath = request.args.get("path", "")
    abs_path = safe_join(base_folder, relpath)
    parent_path = os.path.relpath(os.path.dirname(abs_path), base_folder) if relpath else None

    items = []
    for name in os.listdir(abs_path):
        full = os.path.join(abs_path, name)
        items.append({"name": name, "is_dir": os.path.isdir(full), "relpath": os.path.relpath(full, base_folder)})

    template = '''<!DOCTYPE html>
<html>
<head>
    <title>File Manager</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background:#1e1e2f; color:#eee; padding:20px; }
        h2 { color:#61dafb; }
        form { margin-bottom: 10px; }
        input, button { padding:5px; border-radius:4px; border:none; }
        input[type="file"], input[type="text"] { background:#2d2d44; color:#eee; border:1px solid #3a3f58; }
        button { background:#3a3f58; color:#eee; cursor:pointer; margin-left:5px; }
        button:hover { background:#61dafb; color:#1e1e2f; }
        a { color:#61dafb; text-decoration:none; }
        a:hover { text-decoration:underline; }
        table { width:100%; border-collapse:collapse; margin-top:10px; }
        th, td { border:1px solid #3a3f58; padding:8px; }
        th { background:#2d2d44; }
        tr:nth-child(even) { background:#252539; }
        tr:nth-child(odd) { background:#1e1e2f; }
    </style>
</head>
<body>
<h2>File Manager - {{ current_path }}</h2>

<!-- Upload -->
<form action="/upload?path={{ current_path }}&type={{ folder_type }}" method="post" enctype="multipart/form-data">
    <input type="file" name="file">
    <button type="submit">Upload</button>
</form>

<!-- New Folder -->
<form action="/new_folder" method="post" style="margin-bottom:15px;">
    <input type="text" name="folder_name" placeholder="New Folder Name">
    <input type="hidden" name="path" value="{{ current_path }}">
    <input type="hidden" name="type" value="{{ folder_type }}">
    <button type="submit">Create Folder</button>
</form>

{% if parent_path %}
<p><a href="/files?path={{ parent_path }}&type={{ folder_type }}">⬅ Back</a></p>
{% endif %}

<table>
<tr><th>Name</th><th>Actions</th></tr>
{% for item in items %}
<tr>
    <td>
        {% if item.is_dir %}
            📁 <a href="/files?path={{ item.relpath }}&type={{ folder_type }}">{{ item.name }}</a>
        {% else %}
            📄 {{ item.name }}
        {% endif %}
    </td>
    <td>
        {% if not item.is_dir %}
            <a href="/download?path={{ item.relpath }}&type={{ folder_type }}">Download</a>
            <a href="#" onclick="openEditor('{{ item.relpath }}','{{ folder_type }}')">Edit</a>
            <a href="/delete?path={{ item.relpath }}&type={{ folder_type }}">Delete</a>
        {% else %}
            <a href="/delete?path={{ item.relpath }}&type={{ folder_type }}">Delete Folder</a>
        {% endif %}
    </td>
</tr>
{% endfor %}
</table>

<script>
function openEditor(path, type) {
    window.open(
        '/edit?path=' + encodeURIComponent(path) + '&type=' + encodeURIComponent(type),
        'editorWindow',
        'width=800,height=600,top=100,left=100,resizable=yes,scrollbars=yes'
    );
}
</script>
</body>
</html>

    '''
    return render_template_string(template, items=items, current_path=relpath,
                                  parent_path=None if relpath=="" else os.path.dirname(relpath),
                                  folder_type=folder_type)

@app.route("/upload", methods=["POST"])
def upload_file():
    folder_type = request.args.get("type","server")
    base_folder = SERVER_FOLDER if folder_type=="server" else BUNGEE_FOLDER
    relpath = request.args.get("path", "")
    abs_path = safe_join(base_folder, relpath)
    file = request.files["file"]
    if file:
        file.save(os.path.join(abs_path, file.filename))
    return redirect(url_for("files_page", path=relpath, type=folder_type))

@app.route("/new_folder", methods=["POST"])
def new_folder():
    folder_type = request.form.get("type","server")
    base_folder = SERVER_FOLDER if folder_type=="server" else BUNGEE_FOLDER
    relpath = request.form.get("path","")
    folder_name = request.form.get("folder_name","NewFolder")
    abs_path = safe_join(base_folder, relpath)
    new_path = os.path.join(abs_path, folder_name)
    os.makedirs(new_path, exist_ok=True)
    return redirect(url_for("files_page", path=relpath, type=folder_type))

@app.route("/download")
def download_file():
    folder_type = request.args.get("type","server")
    base_folder = SERVER_FOLDER if folder_type=="server" else BUNGEE_FOLDER
    relpath = request.args.get("path")
    abs_path = safe_join(base_folder, relpath)
    return send_from_directory(os.path.dirname(abs_path), os.path.basename(abs_path), as_attachment=True)

@app.route("/delete")
def delete_file():
    folder_type = request.args.get("type","server")
    base_folder = SERVER_FOLDER if folder_type=="server" else BUNGEE_FOLDER
    relpath = request.args.get("path")
    abs_path = safe_join(base_folder, relpath)
    if os.path.isdir(abs_path):
        shutil.rmtree(abs_path)  # Recursive delete
    else:
        os.remove(abs_path)
    return redirect(url_for("files_page", path=os.path.dirname(relpath), type=folder_type))

# ===== Editor (Ace, Server + Bungee) ===== #
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
            content = f.read()
    except:
        content = "⚠️ Cannot display binary file."

    ext = relpath.split(".")[-1]
    modes = {"yml":"yaml","yaml":"yaml","json":"json","sh":"sh","conf":"ini","properties":"ini","txt":"text"}
    mode = modes.get(ext,"text")

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Editing {relpath}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.12/ace.js"></script>
<style>
body {{ margin:0; background:#1e1e2f; color:#eee; font-family:sans-serif; }}
#editor {{ position:absolute; top:50px; bottom:0; left:0; right:0; }}
h3 {{ padding:10px; margin:0; background:#2d2d44; }}
button {{ position:absolute; top:10px; right:10px; padding:5px 10px; border:none; border-radius:5px; cursor:pointer; background:#61dafb; color:#1e1e2f; }}
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
var editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/{mode}");
editor.session.setValue(`{content}`);
editor.setOptions({{ fontSize:"14pt", showPrintMargin:false }});
function saveContent() {{
    document.getElementById("hiddenContent").value = editor.getValue();
    return true;
}}
</script>
</body>
</html>
"""

if __name__=="__main__":
    app.run(host="0.0.0.0", port=8080)
```
replace the ```/home/yoiwannajinks/<directory>``` with your files okay?
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
