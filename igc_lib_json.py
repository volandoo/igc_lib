#!/usr/bin/env python
from __future__ import print_function

import os
import sys

import json
import igc_lib
import lib.dumpers as dumpers


def dump_json(flight):
    thermals_data = []
    for thermal in flight.thermals:
        thermals_data.append({
            "duration": thermal.time_change(),
            "alt_change": thermal.alt_change(),
            "vertical_velocity": thermal.vertical_velocity(),
            "direction": thermal.direction,
            "started": thermal.enter_fix.timestamp,
            "time_per_circle": thermal.time_per_circle,
            "enter": {"lat":thermal.enter_fix.lat, "lon":thermal.enter_fix.lon, "alt": thermal.enter_fix.alt},
            "exit": {"lat":thermal.exit_fix.lat, "lon":thermal.exit_fix.lon,"alt":thermal.exit_fix.alt}
        })
    
    glides_data = []
    for glide in flight.glides:
        glides_data.append({
            "duration": glide.time_change(),
            "alt_change": glide.alt_change(),
            "glide_ratio": glide.glide_ratio(),
            "speed": glide.speed(),
            "started": glide.enter_fix.timestamp,
            "enter": {"lat":glide.enter_fix.lat, "lon":glide.enter_fix.lon, "alt": glide.enter_fix.alt},
            "exit": {"lat":glide.exit_fix.lat, "lon":glide.exit_fix.lon,"alt":glide.exit_fix.alt}
            })
    
    flight_data = {
        "thermals": thermals_data,
        "glides": glides_data
    }
    
    print(json.dumps(flight_data, indent=2))




def main():

    print("Starting igc_lib_json")
    if len(sys.argv) < 2:
        print("Usage: %s file.igc [file.lkt]" % sys.argv[0])
        sys.exit(1)

    input_file = sys.argv[1]

    flight = igc_lib.Flight.create_from_file(input_file)
    if not flight.valid:
        print("Provided flight is invalid:")
        print(flight.notes)
        sys.exit(1)

    dump_json(flight)



if __name__ == "__main__":
    main()
