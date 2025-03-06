import json
from datetime import datetime, timezone, timedelta
from sgp4.earth_gravity import wgs84
from sgp4.io import twoline2rv
import pymap3d as pm
from collections import defaultdict

from czml import *
from topology import Topology

# DOCUMENT_DURATION_HOURS = 24
DOCUMENT_DURATION_SECONDS = 60
TIME_STEP = 30
NUMBER_OF_POSITIONS = DOCUMENT_DURATION_SECONDS // TIME_STEP + 1


class CZMLManager:
    def __init__(
        self,
    ):
        pass

    def init(
        self,
        tle_filepath: str,
        facility_filepath: str,
    ):
        self.tle_filepath = tle_filepath
        self.facility_filepath = facility_filepath
        self.start_time = datetime.now(timezone.utc)
        # self.duration_hours = DOCUMENT_DURATION_HOURS
        self.duration_seconds = DOCUMENT_DURATION_SECONDS

        # self.stop_time = self.start_time + timedelta(hours=self.duration_hours)
        self.stop_time = self.start_time + timedelta(seconds=self.duration_seconds)
        self.start_time_str = self.start_time.isoformat()
        self.stop_time_str = self.stop_time.isoformat()
        self.interval_time_str = self.start_time_str + "/" + self.stop_time_str
        self.satellite_list = self.load_satellites()
        self.facility_list = self.load_facilities()
        self.node_dict = self.create_node_dict()

    def create_node_dict(self):
        node_dict = {}
        for sat in self.satellite_list:
            node_dict[sat.name] = "sat"
        for faclitiy in self.facility_list:
            node_dict[faclitiy.name] = "facility"
        return node_dict

    def refresh(self):
        self.start_time = datetime.now(timezone.utc)
        self.stop_time = self.start_time + timedelta(seconds=self.duration_seconds)
        self.start_time_str = self.start_time.isoformat()
        self.stop_time_str = self.stop_time.isoformat()
        self.interval_time_str = self.start_time_str + "/" + self.stop_time_str

    def get_mobility(self):
        self.refresh()
        dp = DocumentPacket(
            self.start_time_str,
            self.interval_time_str,
        )
        fps = []
        for facility in self.facility_list:
            xyz = list(pm.geodetic2ecef(facility.latitude, facility.longitude, 0))
            fps.append(
                FacilityPacket(
                    facility.name,
                    self.interval_time_str,
                    facility.type,
                    [xyz[0], xyz[1], xyz[2]],
                    [0, 255, 255, 255],
                )
            )
        sps = []
        for satellite in self.satellite_list:
            sps.append(
                SatellitePacket(
                    satellite.name,
                    self.interval_time_str,
                    self.start_time_str,
                    create_satellite_position_cartesian(
                        satellite.satellite_object,
                        NUMBER_OF_POSITIONS,
                        self.start_time,
                        TIME_STEP,
                    ),
                    [0, 255, 0, 0],
                )
            )

        ap = AccessPacket()
        czml = MobilityCZML(dp, fps, sps)
        return czml.data()

    def get_path(self, topology: Topology, node_name_list, utc_time) -> list:
        topology.update_topology_by_time(utc_time)
        return topology.get_path_by_node_name_list(node_name_list)

    def get_paths_by_time_range(
        self, topology, node_name_list, utc_time, interval_seconds
    ):
        paths = []
        for i in range(interval_seconds):
            paths.append(
                self.get_path(topology, node_name_list, utc_time + timedelta(seconds=i))
            )
        return paths

    def get_paths_czml_by_time_range(
        self, topology, node_name_list, utc_time, interval_seconds
    ):
        path_list = self.get_paths_by_time_range(
            topology, node_name_list, utc_time, interval_seconds
        )
        access_packet = AccessPacket()
        link_packet_list = self.convert_paths_to_link_czml(
            path_list, utc_time, interval_seconds
        )
        route_czml = RouteCZML(access_packet, link_packet_list)
        return route_czml.data()

    def convert_paths_to_link_czml(self, path_list, utc_time, interval_seconds):
        link_packet_list = []
        edges = self.convert_paths_to_edges(path_list, utc_time, interval_seconds)
        availability = (
            utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            + "/"
            + (utc_time + timedelta(seconds=interval_seconds)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
        )

        for edge in edges:
            if self.node_dict[edge[0]] == "sat":
                id1 = "Satellite/{}".format(edge[0])
            else:
                id1 = "Facility/{}".format(edge[0])
            if self.node_dict[edge[1]] == "sat":
                id2 = "Satellite/{}".format(edge[1])
            else:
                id2 = "Facility/{}".format(edge[1])

            link_packet = LinkPacket(
                id1, id2, availability, edges[edge], color=[0, 255, 0, 255]
            )
            link_packet_list.append(link_packet)
        return link_packet_list

    # Function to convert path data into edge time intervals
    def convert_paths_to_edges(self, paths, utc_time, time_interval):
        edge_times = defaultdict(list)

        # Iterate over each path with its time offset
        for offset, path in enumerate(paths):
            start_time = utc_time + timedelta(seconds=offset)

            # Iterate over consecutive pairs to form edges
            for i in range(len(path) - 1):
                edge = (path[i], path[i + 1])
                edge_times[edge].append(start_time)

        # Convert time list to time ranges
        edge_ranges = defaultdict(list)
        for edge, times in edge_times.items():
            times.sort()
            start = times[0]
            end = times[0]

            for t in times[1:]:
                if t == end + timedelta(seconds=1):
                    end = t
                else:
                    edge_ranges[edge].append((start, end + timedelta(seconds=1)))
                    start = t
                    end = t

            edge_ranges[edge].append((start, end + timedelta(seconds=1)))

        # Convert edge ranges to show format with boolean intervals
        full_range_start = utc_time
        full_range_end = utc_time + timedelta(seconds=time_interval - 1)
        show_intervals = {}

        def format_time(t):
            return t.strftime("%Y-%m-%dT%H:%M:%SZ")

        for edge, intervals in edge_ranges.items():
            show = []
            current_start = full_range_start

            for start, end in intervals:
                if start > current_start:
                    show.append(
                        {
                            "interval": f"{format_time(current_start)}/{format_time(start)}",
                            "boolean": False,
                        }
                    )
                show.append(
                    {
                        "interval": f"{format_time(start)}/{format_time(end)}",
                        "boolean": True,
                    }
                )
                current_start = end

            if current_start < full_range_end:
                show.append(
                    {
                        "interval": f"{format_time(current_start)}/{format_time(full_range_end)}",
                        "boolean": False,
                    }
                )

            show_intervals[edge] = show

        return show_intervals

    def load_satellites(self) -> list:
        l = []
        with open(self.tle_filepath, "r") as f:
            tles = f.read().splitlines()
        for i in range(len(tles)):
            if i % 3 == 0:
                l.append(
                    Satellite(tles[i], twoline2rv(tles[i + 1], tles[i + 2], wgs84))
                )
        return l

    def load_facilities(self) -> list:
        l = []
        with open(self.facility_filepath, "r") as f:
            data = json.load(f)
        for name, properties in data.items():
            l.append(
                Facility(
                    name,
                    properties["type"],
                    properties["latitude"],
                    properties["longitude"],
                )
            )
        return l


if __name__ == "__main__":
    TLE_FILEPATH = "./data/three.tle"
    GROUND_EQUIPMENTS_FILEPATH = "./data/facilities.json"
    czmlManager = CZMLManager()
    czmlManager.init(TLE_FILEPATH, GROUND_EQUIPMENTS_FILEPATH)
    print(json.dumps(czmlManager.get_mobility()))
