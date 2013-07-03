import SimpleXMLRPCServer
import xmlrpclib

class AgentListClass:
    agents = [
        ["Red", True],
        ["Hot", False],
        ["Chili", True],
        ["Peppers", False] ]

    def getAgents(self):
        return self.agents

    def appendAgentList(self, name, status):
        self.agents.append([name, status])
        return xmlrpclib.Boolean(True)

    def deleteAgent(self, agent):
        lv_index = 0
        for i in self.agents:
            if (self.agents[lv_index][0] == agent):
                del self.agents[lv_index]
            else:
                lv_index = lv_index+1
        return xmlrpclib.Boolean(True)

    def initAgentList(self):
        self.agents = []
        self.agents.append(["Red", True])
        self.agents.append(["Hot", False])
        self.agents.append(["Chili", True])
        self.agents.append(["Pepper", False])
        return xmlrpclib.Boolean(True)


if __name__ == "__main__":
    AMS_AgentList_instance = AgentListClass()

    print "Hi I am a SPYSE emulator running just fine in my own process space here"
    print "I have created an instance of an agent list:"
    for agents in AMS_AgentList_instance.getAgents():
        print agents

    server = SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", 8888))
    server.register_instance(AMS_AgentList_instance)
    print "You can call the method initAgentList(), getAgents(), appendAgentList(agent, status) and deleteAgent(agent) on this instance through port 8888"
    print "Waiting for your XML-RPC call forever ..."
    server.serve_forever()

