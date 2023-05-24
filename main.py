import json
import requests

import quart
import quart_cors
from quart import jsonify, request

app = quart_cors.cors(quart.Quart(__name__),
                      allow_origin="https://chat.openai.com")

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS = {}
_JOB_IDS = {}

api_key = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlFqaEdSRUl6T1VSRVJEZzJSa0pCUXpjelF6SXhRMFUyUWpnM09VSkJSRU16TVVGRk5FWkZNdyJ9.eyJpc3MiOiJodHRwczovL2Rldi15cXpzbjMyNi5hdXRoMC5jb20vIiwic3ViIjoib2F1dGgyfGRpc2NvcmR8NDU1NDMwMTcyOTI2Mjc5Njk4IiwiYXVkIjpbImh0dHBzOi8vYXBpLmZldmVyZHJlYW1zLmFwcC8iLCJodHRwczovL2Rldi15cXpzbjMyNi5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNjg0ODk4NTcyLCJleHAiOjE2ODQ5ODQ5NzIsImF6cCI6ImRsdDY4M1JLWG9UNnRET0hDYTh3V1FRYW9Ib2JjalFtIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInBlcm1pc3Npb25zIjpbInZldHRlZCJdfQ.RTjKa_YiU4fmWJiHXpbT6i3ni4gtxUxcUWaqGMgp2ksiA4JKfqgN9jDOWEznTGhz8IsZTPcuLaIDH77FzA5UgYUfY3MW_-awwJwVaVwpz48WG3vBRS7aC70nNxD21kvTKQlBdtElvHjSce24naXZb0qv_bs62e9hsA8yX3irAFY3BZfEbKDjcVQ41PDLjx5gmPsZMJ5DAo'  # Replace with your actual API key


def create_job(image_description):
    url = "https://api.feverdreams.app/v3/create/mutate"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    params = {
        "job": {
            "algo": "stable",
            "uuid": "genesis",
            "status": "new",
            "nsfw": False,
            "private": False,
            "hide": False,
            "review": True,
            "priority": "medium",
            "location": {
                "png": None,
                "jpg": None,
                "thumbs": {
                    "64": None,
                    "128": None,
                    "256": None,
                    "512": None,
                    "1024": None
                }
            },
            "params": {
                "sd_model_checkpoint": "cc6cb27103417325ff94f52b7a5d2dde45a7515b25c255d8e396c90014281516",
                "mode": "txt2img",
                "other_model": "",
                "ti_enabled": False,
                "embeddings": [],
                "loras_enabled": False,
                "loras": [],
                "img2img_ref_img_type": "piece",
                "img2img_ref_img_url": "",
                "img2img_resize_mode": 0,
                "img2img_denoising_strength": 0.75,
                "img2img_mask_hash": "",
                "img2img_inpaint": False,
                "img2img_mask_blur": 4,
                "img2img_inpainting_fill": 1,
                "img2img_inpaint_full_res": True,
                "img2img_inpaint_full_res_padding": 32,
                "img2img_inpainting_mask_invert": 1,
                "img2img_initial_noise_multiplier": 1,
                "controlnet_enabled": False,
                "controlnet_ref_img_type": "piece",
                "controlnet_module": "none",
                "controlnet_model": "none",
                "controlnet_threshold_a": 0,
                "controlnet_threshold_b": 0,
                "controlnet_preprocessor_resolution": 512,
                "controlnet_control_mode": "0",
                "controlnet_weight": 1,
                "controlnet_guidance_start": 0,
                "controlnet_guidance_end": 1,
                "width_height": [512, 512],
                "denoising_strength": 0.75,
                "hr_scale": 1.5,
                "seed": -1,
                "scale": 7,
                "offset_noise": 0,
                "clip_skip": 1,
                "steps": 25,
                "prompt": image_description,
                "negative_prompt": "",
                "restore_faces": False,
                "fr_model": "CodeFormer",
                "cf_weight": 0.5,
                "enable_hr": False,
                "sampler": "Euler a",
                "eta": 0,
                "enable_ad": False,
                "ad_model": "face_yolov8n.pt",
                "ad_prompt": "highly detailed face",
                "ad_negative_prompt": "ugly",
                "ad_conf": 0.3,
                "ad_dilate_erode": 32,
                "ad_x_offset": 0,
                "ad_y_offset": 0,
                "ad_mask_blur": 4,
                "ad_denoising_strength": 0.4,
                "ad_inpaint_full_res": True,
                "ad_inpaint_full_res_padding": 0,
                "ad_use_inpaint_width_height": False,
                "ad_inpaint_width": 512,
                "ad_inpaint_height": 512,
                "ad_use_cfg_scale": False,
                "ad_cfg_scale": 7,
                "ad_controlnet_model": "None",
                "ad_controlnet_weight": 1,
                "parent_uuid": "genesis"
            },
            "batch_size": 1
        }
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
    image_description = data.get('description')
    
    response = create_job(image_description)
    
    # Store the job ID for later use.
    if response is not None and 'job_id' in response:
        job_id = response['job_id']
        if job_id not in _JOB_IDS:
            _JOB_IDS[job_id] = {'description': image_description, 'status': 'processing'}
            # Immediately request the job status and update it in the dictionary.
            status_response = check_job_status(job_id)
            if status_response is not None and 'status' in status_response:
                _JOB_IDS[job_id]['status'] = status_response['status']
        return jsonify(response)
    else:
        return jsonify({'error': 'Job creation failed.'}), 500

@app.route('/jobs/<string:job_id>', methods=['GET'])
def check_job_status(job_id):
    url = f"https://api.feverdreams.app/v3/jobs/{job_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return None

@app.route('/job_status/<job_id>', methods=['GET'])
async def get_job_status(job_id):
    if job_id in _JOB_IDS:
        # When the job status is requested, update it in the dictionary.
        status_response = check_job_status(job_id)
        if status_response is not None and 'status' in status_response:
            _JOB_IDS[job_id]['status'] = status_response['status']
        return jsonify(_JOB_IDS[job_id])
    else:
        return jsonify({'error': 'Job not found.'}), 404

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