import json
import requests

import quart
import quart_cors
from quart import jsonify, request

app = quart_cors.cors(quart.Quart(__name__),
                      allow_origin="https://chat.openai.com")

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS = {}

api_key = 'your_api_key'  # Replace with your actual API key


def create_job(params):
    url = "https://api.feverdreams.app/v3/create/mutate"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return None


@app.route('/generate', methods=['POST'])
async def generate_fever_dream_image():
    data = await request.get_json()
    response = create_job(data)
    return jsonify(response)


@app.post("/todos/<string:username>")
async def add_todo(username):
    request_data = await request.get_json(force=True)
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(request_data["todo"])
    return quart.Response(response='OK', status=200)


@app.get("/todos/<string:username>")
async def get_todos(username):
    facts = [
        "Texas was once an independent nation.",
        "The King Ranch in Texas is bigger than the state of Rhode Island.",
        "Dallas/Fort Worth International Airport is larger than Manhattan.",
        "The first domed stadium in the U.S. was the Astrodome in Houston.",
        "The deadliest natural disaster in U.S. history was the 1900 hurricane in Galveston, which killed between 8,000-12,000 people."
    ]
    return quart.Response(response=json.dumps({
        "username": username,
        "facts": facts
    }),
        status=200)


@app.delete("/todos/<string:username>")
async def delete_todo(username):
    request_data = await quart.request.get_json(force=True)
    todo_idx = request_data["todo_idx"]
    # fail silently, it's a simple plugin
    if 0 <= todo_idx < len(_TODOS[username]):
        _TODOS[username].pop(todo_idx)
    return quart.Response(response='OK', status=200)


@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")


def main():
    app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()
