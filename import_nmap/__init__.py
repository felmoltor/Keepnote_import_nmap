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

        print "Hostname %s - %s" % (hnames[0][0],hnames[0][1])

        newhostnode = node.new_child(notebooklib.CONTENT_TYPE_DIR,("%s - %s") % (haddress,hnames[0][0]),index)
        newhostnode.set_attr("title",("%s - %s") % (haddress,hnames[0][0]))
        
        # Create a page with status reason of the host and other information
        statusnode = newhostnode.new_child(notebooklib.CONTENT_TYPE_PAGE,"Status Info",None)
        statusout = safefile.open(statusnode.get_data_file(),"w",codec="utf-8")
        statusout.write(u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><body>""")
        statusout.write("<b>Status:</b> %s<br/>" % hstatus)
        statusout.write("<b>Status Reason:</b> %s<br/>" % hstatusreason)
        statusout.write("<b>Status Reason TTL:</b> %s<br/>" % hstatusreasonttl)
        statusout.write("</body></html>")
        statusout.close()
        
        # Create a page with multiple hostnames of this host
        hostnamenode = newhostnode.new_child(notebooklib.CONTENT_TYPE_PAGE,"Hostnames",None)
        hostnameout = safefile.open(hostnamenode.get_data_file(),"w",codec="utf-8")
        statusout.write(u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><body>""")
        for hnametype in hnames:
            hostnameout.write(("<b>Hostname:</b> %s. <b>Type:</b> %s") % (hnametype[0],hnametype[1]))
        hostnameout.write("</body></html>")
        hostnameout.close()

        for port in hostnode.getElementsByTagName("ports")[0].getElementsByTagName("port"):
            pnumber = port.getAttribute("portid")
            pprotocol = port.getAttribute("protocol")
            pstate = port.getElementsByTagName("state")[0].getAttribute("state")
            pstateresason = port.getElementsByTagName("state")[0].getAttribute("reason")
            # Create the page node
            newportchild = newhostnode.new_child(notebooklib.CONTENT_TYPE_PAGE,("%s/%s - %s") % (pnumber,pprotocol,pstate))
            newportchild.set_attr("title",("%s/%s - %s") % (pnumber,pprotocol,pstate))


    task.finish()

"""
    child = node.new_child(notebooklib.CONTENT_TYPE_PAGE, 
                           os.path.basename(filename), index)
    child.set_attr("title", os.path.basename(filename)) # remove for 0.6.4

    lines = open(filename).readlines()


    out = safefile.open(child.get_data_file(), "w", codec="utf-8")
    out.write("<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"><body>")

    lines = [escape_whitespace(escape(line)) for line in lines]
    text = "".join(lines)

    # replace newlines
    text = text.replace(u"\n", u"<br/>")
    text = text.replace(u"\r", u"")

    out.write(text)
    out.write(u"</body></html>")

    out.close()
"""
                     

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
