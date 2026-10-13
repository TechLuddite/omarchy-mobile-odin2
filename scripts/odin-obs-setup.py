#!/usr/bin/env python3
"""Add the loopback Odin feed to OBS through its existing authenticated API.

Requires websocket-client. Reads the local OBS password without printing it.
Creates a dedicated scene/source; never starts streaming, recording or virtualcam.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import uuid

import websocket

SCENE = "Odin 2 Portal"
SOURCE = "Odin 2 Portal - Live Video"
URL = "http://127.0.0.1:17855/odin.ts"


class OBS:
    def __init__(self):
        path = Path.home() / ".config/obs-studio/plugin_config/obs-websocket/config.json"
        config = json.loads(path.read_text())
        if not config.get("server_enabled"):
            raise SystemExit("Enable OBS's authenticated WebSocket server first")
        self.ws = websocket.create_connection(f"ws://127.0.0.1:{config['server_port']}", timeout=10)
        hello = json.loads(self.ws.recv())["d"]
        data = {"rpcVersion": 1, "eventSubscriptions": 0}
        if "authentication" in hello:
            auth = hello["authentication"]
            secret = base64.b64encode(hashlib.sha256((config["server_password"] + auth["salt"]).encode()).digest()).decode()
            data["authentication"] = base64.b64encode(hashlib.sha256((secret + auth["challenge"]).encode()).digest()).decode()
        self.ws.send(json.dumps({"op": 1, "d": data}))
        if json.loads(self.ws.recv())["op"] != 2:
            raise SystemExit("OBS authentication failed")

    def call(self, request, data=None):
        request_id = uuid.uuid4().hex
        self.ws.send(json.dumps({"op": 6, "d": {"requestType": request,
            "requestId": request_id, "requestData": data or {}}}))
        while True:
            message = json.loads(self.ws.recv())
            if message.get("op") != 7 or message["d"].get("requestId") != request_id:
                continue
            result = message["d"]
            if not result["requestStatus"]["result"]:
                raise RuntimeError(f"OBS {request}: {result['requestStatus'].get('comment', 'failed')}")
            return result.get("responseData", {})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true", help="Show this scene if no live output is active")
    parser.add_argument("--screenshot", type=Path, help="Save a private verification frame from the source")
    parser.add_argument("--status", action="store_true", help="Read back the source without changing OBS")
    args = parser.parse_args()
    obs = OBS()
    try:
        if not args.status:
            scenes = obs.call("GetSceneList")["scenes"]
            if not any(s["sceneName"] == SCENE for s in scenes):
                obs.call("CreateScene", {"sceneName": SCENE})
            inputs = obs.call("GetInputList")["inputs"]
            existing = next((i for i in inputs if i["inputName"] == SOURCE), None)
            settings = {"is_local_file": False, "input": URL, "input_format": "mpegts",
                "buffering_mb": 0, "reconnect_delay_sec": 2, "close_when_inactive": True,
                "restart_on_activate": True, "clear_on_media_end": True}
            if existing is None:
                item = obs.call("CreateInput", {"sceneName": SCENE, "inputName": SOURCE,
                    "inputKind": "ffmpeg_source", "inputSettings": settings, "sceneItemEnabled": True})
            else:
                if existing["inputKind"] != "ffmpeg_source":
                    raise SystemExit("That source name belongs to another input kind; preserve it")
                old = obs.call("GetInputSettings", {"inputName": SOURCE})["inputSettings"]
                if old.get("input") != URL:
                    raise SystemExit("That source name is already used for another feed; preserve it")
                items = obs.call("GetSceneItemList", {"sceneName": SCENE})["sceneItems"]
                item = next((i for i in items if i["sourceName"] == SOURCE), None)
                if item is None:
                    item = obs.call("CreateSceneItem", {"sceneName": SCENE, "sourceName": SOURCE})
            video = obs.call("GetVideoSettings")
            obs.call("SetSceneItemTransform", {"sceneName": SCENE, "sceneItemId": item["sceneItemId"],
                "sceneItemTransform": {"positionX": 0.0, "positionY": 0.0, "alignment": 5,
                    "boundsType": "OBS_BOUNDS_SCALE_INNER", "boundsAlignment": 0,
                    "boundsWidth": video["baseWidth"], "boundsHeight": video["baseHeight"]}})
            if args.preview:
                active = False
                for request in ("GetStreamStatus", "GetRecordStatus", "GetVirtualCamStatus"):
                    try:
                        active |= bool(obs.call(request).get("outputActive"))
                    except RuntimeError as error:
                        if request == "GetVirtualCamStatus" and "VirtualCam is not available" in str(error):
                            continue
                        raise
                if not active:
                    if obs.call("GetStudioModeEnabled")["studioModeEnabled"]:
                        obs.call("SetCurrentPreviewScene", {"sceneName": SCENE})
                    else:
                        obs.call("SetCurrentProgramScene", {"sceneName": SCENE})
        print(f"OBS scene: {SCENE}; media source: {SOURCE}; input: {URL}")
        print(json.dumps(obs.call("GetMediaInputStatus", {"inputName": SOURCE})))
        if args.screenshot:
            obs.call("SaveSourceScreenshot", {"sourceName": SOURCE, "imageFormat": "png",
                "imageFilePath": str(args.screenshot.resolve())})
    finally:
        obs.ws.close()


if __name__ == "__main__":
    main()
