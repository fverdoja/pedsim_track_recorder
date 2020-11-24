#!/usr/bin/env python

import rospy
import os.path

from pedsim_msgs.msg import AgentStates


class AgentTrack:
    def __init__(self, id):
        self.id = id
        self.track = []

    def track_to_string(self):
        track_string = ""

        for point in self.track:
            track_string += "%f\t%f\t%f\n" % (point.x, point.y, point.z)

        return track_string

    def __cmp__(self, other):
        return cmp(self.id, other.id)


class PedsimTrackRecorder:
    def __init__(self, save_folder=".", filename_template="track"):
        self.save_folder = save_folder
        self.filename_template = filename_template
        self.agents = []

    def save_tracks(self):
        rospy.loginfo("Saving track files...")
        for agent in self.agents:
            agent_id = str(agent.id)
            filename = os.path.join(save_folder, filename_template
                                    + "_" + agent_id)
            rospy.loginfo("agent %s on %s" % (agent_id, filename))
            with open(filename, "w") as f:
                f.write(agent.track_to_string())

    def add_new_agent(self, id):
        agent = AgentTrack(id)
        self.agents.append(agent)
        self.agents.sort()
        return self.agents.index(agent)

    def add_point_to_track(self, id, point):
        found = False

        for agent in self.agents:
            if agent.id == id:
                agent.track.append(point)
                found = True

        if not found:
            i = self.add_new_agent(id)
            self.agents[i].track.append(point)

    def callback(self, data):
        for agent in data.agent_states:
            pos = agent.pose.position
            # orientation = agent.pose.orientation
            rospy.loginfo("ID%d in (%f, %f, %f)" %
                          (agent.id, pos.x, pos.y, pos.z))
            self.add_point_to_track(agent.id, pos)


if __name__ == '__main__':
    rospy.init_node('pedsim_track_recorder', anonymous=True)

    save_folder = rospy.get_param("~save_folder", ".")
    filename_template = rospy.get_param("~filename_template", "track")
    track_topic = rospy.get_param(
        "~track_topic", "/pedsim_simulator/simulated_agents")

    pedsim_track_recorder = PedsimTrackRecorder(save_folder, filename_template)

    rospy.Subscriber(track_topic, AgentStates, pedsim_track_recorder.callback)

    rospy.on_shutdown(pedsim_track_recorder.save_tracks)

    rospy.spin()
