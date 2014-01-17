"""

    Author: Felipe Molina de la Torre
    Date: November 2013
    Summary: Import a tree from nmap output XML files

"""

#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.
#

# python imports
# import codecs
import gettext
import mimetypes
import os
import sys
# import re
# from xml.sax.saxutils import escape
from xml.dom import minidom

_ = gettext.gettext


# pygtk imports
import pygtk
pygtk.require('2.0')
from gtk import gdk
import gtk.glade
import gobject

# keepnote imports
import keepnote
from keepnote import unicode_gtk
from keepnote.notebook import NoteBookError, get_valid_unique_filename,\
    CONTENT_TYPE_DIR, attach_file
from keepnote import notebook as notebooklib
from keepnote import tasklib, safefile
from keepnote.gui import extension, FileChooserDialog

# pygtk imports
try:
    import pygtk
    pygtk.require('2.0')
    from gtk import gdk
    import gtk.glade
    import gobject
except ImportError:
    # do not fail on gtk import error,
    # extension should be usable for non-graphical uses
    pass



class Extension (extension.Extension):

    def __init__(self, app):
        """Initialize extension"""
        
        extension.Extension.__init__(self, app)
        self.app = app


    def get_depends(self):
        return [("keepnote", ">=", (0, 7, 1))]


    def on_add_ui(self, window):
        """Initialize extension for a particular window"""
        
        # add menu options
        self.add_action(
            window, "Import Nmap XML", _("Import Nmap XML"),
            lambda w: self.on_import_nmap(
                window, window.get_notebook()),
            tooltip=_("Import a tree of folder extracted from a nmap scan result file"))
        
        # TODO: Fix up the ordering on the affected menus.
        self.add_ui(window,
            """
            <ui>
            <menubar name="main_menu_bar">
               <menu action="File">
                 <menu action="Import">
                     <menuitem action="Import Nmap XML"/>
                 </menu>
               </menu>
            </menubar>
            </ui>
            """)

    def on_import_nmap(self, window, notebook):
        """Callback from gui for importing a plain text file"""
        
        # Ask the window for the currently selected nodes
        nodes = window.get_selected_nodes()
        if len(nodes) == 0:
            return
        node = nodes[0]

        dialog = FileChooserDialog(
            "Import Nmap XML", window, 
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=("Cancel", gtk.RESPONSE_CANCEL,
                     "Import", gtk.RESPONSE_OK))
        dialog.set_select_multiple(True)
        response = dialog.run()

        if response == gtk.RESPONSE_OK and dialog.get_filenames():
            filenames = map(unicode_gtk, dialog.get_filenames())
            dialog.destroy()

            self.import_nmap_xml(node, filenames, window=window)
        else:
            dialog.destroy()


    def import_nmap_xml(self, node, filenames, window=None):
        try:
            for filename in filenames:
                import_nmap(node, filename, task=None)

            if window:
                window.set_status("Nmap XML files imported.")
            return True
    
        except NoteBookError:
            if window:
                window.set_status("")
                window.error("Error while importing nmap files.", 
                             e, sys.exc_info()[2])
            else:
                self.app.error("Error while importing nmap files.", 
                               e, sys.exc_info()[2])
            return False

        except Exception, e:
            if window:
                window.set_status("")
                window.error("unknown error", e, sys.exc_info()[2])
            else:
                self.app.error("unknown error", e, sys.exc_info()[2])
            return False

