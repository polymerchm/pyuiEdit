**pyuiEdit** - a tool for re-organizing pyui heirarchies

pyuiEdit will present a schematic view of the pyui file. Its primary purpose is to group views at the same "level" into a new view as its subviews.  All subviews of the selcted view maintain their hierarchical relationships with their own descendents.   pyuiEdit is only "sized" to operate on iPads.

When started, a file selection pop-up is presented, the upper half of which is a directory selector and the lower half is a file selector.  Only file types of "pyui" and "json" are presented.

Once selected, the ui is presented schematically in the view in the upper right corner of the screen and a list of its views as a ListView in the right side.  The color and indentation level indicate the subview
hierarchies.  

Views can be selected/deselected by either touching them on the schematic or the list.  All can be deselected using the **Deselect All** button in the array at the lower right.  Selected subviews can be hidden by hitting the **Hide Selected** button.  Similarly, all can be unhidden using the **Unhide All** button.  Subviews (and all descendents) of the any selected view can themesleved selected with the **Selected Children** button.

Once the desired views are selected, they (and their descendents) can be "deposited" into a new view by hitting the **Collect** button.  Any hidden views are not "containerized".  All frame values are adjusted accordingly in the subviews to maintain the same physical location on the root view and all "hierarchies are appropriately adjusted.  A dialog is displayed to name the view, a Custom Class, and "margins" to the new view.

The **Undo** button restores the ui to its prior state.

The **Flex Edit** button allows the flex attribute of the view to be changed. In this window the **Save** button changes this, but only in the in-memory copy, not the source pyui.  The **Quit** button, leaves the Flex Editor without making any changes.  

The current state of the ui can be saved as a pyui or json file by hitting the **Save** button.  A dialog presents the file directory of the original source file.  If the extension is not provided, it defaults to ".pyui".  Extensions of than 'pyui or json' are not permitted.  The resultant file is "pretty-printed" so that it is readable when edited as a text file (say using **shellista** or **stash**'s `edit -t` command)

Some goodies for general use are the *ui_draw_arrow*, *Shield* and *uidir* routines.  *NodeListWalker* was separated for debugging purposes only.  


To Do:

-Zoom view interface
-Marquee select