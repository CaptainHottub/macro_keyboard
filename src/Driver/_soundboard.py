#!/usr/bin/env python3

import json
import subprocess
import sys
import shutil
import re
import sounddevice as sd
import soundfile as sf
import threading
from scipy import signal
import numpy as np
from logger_setup import setup_logging, get_logger

"""
Basically a soundboard.          
This doesnt always work, its pretty finicky.
Its build for linux, may not work on windows.
    

To list devices: print(sd.query_devices())  

# Example usage:        
devices = ["default", "HELLDIVERS"]     
play_audio_on_devices(test.mp3, devices, volume=0.5)       
play_audio_on_devices(AHHHHH.mp3, volume=0.5)        

Args:
    filename (str): Audio file you want to play
    devices (list, optional): The audio device you want the audio outputed to. Defaults to "default".
    volume (float, optional): Float val from 1.0 to 0. Defaults to 0.5.
"""
    
# --- Startup procedure ---
# settings._list()
setup_logging()
logger = get_logger('_Soundboard')


class AudioWire:
    def __init__(
        self,
        device=None,            # e.g. (input_id_or_name, output_id_or_name) or None for defaults
        samplerate=None,        # None = device default
        blocksize=None,         # None = host default
        dtype=None,             # e.g. "float32"
        latency=None,           # seconds or (input, output)
        channels=2,
        initial_enabled=True,
        print_status=True,
    ):
        self._device = device
        self._samplerate = samplerate
        self._blocksize = blocksize
        self._dtype = dtype
        self._latency = latency
        self._channels = channels
        self._print_status = print_status

        self._enabled = initial_enabled
        self._enabled_lock = threading.Lock()
        self._stream = None

    @staticmethod
    def list_devices():
        """Return sounddevice.query_devices() for convenience."""
        return sd.query_devices()

    @property
    def enabled(self) -> bool:
        with self._enabled_lock:
            return self._enabled

    def enable(self, flag: bool):
        with self._enabled_lock:
            self._enabled = bool(flag)

    def toggle(self) -> bool:
        with self._enabled_lock:
            self._enabled = not self._enabled
            return self._enabled

    # --- internal callback ---
    def _callback(self, indata, outdata, frames, time, status):
        if status and self._print_status:
            print(status)
        if self.enabled:
            # pass input straight to output
            outdata[:] = indata
        else:
            # output silence while still consuming input
            outdata.fill(0)

    # --- lifecycle ---
    def start(self):
        if self._stream is not None:
            return  # already running

        self._stream = sd.Stream(
            device=self._device,
            samplerate=self._samplerate,
            blocksize=self._blocksize,
            dtype=self._dtype,
            latency=self._latency,
            channels=self._channels,
            callback=self._callback,
        )
        self._stream.start()
        return self

    def stop(self):
        if self._stream is not None:
            try:
                self._stream.stop()
            finally:
                self._stream.close()
                self._stream = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()



# --- helpers ---
def need(cmd):
    if not shutil.which(cmd):
        sys.exit(f"Missing '{cmd}'. Install pipewire-tools.")

def as_int(x):
    try: 
        return int(x)
    except: 
        return x

def get_default_sink_name():
    need("pw-metadata")
    txt = subprocess.check_output(["pw-metadata", "-n", "default", "0"], text=True)
    m = re.search(r"key:'default.audio.sink'.*?value:'(.*?)'", txt, re.S)
    if not m:
        sys.exit("Could not read default.audio.sink from metadata")
    try:
        val = json.loads(m.group(1))
        return val["name"]
    except Exception:
        sys.exit("Malformed metadata for default.audio.sink")

def get_default_source_name():
    need("pw-metadata")
    txt = subprocess.check_output(["pw-metadata", "-n", "default", "0"], text=True)
    m = re.search(r"key:'default.audio.source'.*?value:'(.*?)'", txt, re.S)
    if not m:
        sys.exit("Could not read default.audio.source from metadata")
    try:
        val = json.loads(m.group(1))
        return val["name"]
    except Exception:
        sys.exit("Malformed metadata for default.audio.source")

def pw_dump():
    need("pw-dump")
    return json.loads(subprocess.check_output(["pw-dump"], text=True))

def label(node):
    return node.get("nick") or node.get("name") or node.get("desc")


