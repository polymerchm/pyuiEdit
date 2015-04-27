# coding: utf-8

import ui
import os
import console


class MyTableViewDataSource (object):
    
    def __init__(self,base_dir = '.'):
        self.dir = base_dir
        _, folders, files = next(os.walk(base_dir))
        folders.insert(0,'..')
        self.data = (folders,files)
        
    def tableview_number_of_sections(self, tableview):
        return 2

    def tableview_number_of_rows(self, tableview, section):
        return len(self.data[section])

    def tableview_cell_for_row(self, tableview, section, row):

        cell = ui.TableViewCell()
        cell.accessory_type = ('disclosure_indicator', 'detail_button')[section]
        cell.text_label.text = self.data[section][row]
        if section==0:
            cell.background_color='#eeffee'
        return cell

    def tableview_title_for_header(self, tableview, section):
        return ('Folders','Files')[section]

    def tableview_did_select(self, tableview, section, row):
        if section == 0:
            dir = os.path.join(self.dir, self.data[section][row])
            if os.path.exists(dir):
                self.dir=dir
            newv = FileViewer(self.dir)
            nav = tableview.superview.navigation_view
            nav.push_view(newv)
        else:
            FileGetter.fileName = os.path.join(self.dir, self.data[section][row])
            tableview.superview.navigation_view.close()
            
    def tableview_accessory_button_tapped(self, tableview, section, row):
        full = os.path.join(self.dir,self.data[section][row])
        stats =  os.stat(full)
        console.hud_alert('Size: {0} KB'.format(stats.st_size//1024))


class FileViewer(ui.View):
    def __init__(self,base_dir = '.', *args, **kargs):
        self.table = ui.TableView(*args, **kargs)
        self.table.name = 'FileTable'
        self.src = MyTableViewDataSource(base_dir)
        self.table.data_source = self.src
        self.table.delegate = self.src
        self.table.flex = 'WHTBLR'
        self.background_color = 'white'
        self.add_subview(self.table)

    @property
    def selection(self):
        return FileGetter.fileName
	 
class FileGetter():
	fileName = ''
	def __init__(self,base_dir='.'):
		self.base_dir = base_dir
		self.fv = FileViewer(self.base_dir)
			
	def getFile(self):
		fileName = ''
		self.fv.height=700
		nv = ui.NavigationView(self.fv)
		nv.height=800
		nv.navigation_bar_hidden = True
		nv.name = 'File Selector'
		nv.present('popover')
		#ui.in_background(nv.wait_modal)
		nv.wait_modal()
		
	@property
	def selection(self):
		return FileGetter.fileName

if __name__ == '__main__':
	fg = FileGetter()
	fg.getFile()
	print fg.selection
	
	
	
