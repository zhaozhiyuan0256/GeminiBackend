import json
from datetime import timedelta


GOURNDSTATION_IMAGE_URI = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAACvSURBVDhPrZDRDcMgDAU9GqN0lIzijw6SUbJJygUeNQgSqepJTyHG91LVVpwDdfxM3T9TSl1EXZvDwii471fivK73cBFFQNTT/d2KoGpfGOpSIkhUpgUMxq9DFEsWv4IXhlyCnhBFnZcFEEuYqbiUlNwWgMTdrZ3JbQFoEVG53rd8ztG9aPJMnBUQf/VFraBJeWnLS0RfjbKyLJA8FkT5seDYS1Qwyv8t0B/5C2ZmH2/eTGNNBgMmAAAAAElFTkSuQmCC",
USEREQUIPMENT_IMAGE_URI = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAIGNIUk0AAHomAACAhAAA+gAAAIDoAAB1MAAA6mAAADqYAAAXcJy6UTwAAADYUExURQAAAEzD/1DF/0/E/0zD/0zD/0vD/0vC/03D/0vD/0zD/0zD/0zD/0zD/0zD/0rC/1bG/0zD/0nC/0nC/1nH/03D/0fB/1jH/0jC/07E/0vD/0zD/0zD/0zD/0zD/0zD/0zD/0vD/0zD/0zD/03D/1LF/1TG/17J/1zI/1DE/6Pg/7Tm/7Xm/4zY/7vo/8/v/87v/9Dv/57e/7ro/83u/8zu/5ze/53e/7Pl/8bs/8Tr/8fs/5fc/2LK/2bM/3nS/3HP/1vI/0vD/0rC/27O/1/J/0nC/////1RHxfQAAAAkdFJOUwAAAAAogIODg4VVAVSuA1P8rANT/KwD/AP8A1P9qx5iZGRmQAjlJIAAAAABYktHREdgvcl7AAAAB3RJTUUH6QIbBiEGYTavcAAAAIRJREFUGNNjYGBgBAEmZjDFAAKMLKxs7Bwc7Jxc3FABHhVVNXUNNU1ePqgAv4CWtra2jq6gEFRAWERP38DA0EhUDC5gbGJqamBGbQEDU1N9c7gAv7iFpZWVtY2gBMylkrZ29g52joJSUAFpGSdnF1c3J1mY0+XkFRQUFRWUlGGeQwIMDADkLxQ8MqFFgwAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAyNS0wMi0yN1QwNjozMjo1OSswMDowMPru3ScAAAAldEVYdGRhdGU6bW9kaWZ5ADIwMjUtMDItMjdUMDY6MzI6NTkrMDA6MDCLs2WbAAAAKHRFWHRkYXRlOnRpbWVzdGFtcAAyMDI1LTAyLTI3VDA2OjMzOjA2KzAwOjAwjcxR9wAAAABJRU5ErkJggg=="
SATELLITE_IMAGE_URI = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADJSURBVDhPnZHRDcMgEEMZjVEYpaNklIzSEfLfD4qNnXAJSFWfhO7w2Zc0Tf9QG2rXrEzSUeZLOGm47WoH95x3Hl3jEgilvDgsOQUTqsNl68ezEwn1vae6lceSEEYvvWNT/Rxc4CXQNGadho1NXoJ+9iaqc2xi2xbt23PJCDIB6TQjOC6Bho/sDy3fBQT8PrVhibU7yBFcEPaRxOoeTwbwByCOYf9VGp1BYI1BA+EeHhmfzKbBoJEQwn1yzUZtyspIQUha85MpkNIXB7GizqDEECsAAAAASUVORK5CYII="
ACCESS_UUID = "9927edc4-e87a-4e1f-9b8b-0bfb3b05b227"


def create_satellite_position_cartesian(
    satellite_object, number_of_positions, start_time, time_step
) -> list:
    cur_time_step = 0
    output = []
    for _ in range(number_of_positions):
        current_time = start_time + timedelta(seconds=cur_time_step)
        eci_position, _ = satellite_object.propagate(
            current_time.year,
            current_time.month,
            current_time.day,
            current_time.hour,
            current_time.minute,
            current_time.second,
        )

        output.append(cur_time_step)
        output.append(eci_position[0] * 1000)  # converts km's to m's
        output.append(eci_position[1] * 1000)
        output.append(eci_position[2] * 1000)
        cur_time_step += time_step

    return output


class Satellite:
    def __init__(self, name, satellite_object):
        self.name = name
        self.satellite_object = satellite_object

    def __str__(self):
        return json.dumps(
            {"name": self.name, "satellite_object": self.satellite_object}
        )


class Facility:
    def __init__(self, name, type, latitude, longitude):
        self.name = name
        self.type = type
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return json.dumps(
            {
                "name": self.name,
                "type": self.type,
                "latitude": self.latitude,
                "longitude": self.longitude,
            }
        )


class MobilityCZML:
    def __init__(
        self,
        document_packet,
        facility_packets,
        satellite_packets,
        # access_packet,
        # link_packets,
    ):
        self.document_packet = document_packet
        self.facility_packets = facility_packets
        self.satellite_packets = satellite_packets
        # self.access_packet = access_packet
        # self.link_packets = link_packets

    def data(self):
        d = []
        d.append(self.document_packet.data())
        for facility_packet in self.facility_packets:
            d.append(facility_packet.data())
        for satellite_packet in self.satellite_packets:
            d.append(satellite_packet.data())
        # d.append(self.access_packet.data())
        # for link_packet in self.link_packets:
        #     d.append(link_packet.data())
        return d


