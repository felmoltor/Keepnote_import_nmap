Keepnote_import_nmap
====================

Plugin for keepnote to import a XML nmap file.
This plugin is usefull to keep track of the intrusion test you have done on every port of the alive host in a perimeter scan.

**Instructions**

  1. Open your keepnote.
  2. Navigate to "Edit -> Preferences -> Extensiones"
  3. Click on "Install new extension" and open the file import_nmap.kne.
  4. Once it is installed correctly you can navigate to "File -> Import Notebook -> Import Nmap XML" and select your XML file.

As a result you'll have a beautifull colored tree with a folder for each IP with a hanging folder for port information.

_IP_:
  - Color Red: Is Down
  - Color Green: Is Up

_Ports_:
  - Color Red: Closed
  - Color Orange: Filtered
  - Color Green Is open

**Bugs**

Send any bug to https://twitter.com/felmoltor.
