# traffic_generator_xterm_iperf
Serve a generare traffico usando xterm su gli host e poi iperf

Vi spiego come funziona

1. Eseugo su un terminale

>sudo ptyhon3 geant_topology.py

Serve per generare il file json host_IP.json dove sono contenuti i nomi degli host e gli indirizzi IP associati
ed avvia mininet sul quel terminale


2. Su un altro terminale

>python3 traffic_matrix.py

Utilizza il file host_IP.json e la matrice di traffico per creare il file CLI_xterm_iperf.txt che verrà poi utilizzato in mininet

3. Una volta creato il file possiamo eseguiere il controller

>sudo ryu-manager ryu.app.simple_switch_stp_13

Aspettiamo un po che gli switch imparino le regole dopo di che

4. All'interno del CLI di Mininet eseguo il comando

mininet> source CLI_xterm_iperf.txt

Questo farà partire le coppie (mutuamente esclusive) di Client e Server che si scambiano dati
Tali Coppie sono state stabilite in traffic_matrix.py
(Se le prima volta i client si chiudo da soli, aspettare un pò e riprovare...vuol dire che gli switch non hanno ancora imparato le regole)
