Keepnote_import_nmap
====================

Plugin for keepnote to import a XML nmap file.
This plugin is usefull to keep track of the intrusion test you have done on every port of the alive host in a perimeter scan.

**Output Example**

![My image](http://i.imgur.com/Uamu6Iv.png?1)

**Instructions**

  1. Open your keepnote.
  2. Navigate to "Edit -> Preferences -> Extensions"
  3. Click on "Install new extension" and open the file import_nmap.kne.
  4. Once it is installed correctly:
    - Create a new notebook and select this new notebook before importing the XML.
    - Now, navigate to "File -> Import Notebook -> Import Nmap XML" and select your XML file


As a result you'll have a beautifull colored tree with a folder for each IP with a hanging folder for port information.

_IP_:
  - Color Red: Is Down
  - Color Green: Is Up

_Ports_:
  - Color Red: Closed
  - Color Orange: Filtered
  - Color Green Is open

**Troubleshoots**
-
If you uninstall and install this plugin more than one time, you'll probably have problems installing it again.
This is because Keepnote does not delete the previous kne file of the plugin when you uninstall a plugin.

You have to manually delete the plugin file "import_nmap.kne" from your plugin folder usually located in "~/.config/keepnote/extensions".
Then you will be able to install the plugin again.

**Bugs**

Send any bug to https://twitter.com/felmoltor

**TODO**

- Import multiple XML files at the same time
- Notify the user if he has not selected a keepnote or a node where to import the file.