class RouteCZML:
    def __init__(
        self,
        access_packet,
        link_packets,
    ):
        self.access_packet = access_packet
        self.link_packets = link_packets

    def data(self):
        d = []
        d.append(self.access_packet.data())
        for link_packet in self.link_packets:
            d.append(link_packet.data())
        return d


class Packet(object):

    _properties = ()

    @property
    def properties(self):
        return self._properties

    def __init__(self):
        pass

    def __str__(self):
        return json.dumps(self.data())

    def data(self):
        d = {}
        for attr in self.properties:
            d[attr] = getattr(self, attr)
        return d


class DocumentPacket(Packet):

    _properties = ("id", "version", "clock")

    def __init__(self, current_time: str, interval: str):
        self.id = "document"
        self.version = "1.0"
        self.clock = dict()
        self.clock["currentTime"] = current_time
        self.clock["multiplier"] = 1
        self.clock["interval"] = interval
        self.clock["range"] = "CLAMPED"
        self.clock["step"] = "SYSTEM_CLOCK_MULTIPLIER"


class FacilityPacket(Packet):

    _properties = (
        "id",
        "name",
        "description",
        "availability",
        "billboard",
        "label",
        "position",
    )

    def __init__(
        self,
        name: str,
        availability: str,
        facility_type: str,
        position: list,
        color: list,
    ):
        """
        facility_type: groundstation or ue
        position: [X, Y, Z]
        color: [r, g, b, a]
        """
        self.id = "Facility/{}".format(name)
        self.name = name
        self.availability = availability
        self.description = "Facility name: {}".format(name)
        self.billboard = self.create_billboard(facility_type)
        self.label = self.create_label(facility_type, color)
        self.position = {"cartesian": position}

    def create_billboard(self, facility_type) -> dict:
        return {
            "show": True,
            "image": (
                GOURNDSTATION_IMAGE_URI
                if facility_type == "core"
                else USEREQUIPMENT_IMAGE_URI
            ),
            "scale": 1.5,
        }

    def create_label(self, facility_type, color) -> dict:
        label = dict()
        label["fillColor"] = {"rgba": color}
        label["font"] = "11pt Lucida Console"
        label["horizontalOrigin"] = "LEFT"
        label["outlineColor"] = {"rgba": [0, 0, 0, 255]}
        label["outlineWidth"] = 2
        label["pixelOffset"] = ({"cartesian2": [12, 0]},)
        label["show"] = True
        label["style"] = "FILL_AND_OUTLINE"
        if facility_type == "core":
            label["text"] = "Core"
        elif facility_type == "ue":
            label["text"] = "User Equipment"
        label["verticalOrigin"] = "CENTER"
        return label


class SatellitePacket(Packet):

    _properties = (
        "id",
        "description",
        "availability",
        "billboard",
        "label",
        "position",
    )

    def __init__(
        self, name: str, availability: str, epoch: str, cartesian: list, color: list
    ):
        """
        color: [r, g, b, a]
        """
        self.id = "Satellite/{}".format(name)
        self.description = "Satellite name: {}".format(name)
        self.availability = availability
        self.billboard = self.create_billboard()
        self.label = self.create_label(name, color)
        self.position = self.create_position(epoch, cartesian)

    def create_billboard(self) -> dict:
        return {"show": True, "image": SATELLITE_IMAGE_URI, "scale": 1.5}

    def create_label(self, name, color) -> dict:
        label = dict()
        label["show"] = True
        label["text"] = name
        label["horizontalOrigin"] = "LEFT"
        label["pixelOffset"] = {"cartesian2": [12, 0]}
        label["fillColor"] = {"rgba": [0, 255, 0, 255]}
        label["font"] = "11pt Lucida Console"
        label["outlineColor"] = {"rgba": color}
        label["outlineWidth"] = 2
        return label

    def create_position(self, epoch, cartesian) -> dict:
        return {
            "epoch": epoch,
            "cartesian": cartesian,
            "interpolationAlgorithm": "LAGRANGE",
            "interpolationDegree": 5,
            "referenceFrame": "INERTIAL",
        }


class AccessPacket(Packet):

    _properties = ("id", "name", "description")

    def __init__(self):
        self.id = ACCESS_UUID
        self.name = "Accesses"
        self.description = "List of Accesses"


class LinkPacket(Packet):

    _properties = ("id", "name", "parent", "availability", "description", "polyline")

    def __init__(self, id1: str, id2: str, availability: str, show: list, color: list):
        self.id = id1 + "-to-" + id2
        self.name = self.id
        self.parent = ACCESS_UUID
        self.availability = availability
        self.description = self.id
        self.polyline = self.create_polyline(id1, id2, show, color)

    def create_polyline(self, id1, id2, show, color):
        return {
            "show": show,
            "width": 1,
            "material": {"solidColor": {"color": {"rgba": color}}},
            "arcType": "NONE",
            "positions": {
                "references": ["{}#position".format(id1), "{}#position".format(id2)]
            },
        }
