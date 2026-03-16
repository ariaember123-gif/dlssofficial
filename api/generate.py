from http.server import BaseHTTPRequestHandler
import requests
import os
import json

GTA_PROMPT = (
    "portrait of the same person as the input image, "
    "styled as a GTA San Andreas video game character, "
    "PS2 era 3D game style, "
    "low poly facial structure, "
    "smooth plastic-like skin shading, "
    "video game lighting, "
    "neutral wall background, "
    "center framed character portrait, "
    "shoulders visible, "
    "same hairstyle and facial features, "
    "game engine render aesthetic"
)

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            fal_key = os.environ.get("FAL_KEY", "")
            if not fal_key:
                self._json(500, {"error": "FAL_KEY environment variable not set"})
                return

            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            image_url = body.get("imageUrl", "")

            if not image_url:
                self._json(400, {"error": "No imageUrl provided"})
                return

            res = requests.post(
                "https://fal.run/fal-ai/flux/dev/image-to-image",
                headers={
                    "Authorization": f"Key {fal_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "prompt": GTA_PROMPT,
                    "image_url": image_url,
                    "strength": 0.78,
                    "num_images": 1,
                    "image_size": "square_hd",
                    "num_inference_steps": 28,
                    "guidance_scale": 3.5,
                    "enable_safety_checker": True,
                },
                timeout=120,
            )

            if not res.ok:
                self._json(500, {"error": res.text})
                return

            data = res.json()
            output_url = data.get("images", [{}])[0].get("url", "")
            if not output_url:
                self._json(500, {"error": "No output image returned from fal.ai"})
                return

            self._json(200, {"outputUrl": output_url})

        except Exception as e:
            self._json(500, {"error": str(e)})

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def _json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
