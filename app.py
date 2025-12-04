# app.py
# Compatibility shim for pkgutil.get_loader on Python where it's missing
import pkgutil
import importlib.util

if not hasattr(pkgutil, "get_loader"):
    def _get_loader(name):
        # Some names (like '__main__') may not have a spec; handle gracefully
        if name in ("__main__",):
            return None
        try:
            spec = importlib.util.find_spec(name)
        except (ValueError, ImportError):
            return None
        if not spec:
            return None
        return getattr(spec, "loader", None)
    pkgutil.get_loader = _get_loader

from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello from DevSecOps demo app!"

# Intentional insecure demo endpoint (to be detected by SAST rules)
@app.route('/eval', methods=['POST'])
def dangerous_eval():
    # DO NOT USE exec() in real apps — this exists only for demo detection
    code = request.json.get('code', '')
    try:
        result = {}
        exec(code, {}, result)
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8080'))
    app.run(host='0.0.0.0', port=port)
