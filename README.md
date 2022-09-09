# Guida all'avvio dell'applicativo routing SDN <br>
#1) Avviare mininet tramite file python, file geant_topology.py preso dalla [repo](https://github.com/gabrispa/controllerML/tree/main/TrafficGenerator) <br>
#2) Avviare RYU controller su un altro terminale comando "sudo ryu-manager —observe-links topology_discover.py flow_installation.py monitor.py delay.py" <br>
#3) Aspettare la convergenza della rete e il riempimento del file net_info.csv che si trova nella cartella principale <br>
#4) Avviare RL_threading.py (lui comincia a stampare ok) <br>
#5) I percorsi saranno disponibili (dopo il primo ok) nel file paths.json dentro la cartella RoutingGeant <br>

#Nota: host 24 e 10 sono connessi allo stesso switch e inviano a due host diversi (vedi traffic_matrix) senza alcun problema. <br>

# SDN routing application startup guide <br>
# 1) Start mininet with python file, geant_topology.py file taken from [repo] (https://github.com/gabrispa/controllerML/tree/main/TrafficGenerator) <br>
# 2) Run the RYU controller on another terminal "sudo ryu-manager —observe-links topology_discover.py flow_installation.py monitor.py delay.py" <br>
# 3) Wait for the network and for the net_info.csv file located in the main folder <br>
# 4) Run RL_threading.py (he will start printing ok) <br>
# 5) The paths will be available (after the first ok) in the paths.json file that is located in the RoutingGeant folder <br>

#Note: hosts 24 and 10 are connected to the same switch and send to two different hosts (see traffic_matrix) without any problem.
