<?xml version="1.0"?>
<?xml-stylesheet href="file:///usr/bin/../share/nmap/nmap.xsl" type="text/xsl"?>
<!-- Nmap 6.25 scan initiated Sun Nov 10 20:13:47 2013 as: nmap -sS -oX bing.com -F bing.com -->
<nmaprun scanner="nmap" args="nmap -sS -oX bing.com -F bing.com" start="1384110827" startstr="Sun Nov 10 20:13:47 2013" version="6.25" xmloutputversion="1.04">
<scaninfo type="syn" protocol="tcp" numservices="100" services="7,9,13,21-23,25-26,37,53,79-81,88,106,110-111,113,119,135,139,143-144,179,199,389,427,443-445,465,513-515,543-544,548,554,587,631,646,873,990,993,995,1025-1029,1110,1433,1720,1723,1755,1900,2000-2001,2049,2121,2717,3000,3128,3306,3389,3986,4899,5000,5009,5051,5060,5101,5190,5357,5432,5631,5666,5800,5900,6000-6001,6646,7070,8000,8008-8009,8080-8081,8443,8888,9100,9999-10000,32768,49152-49157"/>
<verbose level="0"/>
<debugging level="0"/>
<host starttime="1384110827" endtime="1384110830"><status state="up" reason="reset" reason_ttl="255"/>
<address addr="204.79.197.200" addrtype="ipv4"/>
<hostnames>
<hostname name="bing.com" type="user"/>
<hostname name="any.edge.bing.com" type="PTR"/>
</hostnames>
<ports><extraports state="filtered" count="98">
<extrareasons reason="no-responses" count="98"/>
</extraports>
<port protocol="tcp" portid="80"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="http" method="table" conf="3"/></port>
<port protocol="tcp" portid="443"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="https" method="table" conf="3"/></port>
</ports>
<times srtt="22012" rttvar="38869" to="177488"/>
</host>
<runstats><finished time="1384110830" timestr="Sun Nov 10 20:13:50 2013" elapsed="3.32" summary="Nmap done at Sun Nov 10 20:13:50 2013; 1 IP address (1 host up) scanned in 3.32 seconds" exit="success"/><hosts up="1" down="0" total="1"/>
</runstats>
</nmaprun>