# --- core ---
def consumers_of_default_source():
    default_src_name = get_default_source_name()
    dump = pw_dump()

    nodes, links = {}, []
    for obj in dump:
        t = obj.get("type","")
        info = obj.get("info",{}) or {}
        props = info.get("props",{}) or {}
        if t.endswith("Node"):
            nid = as_int(obj.get("id"))
            nodes[nid] = {
                "name": props.get("node.name"),
                "nick": props.get("node.nick"),
                "desc": props.get("device.description"),
                "media": props.get("media.class"),
                "props": props,
            }
        elif t.endswith("Link"):
            links.append({
                "out_node": as_int(info.get("output-node-id") or info.get("output.node")),
                "in_node":  as_int(info.get("input-node-id")  or info.get("input.node")),
                "state":    info.get("state"),
            })

    # find the default source node id
    src_id = next((nid for nid,n in nodes.items() if n.get("name") == default_src_name), None)
    if src_id is None:
        sys.exit(f"Default source '{default_src_name}' not found in graph")

    # collect active consumers (deduped by node id)
    consumers = {}
    for L in links:
        if L["out_node"] == src_id and L.get("state") in (None, "active", "linked"):
            n = nodes.get(L["in_node"])
            if not n: 
                continue
            consumers[L["in_node"]] = {
                "node_id": L["in_node"],
                "label": label(n) or f"node-{L['in_node']}",
                "media_class": n.get("media"),
                "application": (n.get("props") or {}).get("application.name"),
                "node_name": n.get("name"),
            }    
            
    # return sorted list by human label
    return default_src_name, sorted(consumers.values(), key=lambda d: d["label"].casefold())

def producers_of_default_sink():
    default_sink_name = get_default_sink_name()
    dump = pw_dump()

    nodes, links = {}, []
    for obj in dump:
        t = obj.get("type","")
        info = obj.get("info",{}) or {}
        props = info.get("props",{}) or {}
        if t.endswith("Node"):
            nid = as_int(obj.get("id"))
            nodes[nid] = {
                "name": props.get("node.name"),
                "nick": props.get("node.nick"),
                "desc": props.get("device.description"),
                "media": props.get("media.class"),
                "props": props,
            }
        elif t.endswith("Link"):
            links.append({
                "out_node": as_int(info.get("output-node-id") or info.get("output.node")),
                "in_node":  as_int(info.get("input-node-id")  or info.get("input.node")),
                "state":    info.get("state"),
            })

    # find the default sink node id
    sink_id = next((nid for nid, n in nodes.items() if n.get("name") == default_sink_name), None)
    if sink_id is None:
        sys.exit(f"Default sink '{default_sink_name}' not found in graph")

    # collect active producers feeding the sink (deduped by node id)
    producers = {}
    for L in links:
        if L["in_node"] == sink_id and L.get("state") in (None, "active", "linked"):
            n = nodes.get(L["out_node"])
            if not n:
                continue
            producers[L["out_node"]] = {
                "node_id": L["out_node"],
                "label": label(n) or f"node-{L['out_node']}",
                "media_class": n.get("media"),
                "application": (n.get("props") or {}).get("application.name"),
                "node_name": n.get("name"),
            }

    # return sorted list by human label
    return default_sink_name, sorted(producers.values(), key=lambda d: d["label"].casefold())

def play_audio_on_device(audio_data, samplerate, volume, device):
    """
    Function to play audio data on a specified device.
    This function will be executed by a separate thread.
    """
    
    device_index = device['index']
    with sd.OutputStream(samplerate=samplerate, device=device_index, channels=audio_data.shape[1]) as stream:
        audio_data *= volume
        if not audio_data.flags['C_CONTIGUOUS']:
            audio_data = np.ascontiguousarray(audio_data, dtype='float32')
        stream.write(audio_data)
    
def play_on_multiple_devices(filename, volume):
    """This works, but runs into memory capacity errors when it tries to send audio to more then 2 devices.
    """

    default_consumer_name, consumers = consumers_of_default_source()
    default = sd.default.device[1]
    devices = sd.query_devices()
        
    new_devices = [devices[default]]
    for consumer in consumers:    
        for device in devices:
            print(consumer['application'])
            if consumer['application'] in device['name']:
                new_devices.append(device)
    
    if len(new_devices) == 1:
        logger.debug("No additional devices found to play audio on.")
        return
                
    data, samplerate = sf.read(filename, dtype='float32')

    threads = []
    for device in new_devices:
        logger.debug(f"Sending audio to {device['name']}")
        # resamples the audio if needed
        device_samplerate = int(device['default_samplerate'])
        audio_data = data
        samplerate = samplerate

        if samplerate != device['default_samplerate']:
            # Resample the audio data to the device's rate
            num = int(len(data) * device_samplerate / samplerate)
            audio_data = signal.resample(data, num)
            samplerate = device_samplerate

        # Create a new thread
        thread = threading.Thread(
            target=play_audio_on_device,
            # args=(filename, device),
            args=(audio_data, samplerate, volume, device),
            name=f"PlaybackThread-{device['name']}"
        )
        threads.append(thread)
        thread.start()  

   
def terminate():
    if sd._initialized:
        sd._terminate()
        return True
    else:
        return False

def initialize():
    if not sd._initialized:
        sd._initialize()

def reset():
    terminate()
    initialize()