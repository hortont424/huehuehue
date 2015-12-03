#!/usr/bin/env python

from phue import Bridge
import pprint
import json
import os

bridge = Bridge('10.0.1.29')
bridge.connect()

sensors = {
    "00:00:00:00:00:40:92:15-f2": "Bedroom Door",
    "00:00:00:00:00:42:06:3b-f2": "Bedroom Nightstand",
    "00:00:00:00:00:43:c1:9b-f2": "Office Door",
    "00:00:00:00:00:43:1c:9f-f2": "Front Door",
}

lights = {
    "00:17:88:01:00:b1:8a:1d-0b": "Bedroom - Alicia",
    "00:17:88:01:00:b1:91:e2-0b": "Bedroom - Tim",
    
    "00:17:88:01:00:ba:20:96-0b": "Living Room 1",
    "00:17:88:01:00:bf:d8:5c-0b": "Living Room 2",
    "00:17:88:01:00:b1:bf:53-0b": "Kitchen Left",
    "00:17:88:01:00:b6:43:72-0b": "Kitchen Right",

    "00:17:88:01:00:ba:63:38-0b": "Office 1",
    "00:17:88:01:00:b6:43:01-0b": "Office 2",
}

plain_white_light_state = {
    "bri": 255,
    "effect": "none",
    "on": True,
    "xy": [0.4448, 0.4066]
}

dim_white_light_state = {
    "bri": 90,
    "effect": "none",
    "on": True,
    "xy": [0.4448, 0.4066]
}

off_light_state = {
    "on": False
}

all_lights_off = {
    "Bedroom - Alicia": off_light_state,
    "Bedroom - Tim": off_light_state,
    "Living Room 1": off_light_state,
    "Living Room 2": off_light_state,
    "Kitchen Left": off_light_state,
    "Kitchen Right": off_light_state,
    "Office 1": off_light_state,
    "Office 2": off_light_state
}

sensor_mappings = {
    "Front Door": {
        1: {
            "Living Room 1": off_light_state,
            "Living Room 2": off_light_state,
            "Kitchen Left": off_light_state,
            "Kitchen Right": off_light_state
        },
        2: {
            "Living Room 1": plain_white_light_state,
            "Living Room 2": plain_white_light_state,
            "Kitchen Left": plain_white_light_state,
            "Kitchen Right": plain_white_light_state
        },
        3: {
            "Kitchen Left": plain_white_light_state,
            "Kitchen Right": plain_white_light_state
        },
        4: all_lights_off
    },
    "Office Door": {
        1: {
            "Office 1": off_light_state,
            "Office 2": off_light_state
        },
        2: {
            "Office 1": plain_white_light_state,
            "Office 2": plain_white_light_state
        },
        3: {
            "Office 1": dim_white_light_state,
            "Office 2": dim_white_light_state
        }
    },
    "Bedroom Door": {
        1: {
            "Living Room 1": off_light_state,
            "Living Room 2": off_light_state,
            "Kitchen Left": off_light_state,
            "Kitchen Right": off_light_state
        },
        2: {
            "Living Room 1": plain_white_light_state,
            "Living Room 2": plain_white_light_state,
            "Kitchen Left": plain_white_light_state,
            "Kitchen Right": plain_white_light_state
        },
        3: {
            "Bedroom - Alicia": plain_white_light_state,
            "Bedroom - Tim": plain_white_light_state
        },
        4: {
            "Bedroom - Alicia": off_light_state,
            "Bedroom - Tim": off_light_state
        }
    },
    "Bedroom Nightstand": {
        1: {
            "Bedroom - Alicia": off_light_state,
            "Bedroom - Tim": off_light_state
        },
        2: {
            "Bedroom - Alicia": plain_white_light_state,
            "Bedroom - Tim": plain_white_light_state
        },
        # 3: # bring back the red
        4: all_lights_off
    }
}

state = bridge.get_api()

def identifier(kind, uuid=None, name=None):
    for other_identifier, config in state[kind].iteritems():
        if kind == "sensors" and not config["modelid"] == "ZGPSWITCH":
            continue
        if (uuid and config["uniqueid"] == uuid) or (name and config["name"] == name):
            return other_identifier
    return None

def path(kind, **kwargs):
    return makePath(kind, identifier(kind, **kwargs))

def dump(kind):
    for identifier, config in sorted(bridge.get_api()[kind].iteritems(), key=lambda k: int(k[0])):
        if kind == "sensors" and not config["modelid"] == "ZGPSWITCH":
            continue
        print identifier, config["uniqueid"], config["name"]

def dumpAll(kind):
    printer = pprint.PrettyPrinter(indent=4)
    printer.pprint(bridge.get_api()[kind])

def sensor(**kwargs):
    return path("sensors", **kwargs)

def light(**kwargs):
    return path("lights", **kwargs)

def read(path):
    return bridge.request('GET', makePath("/api", bridge.username, path))

def write(path, d):
    bridge.request('PUT', makePath("/api", bridge.username, path), json.dumps(d))

def writePost(path, d):
    bridge.request('POST', makePath("/api", bridge.username, path), json.dumps(d))

def delete(path):
    bridge.request('DELETE', makePath("/api", bridge.username, path))

def makePath(*args):
    return os.path.join(*args)

def valueForButtonNumber(button_number):
    if button_number == 1:
        return "34"
    elif button_number == 2:
        return "16"
    elif button_number == 3:
        return "17"
    elif button_number == 4:
        return "18"
    return "unknown"

def ruleMentionsSensor(rule_id, sensor_id):
    for condition in state["rules"][rule_id]["conditions"]:
        if condition["address"].startswith("/sensors/" + sensor_id):
            return True
    return False

for sensor_uuid, sensor_name in sensors.iteritems():
    write(sensor(uuid=sensor_uuid), {"name": sensor_name})

for light_uuid, light_name in lights.iteritems():
    write(light(uuid=light_uuid), {"name": light_name})

state = bridge.get_api()

for sensor_name, mapping in sensor_mappings.iteritems():
    sensor_id = identifier("sensors", name=sensor_name)

    button_scene_id_map = {}

    # Build the scenes.
    for button_number, light_states in mapping.iteritems():
        scene_id = "tap" + sensor_id + "button" + str(button_number)
        button_scene_id_map[button_number] = scene_id
        mapped_light_states = {identifier("lights", name=name) : state for name, state in light_states.iteritems()}
        write(makePath("scenes", scene_id), {"name": sensor_name + ": Button " + str(button_number), "lights": mapped_light_states.keys(), "transitiontime": 8})
        for light_id, light_state in mapped_light_states.iteritems():
            write(makePath("scenes", scene_id, "lights", light_id, "state"), light_state)

    # Delete old rules.
    for rule_id in state["rules"].keys():
        if ruleMentionsSensor(rule_id, sensor_id):
            delete(makePath("rules", rule_id))

    # Build new rules.
    for button_number, scene_id in button_scene_id_map.iteritems():
        writePost(makePath("rules"), {
            "name": scene_id,
            "conditions": [{
                "address": makePath("/", "sensors", sensor_id, "state", "buttonevent"),
                "operator": "eq",
                "value": valueForButtonNumber(button_number)
            }, {
                "address": makePath("/", "sensors", sensor_id, "state", "lastupdated"),
                "operator": "dx"
            }],
            "actions": [{
                "address": "/groups/0/action",
                "body": {"scene": scene_id},
                "method": "PUT"
            }]
        })

state = bridge.get_api()

dumpAll("rules")
