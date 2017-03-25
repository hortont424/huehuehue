#!/usr/bin/env python

from phue import Bridge
import pprint
import json
import os
import sys

bridge = Bridge('192.168.7.32')
bridge.connect()

bridge_state = bridge.get_api()
pprint.pprint(bridge_state)

print "Lights:"

for light_num, light in bridge_state["lights"].iteritems():
    print "\t", light["uniqueid"], light["name"]

print "Sensors:"

for sensor_num, sensor in bridge_state["sensors"].iteritems():
    if not "uniqueid" in sensor:
        continue
    print "\t", sensor["uniqueid"], sensor["name"]

sensors = {
    # Tap
    "00:00:00:00:00:40:92:15-f2": "Kitchen Door",
    "00:00:00:00:00:42:06:3b-f2": "Gym Door",
    "00:00:00:00:00:43:c1:9b-f2": "Bedroom Nightstand",
    "00:00:00:00:00:43:1c:9f-f2": "Bedroom Door Outer",
    "00:00:00:00:00:42:a3:1b-f2": "Tim Office",
    "00:00:00:00:00:41:e4:f4-f2": "Alicia Office",
    "00:00:00:00:00:41:e7:c0-f2": "Den",
    "00:00:00:00:00:42:8e:8c-f2": "Bedroom Door Inner",
    "00:00:00:00:00:47:2f:3b-f2": "Front Door",
    "00:00:00:00:00:40:a4:a1-f2": "Kitchen Entryway",

    # Dimmer
    # "00:17:88:01:02:0f:56:79-02-fc00": "Hue dimmer switch 1",
}

lights = {
    # Bedroom
    "00:17:88:01:00:b6:43:01-0b": "Bedroom Overhead 1",
    "00:17:88:01:00:b1:91:e2-0b": "Bedroom Overhead 2",
    "00:17:88:01:00:ba:63:38-0b": "Bedroom Overhead 3",
    "00:17:88:01:00:1c:57:ea-0b": "Bedroom Floor Tim",
    "00:17:88:01:02:4b:13:ee-0b": "Bedroom Table Tim",
    "00:17:88:01:00:1c:57:ae-0b": "Bedroom Floor Alicia",
    "00:17:88:01:02:45:47:e9-0b": "Bedroom Table Alicia",

    # Alicia's Office
    "00:17:88:01:02:2a:1c:5b-0b": "Alicia Office Table",
    "00:17:88:01:02:4b:72:ba-0b": "Alicia Office Overhead",
    "00:17:88:01:01:15:d7:77-0b": "Alicia Office Floor 1",
    "00:17:88:01:01:15:5b:f4-0b": "Alicia Office Floor 2",

    # Tim's Office
    "00:17:88:01:02:45:47:7d-0b": "Tim Office 1",
    "00:17:88:01:02:45:47:be-0b": "Tim Office 2",
    "00:17:88:01:01:17:ce:9d-0b": "Tim Office Floor 1",
    "00:17:88:01:01:16:01:cb-0b": "Tim Office Floor 2",

    # Tim's Bathroom
    "00:17:88:01:02:3a:c6:48-0b": "Tim Bath 1",
    "00:17:88:01:02:3a:c7:6b-0b": "Tim Bath 2",
    "00:17:88:01:02:3a:c0:79-0b": "Tim Bath 3",

    # Hallway
    "00:17:88:01:02:45:a8:30-0b": "Hallway West 1",
    "00:17:88:01:02:4b:14:55-0b": "Hallway West 2",
    "00:17:88:01:02:45:6f:da-0b": "Hallway East 1",
    "00:17:88:01:02:45:6c:ac-0b": "Hallway East 2",
    "00:17:88:01:02:21:5a:bc-0b": "Hallway Flood",

    # Den
    "00:17:88:01:00:b6:43:72-0b": "Den Overhead 1",
    "00:17:88:01:00:b6:45:31-0b": "Den Overhead 2",
    "00:17:88:01:00:ba:56:b2-0b": "Den Overhead 3",

    # Gym
    "00:17:88:01:02:3a:d1:19-0b": "Gym Standing 1",
    "00:17:88:01:02:3e:7c:d7-0b": "Gym Standing 2",
    "00:17:88:01:02:45:a7:bb-0b": "Gym Overhead 1",
    "00:17:88:01:02:2a:46:e4-0b": "Gym Overhead 2",
    "00:17:88:01:02:2a:47:4b-0b": "Gym Overhead 3",

    # Dining Room
    "00:17:88:01:01:17:68:78-0b": "Dining Room Floor Left",
    "00:17:88:01:01:16:71:d8-0b": "Dining Room Floor Right",
    "00:17:88:01:02:3e:7b:a1-0b": "Dining Room Standing",
}

def color_temperature_to_mireds(kelvin):
    return int(1000000. / kelvin)

plain_white_light_for_whiteambiance_state = {
    "bri": 255,
    "effect": "none",
    "on": True,
    "ct": color_temperature_to_mireds(2700)
}

plain_white_light_state = {
    "bri": 255,
    "effect": "none",
    "on": True,
    "xy": [0.459867518, 0.410600974],
}

