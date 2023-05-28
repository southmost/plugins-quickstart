import json
import quart_cors
from quart import jsonify, request
import asyncio
import quart
_TODOS ={}

app = quart_cors.cors(quart.Quart(__name__),
                      allow_origin="https://chat.openai.com")

@app.route('/explain', methods=['POST'])
async def explain_term():
    data = await request.get_json()
    term = data['term']

    prompts = [
        f"Explain {term} as if you were speaking to an AI researcher.",
        f"Explain {term} as if you were speaking to a computer science undergraduate.",
        f"Explain {term} as if you were speaking to someone with no background in AI or ML."
    ]

    explanations = {}
    for i, level in enumerate(['expert', 'intermediate', 'beginner']):
        # You need to replace 'Your AI model response' with the actual call to your AI model.
        explanations[level + '_explanation'] = 'Your AI model response'

    return quart.Response(response=json.dumps(explanations), mimetype='application/json')


@app.get("/plugin-info")
async def plugin_info():
    return quart.Response(response=json.dumps({
        "name": "ASCII Art Generator",
        "version": "1.0.0",
        "description": "A simple plugin to generate ASCII art from text."
    }), status=200)

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