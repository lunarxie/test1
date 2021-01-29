import networkx as nx
import random
from NodeType import NodeType
import ConstValue


class Model:

    # 必须传入带有权重的图，权重字段weight
    def __init__(self, graph=nx.Graph(), seed=0):
        self.init_list()
        self.graph = graph
        self.seed = seed
        self.birth_nodes = 1000

    def init_list(self):
        self.all_susceptible_nodes = list()
        self.all_exposed_nodes = list()
        self.all_infect_nodes = list()
        self.all_recovered_nodes = list()

        self.all_birth_nodes = list()
        self.all_death_nodes = list()
        #
        self.susceptible_list = list()
        self.exposed_list = list()
        self.infect_list = list()
        self.recovered_list = list()

        self.birth_list = list()
        self.death_list = list()

    def sir_model(self, s2i=0.1, i2r=0.3, rate=10):  # SIR 模型
        print('---------------SIR Init Start-------------------')
        self.init_list()
        # 初始化易感染节点列表和数量
        for node in self.graph.nodes:
            if node != self.seed:
                self.all_susceptible_nodes.append(node)
        self.susceptible_list.append(len(self.all_susceptible_nodes))

        # 初始化感染节点列表和数量
        self.all_infect_nodes.append(self.seed)
        self.infect_list.append(len(self.all_infect_nodes))
        self.graph.nodes[self.seed]['state'] = NodeType.INFECT

        # 初始化恢复节点列表和数量
        self.recovered_list.append(len(self.all_recovered_nodes))

        #print('---------------SIR Diffusion-------------------')
        while True:
            if len(self.all_infect_nodes) <= 0:
                break
            tmp_infect_nodes = list()
            # 传染
            for i_node in self.all_infect_nodes:
                s_nodes = self.graph.neighbors(i_node)
                rate_count = 0
                for s_node in s_nodes:
                    if self.graph.nodes[s_node]['state'] == NodeType.SUSCEPTIBLE:
                        rate_count = rate_count + 1
                        if rate_count >= rate:
                            break
                        edge = self.graph.get_edge_data(i_node, s_node)
                        if random.uniform(0, 1) < edge['weight']*s2i:
                            tmp_infect_nodes.append(s_node)
            for s_node in tmp_infect_nodes:
                if s_node in self.all_susceptible_nodes:
                    self.graph.nodes[s_node]['state'] = NodeType.INFECT
                    self.all_infect_nodes.append(s_node)
                    self.all_susceptible_nodes.remove(s_node)
            # 恢复
            for i_node in self.all_infect_nodes:
                if random.uniform(0, 1) < i2r:
                    self.all_infect_nodes.remove(i_node)
                    self.all_recovered_nodes.append(i_node)
                    self.graph.nodes[i_node]['state'] = NodeType.RECOVERED
            # 计算节点数
            self.susceptible_list.append(len(self.all_susceptible_nodes))
            self.infect_list.append(len(self.all_infect_nodes))
            self.recovered_list.append(len(self.all_recovered_nodes))
        print('-----------SIR END-----------')
        return self.susceptible_list, self.infect_list, self.recovered_list

    def sir_birth_death_model(self, s2i=0.1, i2r=0.3, rate=10, birth_rate=ConstValue.birth_rate, death_rate=0.01):  # SIR modify
        print('---------------sir_birth_death Init Start-------------------')
        # 初始化易感染节点列表和数量
        for node in self.graph.nodes:
            if node != self.seed:
                self.all_susceptible_nodes.append(node)
        self.susceptible_list.append(len(self.all_susceptible_nodes) - self.birth_nodes)
        # 出生人口列表
        for i in range(self.birth_nodes):
            num = random.uniform(0, len(self.all_susceptible_nodes))
            node = self.all_susceptible_nodes[int(num)]
            self.all_susceptible_nodes.remove(node)
            self.all_birth_nodes.append(node)
            self.graph.nodes[node]['state'] = NodeType.BIRTH

        # 初始化感染节点列表和数量
        self.all_infect_nodes.append(self.seed)
        self.infect_list.append(len(self.all_infect_nodes))
        self.graph.nodes[self.seed]['state'] = NodeType.INFECT

        # 初始化恢复节点列表和数量
        self.recovered_list.append(len(self.all_recovered_nodes))

        # 出生数量和死亡数量
        self.birth_list.append(0)
        self.death_list.append(0)

        while True:
            if len(self.all_infect_nodes) <= 0:
                break
            # print('------------------------出生人口 和 死亡人口 --------------------------')
            birth_s = self.birth(self.all_susceptible_nodes, NodeType.SUSCEPTIBLE, birth_rate)
            birth_i = self.birth(self.all_infect_nodes, NodeType.INFECT, birth_rate)
            birth_r = self.birth(self.all_recovered_nodes, NodeType.RECOVERED, birth_rate)
            # print(' susceptible : %s ,' % birth_s + 'infect : %s ,' % birth_i + ' recovered : %s' % birth_r)
            self.death()
            self.birth_list.append(birth_s + birth_i + birth_r)
            self.death_list.append(len(self.all_death_nodes))
            # print('--------------------------------------------------------------------')

            tmp_infect_nodes = list()
            # 传染
            for i_node in self.all_infect_nodes:
                s_nodes = self.graph.neighbors(i_node)
                rate_count = 0
                for s_node in s_nodes:
                    if self.graph.nodes[s_node]['state'] == NodeType.SUSCEPTIBLE:
                        rate_count = rate_count + 1
                        if rate_count >= rate:
                            break
                        edge = self.graph.get_edge_data(i_node, s_node)
                        if random.uniform(0, 1) < edge['weight'] * s2i:
                            tmp_infect_nodes.append(s_node)
            for s_node in tmp_infect_nodes:
                if s_node in self.all_susceptible_nodes:
                    self.graph.nodes[s_node]['state'] = NodeType.INFECT
                    self.all_infect_nodes.append(s_node)
                    self.all_susceptible_nodes.remove(s_node)
            # 恢复
            for i_node in self.all_infect_nodes:
                if random.uniform(0, 1) < i2r:
                    self.all_infect_nodes.remove(i_node)
                    self.all_recovered_nodes.append(i_node)
                    self.graph.nodes[i_node]['state'] = NodeType.RECOVERED
            # 计算节点数
            self.susceptible_list.append(len(self.all_susceptible_nodes))
            self.infect_list.append(len(self.all_infect_nodes))
            self.recovered_list.append(len(self.all_recovered_nodes))

        return self.susceptible_list, self.infect_list, self.recovered_list, self.birth_list, self.death_list

    def death(self):
        for death_node in self.graph.nodes:
            if self.graph.nodes[death_node]['state'] == NodeType.SUSCEPTIBLE:
                if random.uniform(0, 1) < ConstValue.s_death_rate:
                    self.all_death_nodes.append(death_node)
                    self.all_susceptible_nodes.remove(death_node)
                    self.graph.nodes[death_node]['state'] = NodeType.DEATH
            elif self.graph.nodes[death_node]['state'] == NodeType.INFECT:
                if random.uniform(0, 1) < ConstValue.i_death_rate:
                    self.all_death_nodes.append(death_node)
                    self.all_infect_nodes.remove(death_node)
                    self.graph.nodes[death_node]['state'] = NodeType.DEATH
            elif self.graph.nodes[death_node]['state'] == NodeType.RECOVERED:
                if random.uniform(0, 1) < ConstValue.r_death_rate:
                    self.all_death_nodes.append(death_node)
                    self.all_recovered_nodes.remove(death_node)
                    self.graph.nodes[death_node]['state'] = NodeType.DEATH

    def birth(self, type_nodes, node_state, birth_rate):
        birth_count = len(type_nodes) * birth_rate
        for i in range(int(birth_count)):
            if len(self.all_birth_nodes) > 0:
                birth_index = int(random.uniform(0, len(self.all_birth_nodes)))
                birth_node = self.all_birth_nodes[birth_index]
                self.graph.nodes[birth_node]['state'] = node_state
                self.all_birth_nodes.remove(birth_node)
                type_nodes.append(birth_node)
        return round(birth_count)

    def seir_model(self, s2e=0.3, e2i=0.3, i2r=0.2, hidden_day=2):
        print('---------------SIER Init Start-------------------')
        # 初始化易感染节点列表和数量
        for node in self.graph.nodes:
            if node != self.seed:
                self.all_susceptible_nodes.append(node)
        self.susceptible_list.append(len(self.all_susceptible_nodes))

        # 初始化暴露者节点列表和数量
        self.exposed_list.append(len(self.all_exposed_nodes))

        # 初始化感染者节点列表和数量
        self.all_infect_nodes.append(self.seed)
        self.infect_list.append(len(self.all_infect_nodes))
        self.graph.nodes[self.seed]['state'] = NodeType.INFECT

        # 初始化康复者节点列表和数量
        self.recovered_list.append(len(self.all_recovered_nodes))

        while True:
            if len(self.all_exposed_nodes) <= 0 and len(self.all_infect_nodes) <= 0:
                break
            tmp_infect_nodes = list()
            # 传染
            for infect_node in self.all_infect_nodes:
                neighbor_nodes = self.graph.neighbors(infect_node)
                for neighbor_node in neighbor_nodes:
                    if self.graph.nodes[neighbor_node]['state'] == NodeType.SUSCEPTIBLE:
                        edge = self.graph.get_edge_data(infect_node, neighbor_node)
                        if random.uniform(0, 1) < edge['weight']*s2e:
                            if neighbor_node not in tmp_infect_nodes:
                                tmp_infect_nodes.append(neighbor_node)
            for node in tmp_infect_nodes:
                self.graph.nodes[node]['state'] = NodeType.EXPOSED
                self.all_susceptible_nodes.remove(node)
                self.all_exposed_nodes.append(node)

            # 恢复1  exposed -> infect
            for exposed_node in self.all_exposed_nodes:
                if random.uniform(0, 1) < e2i:
                    self.graph.nodes[exposed_node]['state'] = NodeType.INFECT
                    self.all_exposed_nodes.remove(exposed_node)
                    self.all_infect_nodes.append(exposed_node)

            # 恢复2 infect -> recovered
            for infect_node in self.all_infect_nodes:
                if random.uniform(0, 1) < i2r:
                    self.graph.nodes[infect_node]['state'] = NodeType.RECOVERED
                    self.all_infect_nodes.remove(infect_node)
                    self.all_recovered_nodes.append(infect_node)

            # 计算节点数量
            self.susceptible_list.append(len(self.all_susceptible_nodes))
            self.exposed_list.append(len(self.all_exposed_nodes))
            self.infect_list.append(len(self.all_infect_nodes))
            self.recovered_list.append(len(self.all_recovered_nodes))
        print('------------SEIR END--------------')
        return self.susceptible_list, self.exposed_list, self.infect_list, self.recovered_list

    def seir_birth_death_model(self,  s2e=0.3, e2i=0.3, i2r=0.2, rate=10, birth_rate=ConstValue.birth_rate, death_rate=0.01):
        print('---------------SEIR BIRTH DEATH START-------------------')
        # 初始化易感染节点列表和数量
        for node in self.graph.nodes:
            if node != self.seed:
                self.all_susceptible_nodes.append(node)
        self.susceptible_list.append(len(self.all_susceptible_nodes) - self.birth_nodes)
        # 出生人口列表
        for i in range(self.birth_nodes):
            num = random.uniform(0, len(self.all_susceptible_nodes))
            node = self.all_susceptible_nodes[int(num)]
            self.all_susceptible_nodes.remove(node)
            self.all_birth_nodes.append(node)
            self.graph.nodes[node]['state'] = NodeType.BIRTH

        # 初始化感染节点列表和数量
        self.all_infect_nodes.append(self.seed)
        self.infect_list.append(len(self.all_infect_nodes))
        self.graph.nodes[self.seed]['state'] = NodeType.INFECT

        # 初始化潜伏状态   恢复状态  节点列表和数量
        self.recovered_list.append(len(self.all_recovered_nodes))
        self.exposed_list.append(len(self.all_exposed_nodes))

        # 出生数量和死亡数量
        self.birth_list.append(0)
        self.death_list.append(0)

        while True:
            if len(self.all_exposed_nodes) <= 0 and len(self.all_infect_nodes) <= 0:
                break
            # print('------------------------出生人口 和 死亡人口 --------------------------')
            birth_s = self.birth(self.all_susceptible_nodes, NodeType.SUSCEPTIBLE, birth_rate)
            birth_i = self.birth(self.all_infect_nodes, NodeType.INFECT, birth_rate)
            birth_r = self.birth(self.all_recovered_nodes, NodeType.RECOVERED, birth_rate)
            # print(' susceptible : %s ,' % birth_s + 'infect : %s ,' % birth_i + ' recovered : %s' % birth_r)
            self.death()
            self.birth_list.append(birth_s + birth_i + birth_r)
            self.death_list.append(len(self.all_death_nodes))
            # print('--------------------------------------------------------------------')

            tmp_infect_nodes = list()

            # 传染
            for infect_node in self.all_infect_nodes:
                neighbor_nodes = self.graph.neighbors(infect_node)
                for neighbor_node in neighbor_nodes:
                    if self.graph.nodes[neighbor_node]['state'] == NodeType.SUSCEPTIBLE:
                        edge = self.graph.get_edge_data(infect_node, neighbor_node)
                        if random.uniform(0, 1) < edge['weight'] * s2e:
                            if neighbor_node not in tmp_infect_nodes:
                                tmp_infect_nodes.append(neighbor_node)
            for node in tmp_infect_nodes:
                self.graph.nodes[node]['state'] = NodeType.EXPOSED
                self.all_susceptible_nodes.remove(node)
                self.all_exposed_nodes.append(node)

            # 恢复1  exposed -> infect
            for exposed_node in self.all_exposed_nodes:
                if random.uniform(0, 1) < e2i:
                    self.graph.nodes[exposed_node]['state'] = NodeType.INFECT
                    self.all_exposed_nodes.remove(exposed_node)
                    self.all_infect_nodes.append(exposed_node)

            # 恢复2 infect -> recovered
            for infect_node in self.all_infect_nodes:
                if random.uniform(0, 1) < i2r:
                    self.graph.nodes[infect_node]['state'] = NodeType.RECOVERED
                    self.all_infect_nodes.remove(infect_node)
                    self.all_recovered_nodes.append(infect_node)

            # 计算节点数量
            self.susceptible_list.append(len(self.all_susceptible_nodes))
            self.exposed_list.append(len(self.all_exposed_nodes))
            self.infect_list.append(len(self.all_infect_nodes))
            self.recovered_list.append(len(self.all_recovered_nodes))
        print('------------SEIR END--------------')
        return self.susceptible_list, self.exposed_list, self.infect_list, self.recovered_list, self.birth_list, self.death_list