def get_os_icon(hos):
    hlos = hos.lower()
    mypath = os.path.dirname(os.path.abspath(__file__))
    
    # NOTE: For now, not using re as this produces a slower import
    if (hlos.find("freebsd") >= 0): #.search('.*freebsd.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/freebsd.png" % mypath
    elif (hlos.find("windows") >= 0 and hlos.find("xp") >= 0): #(re.search('.*windows\s+xp.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/winxp.png" % mypath
    elif (hlos.find("windows") >= 0 and hlos.find("nt") >= 0): # (re.search('.*windows\s+nt.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/winxp.png" % mypath
    elif (hlos.find("windows") >= 0 and hlos.find("vista") >= 0): # (re.search('.*windows\s+vista.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/win7.png" % mypath
    elif (hlos.find("windows") >= 0 and hlos.find("7") >= 0): # (re.search('.*windows\s+7.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/win7.png" % mypath
    elif (hlos.find("mac") >= 0 and hlos.find("os") >= 0): # (re.search('.*mac\s+os.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/mac.png" % mypath
    elif (hlos.find("solaris") >= 0): # (re.search('.*solaris.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/solaris.png" % mypath
    elif (hlos.find("linux") >= 0): # (re.search('.*linux.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/linux.png" % mypath
    elif (hlos.find("qemu") >= 0): # (re.search('.*qemu.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/qemu.png" % mypath
    elif (hlos.find("blue coat") >= 0): # (re.search('.*qemu.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/bluecoat.png" % mypath
    elif (hlos.find("juniper") >= 0): # (re.search('.*qemu.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/juniper.png" % mypath
    elif (hlos.find("f5") >= 0): # (re.search('.*qemu.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/f5.png" % mypath
    elif (hlos.find("cisco") >= 0): # (re.search('.*qemu.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/cisco.png" % mypath
    elif (hlos.find("windows") >= 0): # (re.search('.*qemu.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/winxp.png" % mypath
    elif (hlos.find("HP-UX") >= 0): # (re.search('.*qemu.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/hp.png" % mypath
    elif (hlos.find("SonicWALL") >= 0): # (re.search('.*qemu.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/sonicwall.png" % mypath
    else:
        return None    


