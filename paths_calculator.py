from pickle import EMPTY_DICT
from ryu.base import app_manager
from ryu.base.app_manager import lookup_service_brick
from ryu.ofproto import ofproto_v1_3

import setting
import ast, csv, json, time


class PathsCalculator(app_manager.RyuApp):
    """
        A Ryu App for routing using Dijkstra algorithm.
    """

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(PathsCalculator, self).__init__(*args, **kwargs)
        self.name = "paths_calculator"
        self.count = 0
        self.paths = {}
        self.awareness = lookup_service_brick('awareness')
        self.monitor = lookup_service_brick('monitor')
        self.delay = lookup_service_brick('delay')
        self.weight_dict = {}
        self.write_paths = self.write_dijkstra_paths

    def write_dijkstra_paths(self):
        print("Writing paths")
        file = setting.PATHS
        time_file = setting.TIMES

        # DELAY
        self.weight_dict = self.delay.delay_dict

        # LOSS
        # for loss in self.monitor.link_loss:
        #     self.weight_dict[loss[0]][loss[1]] = self.monitor.link_loss[loss]
        # print(self.weight_dict)

        time_init = time.time()
        paths = {}
        for dp in self.awareness.switches:
            paths.setdefault(dp,{})
        for src in self.awareness.switches:
            for dst in self.awareness.switches:
                if src != dst:
                    paths[src][dst] = self.dijkstra(self.weight_dict, src, dst, visited=[], distances={}, predecessors={})

        with open(file,'w') as json_file:
            json.dump(paths, json_file, indent=2)
            # print(paths)

        total_time = time.time() - time_init
        with open(time_file,'a') as txt_file:
            txt_file.write(str(total_time)+'\n')
        self.calc_stretch()

    def dijkstra(self, graph, src, dest, visited=[], distances={}, predecessors={}):
        """
            calculates a shortest path tree routed in src
        """

        # a few sanity checks
        if src not in graph:
            raise TypeError('The root of the shortest path tree cannot be found')
        if dest not in graph:
            raise TypeError('The target of the shortest path cannot be found')
        # ending condition
        if src == dest:
            # We build the shortest path and display it
            path = []
            pred = dest
            while pred != None:
                path.append(pred)
                pred = predecessors.get(pred, None)

            return list(reversed(path))
        else:
            # if it is the initial  run, initializes the cost
            if not visited:
                distances[src] = 0
            # visit the neighbors
            for neighbor in graph[src]:
                if neighbor not in visited:
                    new_distance = distances[src] + graph[src][neighbor]
                    if new_distance < distances.get(neighbor, float('inf')):
                        distances[neighbor] = new_distance
                        predecessors[neighbor] = src
            # mark as visited

            visited.append(src)
            # now that all neighbors have been visited: recurse
            # select the non visited node with lowest distance 'x'
            # run Dijskstra with src='x'
            unvisited = {}
            for k in graph:
                if k not in visited:
                    unvisited[k] = distances.get(k, float('inf')) #sets the cost of link to the src neighbors with the actual value and inf for the non neighbors
            x = min(unvisited, key=unvisited.get) #find w not in N' such that D(w) is a minimum
            return self.dijkstra(graph, x, dest, visited, distances, predecessors)

    def get_paths_dijkstra(self):
        file_dijkstra = setting.PATHS
        with open(file_dijkstra,'r') as json_file:
            paths_dict = json.load(json_file)
            paths_dijkstra = ast.literal_eval(json.dumps(paths_dict))
            return paths_dijkstra

    def get_paths_base(self):
        file_base = setting.PATHS_BASE
        with open(file_base,'r') as json_file:
            paths_dict = json.load(json_file)
            paths_base = ast.literal_eval(json.dumps(paths_dict))
            return paths_base

    def get_path(self, src, dst):
        if self.paths:
            path = self.paths.get(src).get(dst)
            return path
        else:
            paths = self.get_paths_base()
            path = paths.get(src).get(dst)
            return path

    def stretch(self, paths, paths_base, src, dst):
        if paths and paths_base:
            add_stretch = len(paths.get(str(src)).get(str(dst))) - len(paths_base.get(str(src)).get(str(dst)))
            mul_stretch = len(paths.get(str(src)).get(str(dst))) / len(paths_base.get(str(src)).get(str(dst)))
            return add_stretch, mul_stretch

    def calc_stretch(self):
        paths_base = self.get_paths_base()
        paths_dijkstra = self.get_paths_dijkstra()
        # print(paths_dijkstra)
        a = time.time()
        sw = self.awareness.switches

        with open(setting.STRETCH_DIR +'stretch.csv','w') as csvfile:
            self.count += 1
            header = ['src','dst','add_st','mul_st']
            file = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
            file.writerow(header)
            for src in sw:
                for dst in sw:
                    if src != dst:
                        add_stretch, mul_stretch = self.stretch(paths_dijkstra, paths_base, src, dst)
                        # print(add_stretch)
                        # print(mul_stretch)
                        file.writerow([src, dst, add_stretch, mul_stretch])
        total_time = time.time() - a

