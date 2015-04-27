# coding: utf-8

'''
allow for text editing to encapsulate specific views from a pyui as subviews of a "container" view

The strucure of a "node" is a dictionary with the four keys:
	
{ "attributes": {dictionary of artibutes of the current node},
  "frame" : "{(top,left},{width,height}}", # notes this is not a dictionary
  "nodes": [list of subviews], # a subview is a node
  "class": "class type"
}

The topmost node (the rootView) is a list with a single node

'''
import ui, console,os,os.path,sys,json,re,uuid,math

import uidir; reload(uidir); from uidir import FileGetter

depthColors =  [(1.00, 0.80, 0.40),
                (1.00, 1.00, 0.00),
                (0.40, 0.80, 1.00),
                (0.90, 0.90, 0.90),
                (1.00, 0.40, 1.00),
                (0.80, 1.00, 0.40),
               ]

validQuadTuple = re.compile(r"""\(
                                 \D?([+-]?\d+\.?\d*)
                                 \D*([+-]?\d+\.?\d*)
                                 \D*([+-]?\d+\.?\d*)
                                 \D*([+-]?\d+\.?\d*)
                                 \D
                                 |
                                 \D?([+-]?\d+\.?\d*)
                                 \D*([+-]?\d+\.?\d*)
                                 \D*([+-]?\d+\.?\d*)
                                 \D*([+-]?\d+\.?\d*)
                                 """,
                              re.X)
                              


genericView =   '''
    						{{
    							"attributes": {{
      						"tint_color": "RGBA(0.000000,0.000000,1.000000,1.000000)", 
      						"border_color": "RGBA(0.000000,0.000000,0.000000,1.000000)", 
      						"background_color": "RGBA(1.000000,1.000000,1.000000,1.000000)", 
      						"enabled": true, 
      						"flex": "",
      						"uuid": "{}",
      						"name": "{}",
    							}}, 
    							"frame": "{}",
    							"nodes": {},
    							"class": "View"						
    						}}
    						'''

class NodeListWalker(object):
	def __init__(self):
		self._level = -1
		self.nodes = []
		self.parent = ["ROOT_UUID"]
		self.uuid = "ROOT_UUID"
		self.frameByUUID = {}
		
	def reset(self):
		self._level = -1
		self.nodes = []   
		
	@property
	def level(self):
		return self._level		
	
	@level.setter	
	def level(self,value):
		self._level = value
		
	def parseFrame(self,frame):
		parser = re.compile(r'\{\{(.*),(.*)\}.*\{(.*),(.*\d)\}')
		res  = parser.match(frame).groups()
		list = [float(x) for x in res]
		return tuple(list)
				
	def traverseNodeList(self,nodeList):
		self._level += 1
		if nodeList:
			for node in nodeList:
				attributes = node['attributes']
				classType = node['class']
				frame = self.parseFrame(node['frame'])
				if self._level:
					nodeName = attributes['name'] if 'name' in attributes.keys() else "NULL"
					self.uuid = attributes['uuid'] if 'uuid' in attributes.keys() else "NULL"
				else:
					nodeName = "BASE"
					self.uuid = 'ROOT_UUID'
				nodes = node['nodes']

				thisParent = self.parent[-1] if len(self.parent) else "ROOT_UUID"
				self.frameByUUID[self.uuid] = (frame,thisParent)
				self.nodes.append({'level':self._level,
				                   'attributes': attributes,
				                   'frame':frame,
				                   'nodes':nodes,
				                   'class':classType,
				                   'parent':thisParent,
				                   'uuid':self.uuid,
				                   'name':nodeName,
				                   })
				self.parent.append(self.uuid)
				self.traverseNodeList(nodes)
		self.parent = self.parent[:-1]
		self._level -= 1


		
