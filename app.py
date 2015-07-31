from flask import Flask, jsonify, request
import subprocess
import tempfile
import os
import sys

app = Flask(__name__)

@app.route("/",methods=["GET","POST"])
def index():
    if request.method == "POST":
        if request.content_type == "application/json":
            data = request.get_json(force=True, silent=True)
            if not data:
                args = data.get("args", [])
                data = data.get("script", False)
        else:
            data = request.form.get("script", False)
            args = request.form.get("args", [])
        if not data:
            return jsonify(success=False)

        f = tempfile.NamedTemporaryFile(delete=False, suffix=".ps1")
        try:
            f.write(data.encode("utf-8"))
            f.close()
            res = subprocess.Popen([r'C:\Windows\system32\WindowsPowerShell\v1.0\powershell.exe', '-ExecutionPolicy', 'UnRestricted', f.name] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = res.communicate()
            out = out.decode(sys.stdout.encoding)
            err = err.decode(sys.stdout.encoding)
            rc = res.returncode
            if rc != 0:
                return jsonify(success=False, out=out,err=err, returncode=rc)
            return jsonify(success=True, out=out, err=err, returncode=rc)
        except Exception as e:
            return jsonify(success=False, out="", err=e, returncode=1)
        finally:
            if not f.closed: f.close()
            os.remove(f.name)
    else:
        return jsonify(success=False)


# Test code form
@app.route("/upload", methods=["GET"])
def upload():
    return """
    <!doctype html>
    <title>Upload Script</title>
    <h1>Upload Script</h1>
    <form action="/" method="post">
    <textarea rows="20" cols="20" name="script"></textarea>
    <input type="submit" value="Upload">
    </form>"""

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4343)