alicia_night_light_state = {
    "bri": 127,
    "effect": "none",
    "on": True,
    "xy": [0.4384, 0.3606]
}

off_light_state = {
    "on": False
}

all_lights_off = {}
for _, light_name in lights.iteritems():
    all_lights_off[light_name] = off_light_state

sensor_mappings = {
    "Kitchen Door": {
        1: {
            "Dining Room Floor Left": off_light_state,
            "Dining Room Floor Right": off_light_state,
            "Dining Room Standing": off_light_state,
        },
        2: {
            "Dining Room Floor Left": plain_white_light_state,
            "Dining Room Floor Right": plain_white_light_state,
            "Dining Room Standing": plain_white_light_state,
        },
        3: {
            "Hallway West 1": plain_white_light_state,
            "Hallway West 2": plain_white_light_state,
            "Hallway East 1": plain_white_light_state,
            "Hallway East 2": plain_white_light_state,
            "Hallway Flood": plain_white_light_for_whiteambiance_state,
        },
        4: {
            "Hallway West 1": off_light_state,
            "Hallway West 2": off_light_state,
            "Hallway East 1": off_light_state,
            "Hallway East 2": off_light_state,
            "Hallway Flood": off_light_state,
        }
    },
    "Gym Door": {
        1: {
            "Gym Standing 1": off_light_state,
            "Gym Standing 2": off_light_state,
            "Gym Overhead 1": off_light_state,
            "Gym Overhead 2": off_light_state,
            "Gym Overhead 3": off_light_state,
        },
        2: {
            "Gym Standing 1": plain_white_light_state,
            "Gym Standing 2": plain_white_light_state,
            "Gym Overhead 1": plain_white_light_state,
            "Gym Overhead 2": plain_white_light_state,
            "Gym Overhead 3": plain_white_light_state,
        },
        3: {
        },
        4: {
        }
    },
    "Bedroom Door Outer": {
        1: {
            "Hallway West 1": off_light_state,
            "Hallway West 2": off_light_state,
            "Hallway East 1": off_light_state,
            "Hallway East 2": off_light_state,
            "Hallway Flood": off_light_state,
        },
        2: {
            "Hallway West 1": plain_white_light_state,
            "Hallway West 2": plain_white_light_state,
            "Hallway East 1": plain_white_light_state,
            "Hallway East 2": plain_white_light_state,
            "Hallway Flood": plain_white_light_state,
        },
        3: {
            "Bedroom Overhead 1": plain_white_light_state,
            "Bedroom Overhead 2": plain_white_light_state,
            "Bedroom Overhead 3": plain_white_light_state,
            "Bedroom Floor Tim": plain_white_light_state,
            "Bedroom Table Tim": plain_white_light_state,
            "Bedroom Floor Alicia": plain_white_light_state,
            "Bedroom Table Alicia": plain_white_light_state,
        },
        4: {
            "Bedroom Overhead 1": off_light_state,
            "Bedroom Overhead 2": off_light_state,
            "Bedroom Overhead 3": off_light_state,
            "Bedroom Floor Tim": off_light_state,
            "Bedroom Table Tim": off_light_state,
            "Bedroom Floor Alicia": off_light_state,
            "Bedroom Table Alicia": off_light_state,
        }
    },
    "Bedroom Nightstand": {
        1: {
            "Bedroom Overhead 1": off_light_state,
            "Bedroom Overhead 2": off_light_state,
            "Bedroom Overhead 3": off_light_state,
            "Bedroom Floor Tim": off_light_state,
            "Bedroom Table Tim": off_light_state,
            "Bedroom Floor Alicia": off_light_state,
            "Bedroom Table Alicia": off_light_state,
        },
        2: {
            "Bedroom Floor Tim": plain_white_light_state,
            "Bedroom Table Tim": plain_white_light_state,
            "Bedroom Floor Alicia": plain_white_light_state,
            "Bedroom Table Alicia": plain_white_light_state,
            "Bedroom Overhead 1": off_light_state,
            "Bedroom Overhead 2": off_light_state,
            "Bedroom Overhead 3": off_light_state,
        },
        3: {
            "Bedroom Floor Tim": alicia_night_light_state,
            "Bedroom Floor Alicia": alicia_night_light_state,
            "Bedroom Table Tim": off_light_state,
            "Bedroom Table Alicia": off_light_state,
            "Bedroom Overhead 1": off_light_state,
            "Bedroom Overhead 2": off_light_state,
            "Bedroom Overhead 3": off_light_state,
        },
        4: all_lights_off
    },
    "Bedroom Door Inner": {
        1: {
            "Bedroom Overhead 1": off_light_state,
            "Bedroom Overhead 2": off_light_state,
            "Bedroom Overhead 3": off_light_state,
            "Bedroom Floor Tim": off_light_state,
            "Bedroom Table Tim": off_light_state,
            "Bedroom Floor Alicia": off_light_state,
            "Bedroom Table Alicia": off_light_state,
        },
        2: {
            "Bedroom Overhead 1": plain_white_light_state,
            "Bedroom Overhead 2": plain_white_light_state,
            "Bedroom Overhead 3": plain_white_light_state,
            "Bedroom Floor Tim": plain_white_light_state,
            "Bedroom Table Tim": plain_white_light_state,
            "Bedroom Floor Alicia": plain_white_light_state,
            "Bedroom Table Alicia": plain_white_light_state,
        },
        3: {
            "Bedroom Floor Tim": plain_white_light_state,
            "Bedroom Floor Alicia": plain_white_light_state,
            "Bedroom Table Tim": plain_white_light_state,
            "Bedroom Table Alicia": plain_white_light_state,
            "Bedroom Overhead 1": off_light_state,
            "Bedroom Overhead 2": off_light_state,
            "Bedroom Overhead 3": off_light_state,
        },
        4: all_lights_off
    },
    "Tim Office": {
        1: {
            "Tim Office 1": off_light_state,
            "Tim Office 2": off_light_state,
            "Tim Office Floor 1": off_light_state,
            "Tim Office Floor 2": off_light_state,
        },
        2: {
            "Tim Office 1": plain_white_light_state,
            "Tim Office 2": plain_white_light_state,
            "Tim Office Floor 1": plain_white_light_state,
            "Tim Office Floor 2": plain_white_light_state,
        },
        3: {
            "Tim Office 1": alicia_night_light_state,
            "Tim Office 2": alicia_night_light_state,
            "Tim Office Floor 1": alicia_night_light_state,
            "Tim Office Floor 2": alicia_night_light_state,
        },
        4: {
            "Hallway West 1": plain_white_light_state,
            "Hallway West 2": plain_white_light_state,
            "Hallway East 1": plain_white_light_state,
            "Hallway East 2": plain_white_light_state,
            "Hallway Flood": plain_white_light_for_whiteambiance_state,
        }
    },
    "Alicia Office": {
        1: {
            "Alicia Office Table": off_light_state,
            "Alicia Office Overhead": off_light_state,
            "Alicia Office Floor 1": off_light_state,
            "Alicia Office Floor 2": off_light_state,
        },
        2: {
            "Alicia Office Table": plain_white_light_state,
            "Alicia Office Overhead": plain_white_light_state,
            "Alicia Office Floor 1": plain_white_light_state,
            "Alicia Office Floor 2": plain_white_light_state,
        },
        3: {
            "Alicia Office Table": alicia_night_light_state,
            "Alicia Office Overhead": alicia_night_light_state,
            "Alicia Office Floor 1": alicia_night_light_state,
            "Alicia Office Floor 2": alicia_night_light_state,
        },
        4: {
            "Hallway West 1": plain_white_light_state,
            "Hallway West 2": plain_white_light_state,
            "Hallway East 1": plain_white_light_state,
            "Hallway East 2": plain_white_light_state,
            "Hallway Flood": plain_white_light_for_whiteambiance_state,
        }
    },
    "Front Door": {
        1: {
            "Hallway West 1": off_light_state,
            "Hallway West 2": off_light_state,
            "Hallway East 1": off_light_state,
            "Hallway East 2": off_light_state,
            "Hallway Flood": off_light_state,
        },
        2: {
            "Hallway West 1": plain_white_light_state,
            "Hallway West 2": plain_white_light_state,
            "Hallway East 1": plain_white_light_state,
            "Hallway East 2": plain_white_light_state,
            "Hallway Flood": plain_white_light_for_whiteambiance_state,
        },
        3: {
        },
        4: all_lights_off
    },
    "Kitchen Entryway": {
        1: {
            "Dining Room Floor Left": off_light_state,
            "Dining Room Floor Right": off_light_state,
            "Dining Room Standing": off_light_state,
        },
        2: {
            "Dining Room Floor Left": plain_white_light_state,
            "Dining Room Floor Right": plain_white_light_state,
            "Dining Room Standing": plain_white_light_state,
        },
        3: {
        },
        4: all_lights_off
    },
    "Den": {
        1: {
            "Den Overhead 1": off_light_state,
            "Den Overhead 2": off_light_state,
            "Den Overhead 3": off_light_state,
        },
        2: {
            "Den Overhead 1": plain_white_light_state,
            "Den Overhead 2": plain_white_light_state,
            "Den Overhead 3": plain_white_light_state,
        },
        3: {
            "Den Overhead 1": alicia_night_light_state,
            "Den Overhead 2": alicia_night_light_state,
            "Den Overhead 3": alicia_night_light_state,
        },
        4: {
            "Hallway West 1": plain_white_light_state,
            "Hallway West 2": plain_white_light_state,
            "Hallway East 1": plain_white_light_state,
            "Hallway East 2": plain_white_light_state,
            "Hallway Flood": plain_white_light_for_whiteambiance_state,
        }
    },
}

state = bridge.get_api()

def identifier(kind, uuid=None, name=None):
    for other_identifier, config in state[kind].iteritems():
        if kind == "sensors" and not config["modelid"] == "ZGPSWITCH":
            continue
        if (uuid and config["uniqueid"] == uuid) or (name and config["name"] == name):
            return other_identifier
    print "Didn't find a identifier for", name or uuid
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
    print "Setting name", light_name, "for light", light_uuid
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
