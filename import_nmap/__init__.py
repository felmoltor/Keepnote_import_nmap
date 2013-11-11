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
import codecs
import gettext
import mimetypes
import os
import sys
import re
from xml.sax.saxutils import escape
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

    for hostnode in nmapxml.getElementsByTagName("host"):
        hstartime = hostnode.getAttribute("starttime")
        hendtime = hostnode.getAttribute("endtime")
        hstatus = hostnode.getElementsByTagName("status")[0].getAttribute("state")
        hstatusreason =  hostnode.getElementsByTagName("status")[0].getAttribute("reason")
        hstatusreasonttl =  hostnode.getElementsByTagName("status")[0].getAttribute("reason_ttl")
        haddress = hostnode.getElementsByTagName("address")[0].getAttribute("addr")
        # Create the folder with the first IP obtained and the fist hostname
        hnames = []
        for hostname in hostnode.getElementsByTagName("hostnames")[0].getElementsByTagName("hostname"):
            hnames.append([hostname.getAttribute("name"),hostname.getAttribute("type")]) 
        
        if len(hnames)==0:
            mainhostname = haddress
        else:
            if hnames[0][0] is not None:
                mainhostname = hnames[0][0]
            else:
                mainhostname = haddress
        
        newhostnode = node.new_child(notebooklib.CONTENT_TYPE_DIR,("%s - %s") % (haddress,mainhostname),index)
        newhostnode.set_attr("title",("%s - %s") % (haddress,mainhostname))
        
        # Create a page with status reason of the host and other information
        statusnode = newhostnode.new_child(notebooklib.CONTENT_TYPE_PAGE,"Status Info",None)
        statusout = safefile.open(statusnode.get_data_file(),"w",codec="utf-8")
        statusout.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><body>""")
        statusout.write("<b>Status:</b> %s<br/>" % hstatus)
        statusout.write("<b>Status Reason:</b> %s<br/>" % hstatusreason)
        statusout.write("<b>Status Reason TTL:</b> %s<br/>" % hstatusreasonttl)
        statusout.write("</body></html>")
        statusout.close()
        
        # Change the color of the Host depending on the state (Up: Green, Dow: Red)
        if hstatus == "up":
            # Green
            newhostnode.set_attr("icon","folder-green.png")
            newhostnode.set_attr("title_fgcolor","#00AA00")
        else:
            # Red
            newhostnode.set_attr("icon","folder-red.png")
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
            
        # Create a folder for the ports information
        newportfoldernode = newhostnode.new_child(notebooklib.CONTENT_TYPE_DIR,("Ports"),index)
        newportfoldernode.set_attr("title", ("Ports"))
        
        for port in hostnode.getElementsByTagName("ports")[0].getElementsByTagName("port"):
            pnumber = port.getAttribute("portid")
            pprotocol = port.getAttribute("protocol")
            pstate = port.getElementsByTagName("state")[0].getAttribute("state")
            pstatereason = port.getElementsByTagName("state")[0].getAttribute("reason")
            pservicename = port.getElementsByTagName("service")[0].getAttribute("name")
            pserviceproduct = port.getElementsByTagName("service")[0].getAttribute("product")
            pserviceversion = port.getElementsByTagName("service")[0].getAttribute("version")
            pserviceostype = port.getElementsByTagName("service")[0].getAttribute("ostype")
            # Create the page node
            newportchild = newportfoldernode.new_child(notebooklib.CONTENT_TYPE_PAGE,("%s_%s - %s [%s]") % (pnumber,pprotocol,pservicename,pstate))
            newportchild.set_attr("title",("%s/%s - %s [%s]") % (pnumber,pprotocol,pservicename,pstate))
            
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
            elif pstate == "filtered":
                # Orange
                newportchild.set_attr("icon","note-orange.png")
                newportchild.set_attr("title_fgcolor","#ffa300")
            else:
                # Red
                newportchild.set_attr("icon","note-red.png")
                newportchild.set_attr("title_fgcolor","#AA0000")


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
