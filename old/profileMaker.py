import math
import wx
import os

MATERIALS_DIR			=	"C:\\Program Files\\Ultimaker Cura 3.3\\resources\\materials\\"
MATERIALS_EXT			=	".xml.fdm_material"
QUALITY_DIR				=	"C:\\Program Files\\Ultimaker Cura 3.3\\resources\\quality\\"
QUALITY_EXT				=	".inst.cfg"
# PRINTERS				=	["ultimaker2_plus", "ultimaker3", "ultimaker_s5"]
PRINTERS				=	["ultimaker2_plus"]
PRINTER_SHORTS			=	["um2p", "um3", "um_s5"]
PRINTER_IDENTIFIERS		=	["Ultimaker 2+", "Ultimaker 3", "Ultimaker S5"]
PRINTER_TAGS			=	[	
								"			<machine_identifier manufacturer=\"Ultimaker B.V.\" product=\"Ultimaker 2+\"/>\n            <machine_identifier manufacturer=\"Ultimaker B.V.\" product=\"Ultimaker 2 Extended+\"/>\n",
								"			<machine_identifier manufacturer=\"Ultimaker B.V.\" product=\"Ultimaker 3\"/>\n			<machine_identifier manufacturer=\"Ultimaker B.V.\" product=\"Ultimaker 3 Extended\"/>\n",
								"			<machine_identifier manufacturer=\"Ultimaker B.V.\" product=\"Ultimaker S5\"/>\n"
							]
						
class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title = "Cura profile maker")
		
		self.parent = wx.Panel(self)
		nb = Notebook(self)
		
		self.fileTab = FileTab(nb)
		self.materialTab = MaterialTab(nb)
		
		nb.AddPage(self.fileTab, "Choose file")
		nb.AddPage(self.materialTab, "Edit material")
		
		self.printerTabs = []
		for i in range(0, len(PRINTERS)):
			self.printerTabs.append(PrinterTab(nb))
			nb.AddPage(self.printerTabs[i], PRINTERS[i])
		
		sizer = wx.BoxSizer()
		sizer.Add(nb, 1, wx.EXPAND)
		self.parent.SetSizer(sizer)
		self.SetMinSize(wx.Size(800, 600))

class Notebook(wx.Notebook):
	def __init__(self, parent):
		wx.Notebook.__init__(self, parent.parent)
		self.parent = parent