class nodeMapView(ui.View):
	def did_load(self):
		self.nodes = []

	def inRectangle(self,point,rect):
		if (rect[0] <= point[0] <= rect[0]+rect[2]) and (rect[1] <= point[1] <= rect[1]+rect[3]):
			return True
		else:
			return False
		
		
	def centroid(self,frame):
		cX = frame[2]/2.0 + frame[0]
		cY = frame[3]/2.0 + frame[1]
		return (cX,cY)
		
	def angle_distance(self,p1,p2):
		deltaX = p1[0] - p2[0]
		deltaY = p1[1] - p2[1]
		return (math.atan2(deltaY,deltaX), math.sqrt(deltaX*deltaX + deltaY*deltaY))
		
	def displace(self,point,centroid):
		''' diplace a point towards to centroid'''
		angle,distance = self.angle_distance(point,centroid)
		displacement = 0 #distance*(.005)#(1.0 - self.ratio)
		deltaX = -displacement*math.cos(angle)
		deltaY = -displacement*math.sin(angle)
		return (deltaX, deltaY)
		
				
	def init(self,data_source):
		self.items = data_source.items
		self.pyuiFrame = self.items[0]['node']['frame']
		self.pyuiWidth = self.pyuiFrame[2] - self.pyuiFrame[0]
		self.pyuiHeight = self.pyuiFrame[3] - self.pyuiFrame[1]
		if self.pyuiWidth > self.pyuiHeight:
			self.ratio = self.width/self.pyuiWidth
		else:
			self.ratio = self.height/self.pyuiHeight
		
		
	def draw(self):
		if not self.items: return
		topNodesFrame = self.items[0]['node']['frame']
		topNodeCentroid = self.centroid(topNodesFrame)
		
# need to account for orgins ofr parents.  need to walk down the tree

		for item in self.items:
			title = item['title']
			node = item['node']
			frame = node['frame']
			level = node['level']
			uuid = node['uuid']
			parent = node['parent']
			isSelected = item['selected']
			isHidden = item['hidden']
			offset = [0,0]
			while parent != 'ROOT_UUID':
				parentFrame,parent = walker.frameByUUID[parent]
				offset = [offset[0] + parentFrame[0], offset[1] +parentFrame[1]]
					
			frame = [frame[0] + offset[0], frame[1] + offset[1], frame[2], frame[3]]	
			if not isHidden and level:
				path = ui.Path.rect(*[x*self.ratio for x in frame])
				ui.set_color((depthColors[level]) + (0.5,))
				path.fill()
				ui.set_color(0.5)
				path.line_width = 5 if isSelected else 2
				path.stroke()
			
			
	def touch_began(self,touch):
		location = touch.location
		for row,item in enumerate(nodeDelegate.items[1:]):
			if self.inRectangle(location,[x*self.ratio for x in item['node']['frame']]) and not item['hidden']:
				nodeDelegate.items[row+1]['selected'] = not nodeDelegate.items[row+1]['selected']
				tvNodeList.reload_data()
				self.set_needs_display()
				
class NodeTableViewDelegate(object):
	def __init__(self,items):
		self.items = items
		self.listLength = len(self.items)
		
	def tableview_number_of_sections(self, tableview):
		# Return the number of sections (defaults to 1)
		return 1
	
	def delayed_reload(self):
		global tvNodeList
		tvNodeList.selected_rows = []
		tvNodeList.reload_data()
		

	def tableview_number_of_rows(self, tableview, section):
		# Return the number of rows in the section
		return self.listLength

	def tableview_cell_for_row(self, tableview, section, row):
		# Create and return a cell for the given section/row
		cell = ui.TableViewCell()
		cell.text_label.text = self.items[row]['title']
		if self.items[row]['hidden']:
			cell.text_label.text_color = (0.90, 0.90, 0.90)
		else:
			cell.text_label.text_color = 'red' if self.items[row]['selected'] else 'black'	
		cell.accessory_type = 'detail_button'
		level = self.items[row]['node']['level']
		cell.background_color = depthColors[level]
		return cell
	
	def tableview_did_select(self, tableview, section, row):
		# Called when a row was selected.
		if not self.items[row]['hidden']:
			self.items[row]['selected'] =  not self.items[row]['selected']
			viewNodeMap.set_needs_display()
		ui.delay(self.delayed_reload,0.05)

			
		
	def tableview_did_deselect(self,tableview,section,row):
		pass

	def tableview_accessory_button_tapped(self, tableview, section, row):	
		console.hud_alert('Frame: {}'.format(self.items[row]['node']['frame']))

def collectiveSize(selected,margin=(0,0,0,0)):
	' calculate size of a container with margins specified '
	topLeftX = 10000
	bottomRightX = -10000
	topLeftY = 10000
	bottomRightY = -10000
	for _,item in selected:
		frame = item['node']['frame']
		topLeftX = min(topLeftX,frame[0])
		topLeftY = min(topLeftY,frame[1])
		bottomRightX = max(bottomRightX, (frame[0]+frame[2]))
		bottomRightY = max(bottomRightY, (frame[1]+frame[3]))
	topLeftX -= margin[0]
	topLeftY -= margin[1]
	bottomRightX += margin[2]
	bottomRightY += margin[3]	
	return (topLeftX,topLeftY,bottomRightX - topLeftX, bottomRightY - topLeftY)
	
	