def import_nmap(node, filename, index=None, task=None):
    """
    Import a nmap XML single file into the notebook

    node     -- node to attach folder to
    filename -- filename of text file to import
    task     -- Task object to track progress
    """

    # TODO: handle spaces correctly

    if task is None:
        # create dummy task if needed
        task = tasklib.Task()

    nmapxml = minidom.parse(filename)
    
    # Searching for up and down numbers
    nhostup=nmapxml.getElementsByTagName("hosts")[0].getAttribute("up")
    nhostdown=nmapxml.getElementsByTagName("hosts")[0].getAttribute("down")
    scanstats = "(%s up, %s down)" % (nhostup,nhostdown)
    originaltitle = node.get_attr("title")
    node.set_attr("title", "%s %s" % (originaltitle,scanstats))
    
    # Create a Up and Down folder
    uphostsfolder = node.new_child(notebooklib.CONTENT_TYPE_DIR,("Up"),index)
    uphostsfolder.set_attr("title", ("Up (%s)" % nhostup))
    # Create a Up and Down folder
    downhostsfolder = node.new_child(notebooklib.CONTENT_TYPE_DIR,("Down"),index)
    downhostsfolder.set_attr("title", ("Down (%s)" % nhostdown))
    
    noportsopenfolder = uphostsfolder.new_child(notebooklib.CONTENT_TYPE_DIR,("No Ports Open"),index)
    noportsopenfolder.set_attr("title",("No Ports Open"))
    withportsopenfolder = uphostsfolder.new_child(notebooklib.CONTENT_TYPE_DIR,("With Ports Open"),index)
    withportsopenfolder.set_attr("title","With Ports Open")
    
    for hostnode in nmapxml.getElementsByTagName("host"):
        
        hstatus = "Unknown"
        hstatusreason = "Unknown"
        hstatusreasonttl = "Unknown"
        haddress = "Unknown"
        hosfirstmatch = None
        newhostnode = None
        icon = None
        detectedos = []
        
        if len(hostnode.getElementsByTagName("status")) > 0:
            hstatusnode = hostnode.getElementsByTagName("status")[0]
            hstatus = hstatusnode.getAttribute("state")
            hstatusreason =  hstatusnode.getAttribute("reason")
            hstatusreasonttl =  hstatusnode.getAttribute("reason_ttl")
        
        if (len(hostnode.getElementsByTagName("address")) > 0):
            haddress = hostnode.getElementsByTagName("address")[0].getAttribute("addr")
        
        if len(hostnode.getElementsByTagName("os")) > 0:
            oscount = 0
            for osmatch in hostnode.getElementsByTagName("os")[0].getElementsByTagName("osmatch"):
                osname = osmatch.getAttribute("name")
                osaccuracy = osmatch.getAttribute("accuracy")
                osfamily = osmatch.getElementsByTagName("osclass")[0].getAttribute("family")
                osvendor = osmatch.getElementsByTagName("osclass")[0].getAttribute("vendor")
                ostype = osmatch.getElementsByTagName("osclass")[0].getAttribute("type")
                detectedos.append([osname,osaccuracy,ostype,osvendor,osfamily])
                if oscount == 0:
                    hosfirstmatch = osname
                    icon = get_os_icon(hosfirstmatch)
                oscount += 1
            
            # If no OS was identified by nmap
            if oscount == 0:
                mypath = os.path.dirname(os.path.abspath(__file__))
                icon = "%s/icons/question.png" % mypath
        
        # Create the folder with the first IP obtained and the fist hostname
        hnames = []
        if len(hostnode.getElementsByTagName("hostnames")) > 0:
            for hostname in hostnode.getElementsByTagName("hostnames")[0].getElementsByTagName("hostname"):
                hnames.append([hostname.getAttribute("name"),hostname.getAttribute("type")]) 
            
        if len(hnames)==0:
            mainhostname = haddress
        else:
            if hnames[0][0] is not None:
                mainhostname = hnames[0][0]
            else:
                mainhostname = haddress
        
        # New host node hanging from "Up" or "Down" folder
        if (hstatus == "up"):
            if len(hostnode.getElementsByTagName("ports")) > 0:
                newhostnode = withportsopenfolder.new_child(notebooklib.CONTENT_TYPE_DIR,("%s - %s") % (haddress,mainhostname),index)
            else:
                newhostnode = noportsopenfolder.new_child(notebooklib.CONTENT_TYPE_DIR,("%s - %s") % (haddress,mainhostname),index)
        else:
            newhostnode = downhostsfolder.new_child(notebooklib.CONTENT_TYPE_DIR,("%s - %s") % (haddress,mainhostname),index)
        newhostnode.set_attr("title",("%s - %s") % (haddress,mainhostname))
        
        # Create a page with status reason of the host and other information
        statusnode = newhostnode.new_child(notebooklib.CONTENT_TYPE_PAGE,"Status Information",None)
        statusout = safefile.open(statusnode.get_data_file(),"w",codec="utf-8")
        statusout.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><body>""")
        statusout.write("<b>Status:</b> %s<br/>" % hstatus)
        statusout.write("<b>Status Reason:</b> %s<br/>" % hstatusreason)
        statusout.write("<b>Status Reason TTL:</b> %s<br/>" % hstatusreasonttl)
        statusout.write("</body></html>")
        statusout.close()
        
        
        if len(hostnode.getElementsByTagName("os")) > 0:
            osinfonode = newhostnode.new_child(notebooklib.CONTENT_TYPE_PAGE,"OS Information",None)
            osinfonode = safefile.open(osinfonode.get_data_file(),"w",codec="utf-8")
            osinfonode.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><body>""")
            
            if icon is not None:
                osinfonode.write("<br/>")
                osinfonode.write("<img src=\"%s\"/><br/>" % icon)                
                
            for detected_os in detectedos:
                osinfonode.write("-----------------------------------<br/>")
                osinfonode.write("<b>OS Name:</b> %s<br/>" % detected_os[0])
                osinfonode.write("<b>OS Accuracy:</b> %s<br/>" % detected_os[1])
                osinfonode.write("<b>OS Type:</b> %s<br/>" % detected_os[2])
                osinfonode.write("<b>OS Vendor:</b> %s<br/>" % detected_os[3])
                osinfonode.write("<b>OS Family:</b> %s<br/>" % detected_os[4])
                osinfonode.write("-----------------------------------<br/>")
            
            osinfonode.write("</body></html>")
            osinfonode.close()
        
        # Icon selection
        if icon is not None:
            print "Setting the icon for host %s to %s" % (haddress,icon)
            newhostnode.set_attr("icon",icon)
        else:
            # Change the color of the Host depending on the state (Up: Green, Dow: Red)
            if hstatus == "up":
                # Green
                newhostnode.set_attr("icon","folder-green.png")
            else:
                # Red
                newhostnode.set_attr("icon","folder-red.png")
                
        # Change the color of the Host depending on the state (Up: Green, Dow: Red)
        if hstatus == "up":
            # Green
            newhostnode.set_attr("title_fgcolor","#00AA00")
        else:
            # Red
            newhostnode.set_attr("title_fgcolor","#AA0000")
            
        # Create a page with multiple hostnames of this host
        if len(hnames) > 0:
            hostnamenode = newhostnode.new_child(notebooklib.CONTENT_TYPE_PAGE,"Hostnames",None)
            hostnameout = safefile.open(hostnamenode.get_data_file(),"w",codec="utf-8")
            hostnameout.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><body>""")
            for hnametype in hnames:
                hostnameout.write(("<b>Hostname:</b> %s. <b>Type:</b> %s<br/>") % (hnametype[0],hnametype[1]))
            hostnameout.write("</body></html>")
            hostnameout.close()
            
        # If this host has any port information
        if len(hostnode.getElementsByTagName("ports")) > 0:
            n_udpopen = 0
            n_udpclosed = 0
            n_udpfiltered = 0
            n_tcpopen = 0
            n_tcpclosed = 0
            n_tcpfiltered = 0
            # Create a folder for TCP Ports
            tcpportfolder = newhostnode.new_child(notebooklib.CONTENT_TYPE_DIR,("TCP"),index)
            tcpportfolder.set_attr("title", ("TCP"))
            
            # Create a folder for UDP Ports
            udpportfolder = newhostnode.new_child(notebooklib.CONTENT_TYPE_DIR,("UDP"),index)
            udpportfolder.set_attr("title", ("UDP"))
            
            for port in hostnode.getElementsByTagName("ports")[0].getElementsByTagName("port"):
                
                pstate = "Unknown"
                pstatereason = "Unknown"
                pservicename = "Unknown"
                pserviceproduct = "Unknown"
                pserviceversion = "Unknown"
                pserviceostype = "Unknown"
                    
                pnumber = port.getAttribute("portid")
                pprotocol = port.getAttribute("protocol")
                
                if len(port.getElementsByTagName("state")) > 0:
                    statenode = port.getElementsByTagName("state")[0]
                    pstate = statenode.getAttribute("state")
                    pstatereason = statenode.getAttribute("reason")
                    
                if len(port.getElementsByTagName("service")) > 0:
                    servicenode = port.getElementsByTagName("service")[0]
                    pservicename = servicenode.getAttribute("name")
                    pserviceproduct = servicenode.getAttribute("product")
                    pserviceversion = servicenode.getAttribute("version")
                    pserviceostype = servicenode.getAttribute("ostype")
                
                newportchild = None
                if pprotocol.upper() == "TCP":
                    # Create the page node fot TCP
                    newportchild = tcpportfolder.new_child(notebooklib.CONTENT_TYPE_PAGE,("%s_%s - %s [%s]") % (pnumber,pprotocol,pservicename,pstate))
                    newportchild.set_attr("title",("%s_%s - %s [%s]") % (pnumber,pprotocol,pservicename,pstate))
                    # Save port status stats
                    if (pstate.upper() == "OPEN"):
                        n_tcpopen += 1
                    elif (pstate.upper() == "CLOSED"):
                        n_tcpclosed += 1
                    else:    
                        n_tcpfiltered += 1                    
                else:
                    # Create the page node fot UDP
                    newportchild = udpportfolder.new_child(notebooklib.CONTENT_TYPE_PAGE,("%s_%s - %s [%s]") % (pnumber,pprotocol,pservicename,pstate))
                    newportchild.set_attr("title",("%s_%s - %s [%s]") % (pnumber,pprotocol,pservicename,pstate))
                    # Save port status stats
                    if (pstate.upper() == "OPEN"):
                        n_udpopen += 1
                    elif (pstate.upper() == "CLOSED"):
                        n_udpclosed += 1
                    else:
                        n_udpfiltered += 1
                    
                portout = safefile.open(newportchild.get_data_file(),"w",codec="utf-8")
                portout.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><body>""")
                portout.write(("<b>Port Number:</b> %s. <b>Protocol:</b> %s. <b>State:</b> %s. <b>State Reason:</b> %s<br/>") % (pnumber,pprotocol,pstate,pstatereason))
                portout.write(("<b>Service:</b> %s. <b>Product:</b> %s. <b>version:</b> %s. <b>OS Type:</b> %s<br/>") % (pservicename,pserviceproduct,pserviceversion,pserviceostype))
                portout.write("</body></html>")
                portout.close()
                
                # Change the color of the note depending on the state (Open: Green, Closed: Red, Filtered: Orange)
                if pstate == "open":
                    # Green
                    newportchild.set_attr("icon","note-green.png")
                    newportchild.set_attr("title_fgcolor","#00AA00")
                elif pstate == "filtered" or pstate == "open|filtered":
                    # Orange
                    newportchild.set_attr("icon","note-orange.png")
                    newportchild.set_attr("title_fgcolor","#ffa300")
                else:
                    # Red
                    newportchild.set_attr("icon","note-red.png")
                    newportchild.set_attr("title_fgcolor","#AA0000")

            # Update Ports UPD/TCP Stats in the title
            # For TCP
            portstats = "" 
            if (n_tcpopen>0):
                portstats += "%s open" % n_tcpopen
            if (n_tcpclosed>0):
                if (len(portstats)>0):
                    portstats += ","
                portstats += "%s closed" % n_tcpclosed
            if (n_tcpfiltered>0):
                if (len(portstats)>0):
                    portstats += ","
                portstats += "%s filtered" % n_tcpfiltered
            if (len(portstats)>0):
                tcpportfolder.set_attr("title","TCP (%s)" % portstats)
            # For UDP
            portstats = "" 
            if (n_udpopen>0):
                portstats += "%s open" % n_udpopen
            if (n_udpclosed>0):
                if (len(portstats)>0):
                    portstats += ","
                portstats += "%s closed" % n_udpclosed
            if (n_udpfiltered>0):
                if (len(portstats)>0):
                    portstats += ","
                portstats += "%s filtered" % n_udpfiltered
            if (len(portstats)>0):
                udpportfolder.set_attr("title","UDP (%s)" % portstats)
        
                
    task.finish()
                     

def escape_whitespace(line):
    """Escape white space for an HTML line"""

    line2 = []
    it = iter(line)

    # replace leading spaces
    for c in it:
        if c == " ":
            line2.append("&nbsp;")
        else:
            line2.append(c)
            break

    # replace multi-spaces
    for c in it:
        if c == " ":
            line2.append(" ")
            for c in it:
                if c == " ":
                    line2.append("&nbsp;")
                else:
                    line2.append(c)
                    break
        else:
            line2.append(c)

    return "".join(line2)
    


if __name__ == "__main__":
    print "Use this as an extension for Keepnote, this is not a command line program..."
    exit(1)