class FileTab(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.master = self.parent.parent
		
		self.parent.fileList = wx.ListBox(self, size = wx.Size(256, 512), choices = [], pos = wx.Point(10, 10), style = wx.LB_SINGLE)
		
		self.refreshFileList()
		
		self.openButton = wx.Button(self, -1, "Open file", pos = wx.Point(276, 10))
		self.openButton.Bind(wx.EVT_BUTTON, self.openButton_clicked)
		
		self.saveButton = wx.Button(self, -1, "Save file", pos = wx.Point(276, 40))
		self.saveButton.Bind(wx.EVT_BUTTON, self.saveButton_clicked)
		
		self.saveNewButton = wx.Button(self, -1, "Save as new", pos = wx.Point(276, 70))
		self.fileNameText = wx.TextCtrl(self, -1, "makerpoint_material", pos = wx.Point(376, 73), size = wx.Size(256, 20))
		self.saveNewButton.Bind(wx.EVT_BUTTON, self.saveNewButton_clicked)
	
	def refreshFileList(self):
		self.parent.fileList.Clear()
		self.files = os.listdir(MATERIALS_DIR)
		for i in range(0, len(self.files)):
			self.parent.fileList.Append(self.files[i][0:self.files[i].find(MATERIALS_EXT)])
	
	def openButton_clicked(self, event):
		index = self.parent.fileList.GetSelection()
		
		file = open("{}{}".format(MATERIALS_DIR, self.files[index]))
		self.materialName = self.files[index][0:self.files[index].find(MATERIALS_EXT)]
		self.materialText = file.read()
		self.materialTextLength = len(self.materialText)
		file.close()
		
		self.extractMaterialProperties()
		self.extractPrinterProfiles()
	
	def extractMaterialProperties(self):
		tags = self.master.materialTab.tags
		settings = self.master.materialTab.settings
		
		for i in range(0, len(tags)):
			self.master.materialTab.changeTagValue(tags[i], self.extractMaterialTag(tags[i], [], []))
		
		for i in range(0, len(settings)):
			self.master.materialTab.changeTagValue(settings[i], self.extractMaterialTag("setting ", ["key"], [settings[i]]))
	
	def extractMaterialTag(self, name, keyId, key):
		openingBracket = 0
		openingBracket2 = 0
		rerun = False
		while True:
			openingBracket = self.materialText.find("<{}".format(name), openingBracket2)
			if(openingBracket <= 0):
				return ""
			closingBracket = self.materialText.find(">", openingBracket + 1)
			openingBracket2 = self.materialText.find("<", closingBracket + 1)
			if(len(keyId) != 0):
				for i in range(0, len(keyId)):
					if(self.materialMatchTagKey(keyId[i], key[i], openingBracket) == False):
						rerun = True
					else:
						rerun = False
						break
				if(rerun):
					continue
			return self.materialText[closingBracket + 1:openingBracket2]
	
	def materialMatchTagKey(self, keyId, key, openingBracket):
		index1 = self.materialText.find("{}=\"".format(keyId), openingBracket) + len(keyId) + 2
		index2 = self.materialText.find("\"", index1)
		if(index1 < openingBracket):
			return False
		elif(self.materialText[index1:index2] == key):
			return True
		return False
	
	def extractPrinterProfiles(self):
		for i in range(0, len(PRINTERS)):
			self.master.printerTabs[i].removeAllTags()
			files = os.listdir("{}\\{}".format(QUALITY_DIR, PRINTERS[i]))
			self.propertyList = []
			for j in range(0, len(files)):
				file = open("{}\\{}\\{}".format(QUALITY_DIR, PRINTERS[i], files[j]))
				self.text = file.read()
				if(self.text.find("material = {}".format(self.materialName)) > 0):
					self.master.printerTabs[i].profiles.append(Profile())
					index = len(self.master.printerTabs[i].profiles) - 1
					
					self.profile = self.master.printerTabs[i].profiles[index]
					
					index1 = self.text.find("name") + 7
					index2 = self.text.find("\n", index1)
					self.profile.name = self.text[index1:index2]
					
					index1 = self.text.find("variant") + 10
					index2 = self.text.find("\n", index1)
					tmp = self.text[index1:index2].split(" ")
					try:
						self.profile.variant = "{}".format(float(tmp[0]))
					except ValueError:
						self.profile.variant = "{}".format(float(tmp[1]))
					self.profile.name = self.text[index1:index2]
					
					index1 = self.text.find("quality_type") + 15
					index2 = self.text.find("\n", index1)
					self.profile.quality_type = self.text[index1:index2]
					
					self.profileName = "{}_{}_{}_{}".format(PRINTER_SHORTS[i], self.materialName, self.profile.variant, self.profile.quality_type)
					print self.profileName
					
					self.extractAllProfileProperties()
		for i in range(0, len(PRINTERS)):
			for I in range(0, len(self.propertyList)):
				values = []
				for j in range(0, len(self.master.printerTabs[i].profiles)):
					values.append("")
					for k in range(0, len(self.master.printerTabs[i].profiles[j].values)):						
						if(self.master.printerTabs[i].profiles[j].values[k].name == self.propertyList[I]):
							values[j] = self.master.printerTabs[i].profiles[j].values[k].value
				self.master.printerTabs[i].tagList.append(ProfileTag(self.master.printerTabs[i], self.propertyList[I], values, (10, 40 + I * 30)))
	
	def extractAllProfileProperties(self):
		generalIndex = self.text.find("[metadata]")
		metadataIndex = self.text.find("[values]")
		valuesIndex = len(self.text)
		
		index = 0
		while (index < generalIndex):
			indexEnter = self.text.find("\n", index + 1)
			p = self.extractSingleProperty(index, indexEnter)
			if(len(p) > 0):
				self.profile.general.append(Property(p[0], p[1]))
			index = indexEnter + 1
		while (index < metadataIndex):
			indexEnter = self.text.find("\n", index + 1)
			p = self.extractSingleProperty(index, indexEnter)
			if(len(p) > 0):
				self.profile.metadata.append(Property(p[0], p[1]))
			index = indexEnter + 1
		while (index < valuesIndex):
			indexEnter = self.text.find("\n", index + 1)
			p = self.extractSingleProperty(index, indexEnter)
			if(len(p) > 0):
				self.profile.values.append(Property(p[0], p[1]))
			index = indexEnter + 1
			propertyExists = False
			for i in range(0, len(self.propertyList)):
				if(self.propertyList[i] == p[0]):
					properyExists = True
					break
			if(propertyExists == False):
				self.propertyList.append(p[0])
	
	def extractSingleProperty(self, index, indexEnter):
		indexEqualSign = self.text.find("=", index)
		if(indexEqualSign >= indexEnter):
			return []
		else:
			name = self.text[index:indexEqualSign - 1]
			return [name, self.text[indexEqualSign + 2:indexEnter]]
	
	def saveButton_clicked(self, event):
		print "test"
	
	def saveNewButton_clicked(self, event):
		print "rest"

class MaterialTab(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		
		self.tagList = []
		
		self.tags = ["brand", "material", "color", "GUID", "version", "color_code", "description", "adhesion_info", "density", "diameter"]
		self.settings = ["print temperature", "heated bed temperature", "standby temperature", "adhesion tendency", "surface energy", "shrinkage percentage", "retraction amount", "retraction speed", "print cooling"]
		
		for i in range(0, len(self.tags)):
			self.tagList.append(Tag(self, self.tags[i], (10, 10 + i * 30)))
		
		for i in range(0, len(self.settings)):
			self.tagList.append(Tag(self, self.settings[i], (10, 10 + (len(self.tags) + i) * 30)))
	
	def changeTagValue(self, name, value):
		for i in range(0, len(self.tagList)):
			if(self.tagList[i].name == name):
				self.tagList[i].text.SetValue(value)
				return

class PrinterTab(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		
		self.tagList = []
		self.profiles = []
	
	def removeAllTags(self):
		for i in range(0, len(self.tagList)):
			self.tagList[i].label.Destroy()
			for j in range(0, len(self.tagList[i].texts)):
				self.tagList[i].texts[j].Destroy()
		self.tagList = []
		self.profiles = []

class ProfileTag():
	def __init__(self, parent, name, values, pos_):
		self.parent = parent
		self.label = wx.StaticText(self.parent, -1, name, pos = pos_)
		self.texts = []
		for i in range(0, len(values)):
			self.texts.append(wx.TextCtrl(self.parent, -1, values[i], pos = [pos_[0] + 192 + i * 138, pos_[1]], size = wx.Size(128, 20)))

class Tag():
	def __init__(self, parent, name, pos_):
		self.name = name
		self.parent = parent
		self.label = wx.StaticText(self.parent, -1, name, pos = pos_)
		self.text = wx.TextCtrl(self.parent, -1, "", pos = [pos_[0] + 192, pos_[1]], size = wx.Size(512, 20))

class Profile():
	def __init__(self):
		self.general = []
		self.metadata = []
		self.values = []
		self.name = ""
		self.variant = ""
		self.quality_type = ""
		self.profileName = ""

class Property():
	def __init__(self, name, value):
		self.name = name
		self.value = value

if __name__ == "__main__":
	app = wx.App()
	MainFrame().Show()
	app.MainLoop()