def onSave(button):
	pass

@ui.in_background
def onCollect(button):
	global tvNodeList
	selected = []
	for row,item in enumerate(tvNodeList.delegate.items):
		if item['selected']:
			selected.append((row,item))
	if selected:
		try:
			result = console.input_alert('Container View Margins',"Enter tuple of Left,Top,Right and Bottom Margins","(0,0,0,0)")
			match = validQuadTuple.match(result)
			if match:
				margins = [float(x) for x in match.groups() if x]
				if len(margins) != 4:
					console.hud_alert("{} is invalid margin definition".format(result))
			else:
				console.hud_alert("{} is invalid margin definition".format(result))
				return			
		except KeyboardInterrupt:
			margins = (0,0,0,0)	
		try: 
			name = console.input_alert('Container View Name','Enter name for new container view')
		except KeyboardInterrupt:
			return
			
		collectionFrame = collectiveSize(selected,margins)
		uuidString = str(uuid.uuid4()).upper()
		location = "{{{}, {}}}".format(*collectionFrame[:2])
		widthHeight = "{{{}, {}}}".format(*collectionFrame[2:])
		frame = "{{{}, {}}}".format(location,widthHeight)

		for row,item in selected:
			pass
				
						
		thisView = genericView.format(uuidString, name, frame, "***REPLACE***")
	
		tvNodeList.selected_rows = []
		tvNodeList.reload_data()
		viewNodeMap.set_needs_display()
		
		
		
		
def onSelectChildren(button):
	global nodeDelegate
	def markChildren(thisRow):
		thisUUID = nodeDelegate.items[thisRow]['node']['uuid']
		for row in range(thisRow,len(nodeDelegate.items)):
			if nodeDelegate.items[row]['node']['parent'] == thisUUID:
				nodeDelegate.items[row]['selected'] = True
				markChildren(row)
						
	selected = -1
	for row,item in enumerate(nodeDelegate.items):
		if item['selected']:
			selected = row
			break
	if selected < 0:
		return
	markChildren(selected)
	tvNodeList.reload_data()
	viewNodeMap.set_needs_display()

		
def onQuit(button):
	global v
	v.close()
	
def onFlatten(button):
	pass
	
def onUndo(button):
	pass
	
def onHideSelected(button):
	global nodeDelegate
	for row,item in enumerate(nodeDelegate.items):
		if item['selected']:
			nodeDelegate.items[row]['hidden'] = True
			item['selected'] = False
	viewNodeMap.set_needs_display()
	tvNodeList.reload_data()
			
	
def onUnhideAll(button):
	global nodeDelegate
	for item in nodeDelegate.items:
		item['hidden'] = False
	viewNodeMap.set_needs_display()
	tvNodeList.reload_data()
	
def onDeselectAll(button):
	global nodeDelegate
	for item in nodeDelegate.items:
		item['selected'] = False
	viewNodeMap.set_needs_display()
	tvNodeList.reload_data()

fg = FileGetter()
fg.getFile()
thisFile = fg.selection


_,ext = os.path.splitext(thisFile)
if not ext in ['.pyui','.json']:
	console.hud_alert('Invalid file type')
	sys.exit(1)
	
with open(thisFile,'r') as fh:
	pyui = json.load(fh)

#print json.dumps(pyui,indent=2)	
	
walker = NodeListWalker()
walker.traverseNodeList(pyui)

items = [{
          'title': "{}{}".format(x['level']*2*'   ',x['name']),
          'node' : x, 
          'selected':False,
          'hidden':False,
          'accessory_type':None
          } 
          for x in walker.nodes]
          
v = ui.load_view()
nodeDelegate = NodeTableViewDelegate(items)
tvNodeList = v['view_nodeList']
tvNodeList.delegate = tvNodeList.data_source = nodeDelegate
tvNodeList.allows_multiple_selection = True

viewNodeMap = v['nodeMap']
viewNodeMap.init(nodeDelegate)
viewNodeMap.touch_enabled = True

v['button_Collect'].action = onCollect
v['button_Quit'].action = onQuit 
v['button_Flatten'].action = onFlatten
v['button_Save'].action = onSave
v['button_Undo'].action = onUndo
v['button_Hide_Selected'].action = onHideSelected
v['button_Unhide_All'].action = onUnhideAll
v['button_Select_Children'].action = onSelectChildren
v['button_Deselect_All'].action = onDeselectAll

v.present()



          

	