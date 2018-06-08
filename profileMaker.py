import math
import wx
import os

MATERIALS_DIR			=	"C:\\Program Files\\Ultimaker Cura 3.3\\resources\\materials\\"
MATERIALS_EXT			=	".xml.fdm_material"
QUALITY_DIR				=	"C:\\Program Files\\Ultimaker Cura 3.3\\resources\\quality\\"
QUALITY_EXT				=	".inst.cfg"
PRINTERS				=	["ultimaker2_plus", "ultimaker3", "ultimaker_s5"]
PRINTER_SHORTS			=	["um2p", "um3", "um_s5"]
PRINTER_IDENTIFIERS		=	["Ultimaker 2+", "Ultimaker 3", "Ultimaker S5"]
PRINTER_TAGS			=	[	
								"	  <machine_identifier manufacturer=\"Ultimaker B.V.\" product=\"Ultimaker 2+\"/>\n	  <machine_identifier manufacturer=\"Ultimaker B.V.\" product=\"Ultimaker 2 Extended+\"/>\n",
								"	  <machine_identifier manufacturer=\"Ultimaker B.V.\" product=\"Ultimaker 3\"/>\n	  <machine_identifier manufacturer=\"Ultimaker B.V.\" product=\"Ultimaker 3 Extended\"/>\n",
								"	  <machine_identifier manufacturer=\"Ultimaker B.V.\" product=\"Ultimaker S5\"/>\n"
							]
VARIANTS				=	[
								["0.25 mm", "0.4 mm", "0.6 mm", "0.8 mm"],
								["AA 0.25", "AA 0.4", "AA 0.8", "BB 0.4", "BB 0.8"],
								["AA 0.25", "AA 0.4", "AA 0.8", "BB 0.4", "BB 0.8"]
							]
PRINTER_D_TEMP			=	[0, -10, -10]
TAGS					=	["brand", "material", "color", "GUID", "version", "color_code", "description", "adhesion_info", "density", "diameter"]
SETTINGS				=	["print temperature", "heated bed temperature", "standby temperature", "adhesion tendency", "surface energy", "heated bed temperature", "shrinkage percentage", "retraction amount", "retraction speed", "print cooling"]

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title = "Cura profile maker")
		
		self.parent = wx.Panel(self)
		nb = Notebook(self)
		
		self.fileTab = FileTab(nb)
		
		nb.AddPage(self.fileTab, "Choose file")
		
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
		
		self.openButton = wx.Button(self, -1, "Open profile", pos = wx.Point(276, 10))
		self.openButton.Bind(wx.EVT_BUTTON, self.openButton_clicked)
		
		self.exportButton = wx.Button(self, -1, "Export profile", pos = wx.Point(276, 40))
		self.fileNameText = wx.TextCtrl(self, -1, "makerpoint_material", pos = wx.Point(376, 43), size = wx.Size(256, 20))
		self.exportButton.Bind(wx.EVT_BUTTON, self.exportButton_clicked)
		
		self.importButton = wx.Button(self, -1, "Import profile", pos = wx.Point(276, 70))
		self.importButton.Bind(wx.EVT_BUTTON, self.importButton_clicked)

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
		print self.materialName
		file.close()
		
		self.extractMaterialProperties()
		self.extractPrinterProfiles()
	
	def extractMaterialProperties(self):
		self.tags = [0 for i in range(0, len(TAGS))]
		self.settings = [0 for i in range(0, len(SETTINGS))]
		
		for i in range(0, len(TAGS)):
			self.tags[i] = self.extractMaterialTag(TAGS[i], [], [], 0)
		
		for i in range(0, len(SETTINGS)):
			self.settings[i] = self.extractMaterialTag("setting ", ["key"], [SETTINGS[i]], 0)

	def extractMaterialTag(self, name, keyId, key, startIndex):
		openingBracket = 0
		openingBracket2 = startIndex
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
		self.printerProfiles = [[] for i in range(0, len(PRINTERS))]
		self.activeProfile = Profile()
		self.propertyList = []
		for i in range(0, len(PRINTERS)):
			files = os.listdir("{}\\{}".format(QUALITY_DIR, PRINTERS[i]))
			for j in range(0, len(files)):
				file = open("{}{}\\{}".format(QUALITY_DIR, PRINTERS[i], files[j]))
				self.text = file.read()
				self.textLength = len(self.text)
				if(self.text.find("material = {}".format(self.materialName)) > 0):
					print "{}{}\\{}".format(QUALITY_DIR, PRINTERS[i], files[j])
					index = len(self.printerProfiles[i])
					self.printerProfiles[i].append(Profile())
					self.activeProfile = self.printerProfiles[i][index]
					
					self.activeProfile.name = self.extractProfileTag("name")
					tmp = self.extractProfileTag("variant").split(" ")
					try:
						self.activeProfile.variant = "{}".format(float(tmp[0]))
					except ValueError:
						self.activeProfile.variant = "{}".format(float(tmp[1]))
					self.activeProfile.quality_type = self.extractProfileTag("quality_type")
					self.activeProfile.profileName = "{}_{}_{}_{}".format(PRINTER_SHORTS[i], self.materialName, self.activeProfile.variant, self.activeProfile.quality_type)
					
					self.extractAllProfileProperties()

	def extractProfileTag(self, tag):
		index1 = self.text.find(tag) + len(tag) + 3
		index2 = self.text.find("\n", index1)
		return self.text[index1:index2]
	
	def extractAllProfileProperties(self):
		index = 0
		currentTag = ""
		prevIndex = 0
		
		while((index >= 0) & (index < self.textLength)):
			indexEnter = self.text.find("\n", index + 1)
			if(indexEnter < prevIndex):
				break
			prevIndex = indexEnter
			if(self.text[index] == "\n"):
				index = index + 1
				continue
			if(self.text[index] == "["):
				currentTag = self.text[index:indexEnter]
			else:
				p = self.extractSingleProperty(index, indexEnter)
				if(len(p) > 0):
					self.activeProfile.properties.append(Property(p[0], p[1], currentTag))
					propertyExists = False
					for i in range(0, len(self.propertyList)):
						if(self.propertyList[i][1] == p[0]):
							propertyExists = True
							break
					if(propertyExists == False):
						self.propertyList.append([currentTag, p[0]])
			index = indexEnter + 1
	
	def extractSingleProperty(self, index, indexEnter):
		indexEqualSign = self.text.find("=", index)
		if(indexEqualSign >= indexEnter):
			return []
		else:
			name = self.text[index:indexEqualSign - 1]
			return [name, self.text[indexEqualSign + 2:indexEnter]]
	
	def exportButton_clicked(self, event):
		file = open("worksheetOptions.xml", "r")
		self.WORKSHEET_OPTIONS = file.read()
		file.close()
		self.text = ""
		
		self.startWorksheet("Material", 1, 2, len(self.tags) + len(self.settings))
		for i in range(0, len(self.tags)):
			self.addRow([TAGS[i], self.tags[i]])
		for i in range(0, len(self.settings)):
			self.addRow([SETTINGS[i], self.settings[i]])
		self.closeWorksheet()
		
		for i in range(0, len(PRINTERS)):
			self.startWorksheet(PRINTERS[i], 2, 2 + len(self.printerProfiles[i]), len(self.propertyList))
			for j in range(0, len(self.propertyList)):
				data = [self.propertyList[j][0], self.propertyList[j][1]]
				for k in range(0, len(self.printerProfiles[i])):
					data.append("")
					for l in range(0, len(self.printerProfiles[i][k].properties)):
						if(self.printerProfiles[i][k].properties[l].name == self.propertyList[j][1]):
							data[k + 2] = self.printerProfiles[i][k].properties[l].value
				self.addRow(data)
			self.closeWorksheet()
		
		file = open("xmlBase.xml", "r")
		self.fileText = file.read()
		self.fileTextLength = len(self.fileText)
		file.close()
		
		index = self.fileText.find("<!-- Insert data here -->")
		index = self.fileText.find("\n", index) + 1
		self.fileText = self.fileText[0:index] + self.text + self.fileText[index:self.fileTextLength]
		
		file = open("{}.xml".format(self.fileNameText.GetLineText(0)), "w")
		file.write(self.fileText)
		file.close()
	
	def startWorksheet(self, name, amountBold, columns, rows):
		self.text += " <Worksheet ss:Name=\"{}\">\n".format(name)
		self.text += "  <Table ss:ExpandedColumnCount=\"{}\" ss:ExpandedRowCount=\"{}\" x:FullColumns=\"1\" x:FullRows=\"1\" ss:DefaultRowHeight=\"15\">\n".format(columns, rows)
		for i in range(0, amountBold):
			self.text += "  <Column ss:StyleID=\"s62\" ss:AutoFitWidth=\"0\" ss:Width=\"150\"/>\n"
		for i in range(0, columns - amountBold):
			self.text += "  <Column ss:AutoFitWidth=\"0\" ss:Width=\"150\"/>\n"
	
	def addRow(self, data):
		self.text += "   <Row>\n"
		for i in range(0, len(data)):
			try:
				float(data[i])
				self.text += "    <Cell><Data ss:Type=\"Number\">{}</Data></Cell>\n".format(data[i])
			except ValueError:
				self.text += "    <Cell><Data ss:Type=\"String\">{}</Data></Cell>\n".format(data[i])
		self.text += "   </Row>\n"
	
	def closeWorksheet(self):
		self.text += self.WORKSHEET_OPTIONS
	
	def importButton_clicked(self, event):
		with wx.FileDialog(self, "Open XML file", wildcard="XML files (*.xml)|*.xml", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return

			pathname = fileDialog.GetPath()
			file = open(pathname, "r")
			self.materialText = file.read()
			self.materialTextLength = len(self.materialText)
			
			self.tags = [0 for i in range(0, len(TAGS))]
			self.settings = [0 for i in range(0, len(SETTINGS))]
			self.printerProfiles = [[] for i in range(0, len(PRINTERS))]
			
			self.extractTagsFromXML()
			self.createMaterialFile()
			self.extractProfilesFromXML()
			self.createPrinterFiles()
	
	def extractTagsFromXML(self):
		index = 0
		for i in range(0, len(TAGS)):
			index = self.materialText.find("<Cell><Data ss:Type=\"String\">{}</Data></Cell>".format(TAGS[i]), index + 1)
			self.tags[i] = self.extractMaterialTag("Data", [], [], index + 10)
		for i in range(0, len(SETTINGS)):
			index = self.materialText.find("<Cell><Data ss:Type=\"String\">{}</Data></Cell>".format(SETTINGS[i]), index + 1)
			self.settings[i] = self.extractMaterialTag("Data", [], [], index + 10)
		self.materialName = self.extractTag("brand").lower() + "_" + self.extractTag("material").lower().replace("-", "")
	
	def createMaterialFile(self):
		file = open("{}{}{}".format(MATERIALS_DIR, self.materialName, MATERIALS_EXT), "w")
		file.write("<?xml version='1.0' encoding='utf-8'?>\n<fdmmaterial version=\"1.3\" xmlns=\"http://www.ultimaker.com/material\" xmlns:cura=\"http://www.ultimaker.com/cura\">\n  <metadata>\n    <name>\n")
		file.write("      <{}>{}</{}>\n".format("brand", self.extractTag("brand"), "brand"))
		file.write("      <{}>{}</{}>\n".format("material", self.extractTag("material"), "material"))
		file.write("      <{}>{}</{}>\n".format("color", self.extractTag("color"), "color"))
		file.write("      <{}>{}</{}>\n".format("label", self.extractTag("material"), "label"))
		file.write("    </name>\n")
		file.write("    <{}>{}</{}>\n".format("adhesion_info", self.extractTag("adhesion_info"), "adhesion_info"))
		file.write("    <{}>{}</{}>\n".format("compatible", "True", "compatible"))
		file.write("    <{}>{}</{}>\n".format("color_code", self.extractTag("color_code"), "color_code"))
		file.write("    <{}>{}</{}>\n".format("description", self.extractTag("description"), "description"))
		file.write("    <{}>{}</{}>\n".format("definition", "fdmprinter", "definition"))
		file.write("    <{}>{}</{}>\n".format("version", self.extractTag("version"), "version"))
		file.write("    <{}>{}</{}>\n".format("GUID", self.extractTag("GUID"), "GUID"))
		file.write("  </metadata>\n  <properties>\n")
		file.write("    <{}>{}</{}>\n".format("density", self.extractTag("density"), "density"))
		file.write("    <{}>{}</{}>\n".format("diameter", self.extractTag("diameter"), "diameter"))
		file.write("  </properties>\n  <settings>\n")
		file.write("    <setting key=\"{}\">{}</setting>\n".format("surface energy", self.extractSetting("surface energy")))
		file.write("    <setting key=\"{}\">{}</setting>\n".format("heated bed temperature", self.extractSetting("heated bed temperature")))
		file.write("    <setting key=\"{}\">{}</setting>\n".format("adhesion tendency", self.extractSetting("adhesion tendency")))
		file.write("    <setting key=\"{}\">{}</setting>\n".format("retraction speed", self.extractSetting("retraction speed")))
		file.write("    <setting key=\"{}\">{}</setting>\n".format("retraction amount", self.extractSetting("retraction amount")))
		for i in range(0, len(PRINTER_TAGS)):
			file.write("    <machine>\n{}".format(PRINTER_TAGS[i]))
			file.write("	  <setting key=\"{}\">{}</setting>\n".format("print temperature", float(self.extractSetting("print temperature")) + PRINTER_D_TEMP[i]))
			file.write("	  <setting key=\"{}\">{}</setting>\n".format("standby temperature", float(self.extractSetting("standby temperature")) + PRINTER_D_TEMP[i]))
			for j in range(0, len(VARIANTS[i])):
				file.write("      <hotend id=\"{}\">\n        <setting key=\"hardware compatible\">yes</setting>\n      </hotend>\n".format(VARIANTS[i][j]))
			file.write("    </machine>\n")
			
		file.write("  </settings>\n</fdmmaterial>")
		
		file.close()
	
	def extractProfilesFromXML(self):
		for i in range(0, len(PRINTERS)):
			index = self.materialText.find("<Worksheet ss:Name=\"{}\">".format(PRINTERS[i]))
			if(index >= 0):
				indexR1 = self.materialText.find("<Row", index)
				indexR2 = self.materialText.find("</Row>", indexR1)
				amountProfiles = self.materialText[indexR1:indexR2].count("<Cell><Data ss:Type=") - 2
				self.printerProfiles[i] = [Profile() for z in range(0, amountProfiles)]
				index_ = self.materialText.find("<Cell><Data ss:Type=", index)
				endIndex = self.materialText.find("</Worksheet>", index_)
				while( (index_ < endIndex) & (index_ > index)):
					tagType = self.extractMaterialTag("Data", [], [], index_)
					index_ = self.materialText.find("<Cell><Data ss:Type=", index_ + 1)
					name = self.extractMaterialTag("Data", [], [], index_)
					index_ = self.materialText.find("<Cell><Data ss:Type=", index_ + 1)
					for j in range(0, amountProfiles):
						value = self.extractMaterialTag("Data", [], [], index_)
						self.printerProfiles[i][j].properties.append(Property(name, value, tagType))
						index_ = self.materialText.find("<Cell><Data ss:Type=", index_ + 1)
	
	def createPrinterFiles(self):
		for i in range(0, len(PRINTERS)):
			for j in range(0, len(self.printerProfiles[i])):
				self.activeProfile = self.printerProfiles[i][j]
				self.activeProfile.name = self.extractValueFromProfile("name")
				self.activeProfile.quality_type = self.extractValueFromProfile("quality_type")
				self.activeProfile.variant = self.extractValueFromProfile("variant").split("mm")[0].replace(" ", "").lower()
				self.activeProfile.profileName = "{}_{}_{}_{}{}".format(PRINTER_SHORTS[i], self.extractTag("material").lower().replace("-", ""), self.activeProfile.variant, self.activeProfile.quality_type, QUALITY_EXT)
				file = open("{}{}\\{}".format(QUALITY_DIR, PRINTERS[i], self.activeProfile.profileName), "w")
				currentTag = ""
				firstLine = True
				for k in range(0, len(self.activeProfile.properties)):
					if(len(self.activeProfile.properties[k].value) > 0):
						if(self.activeProfile.properties[k].tagType != currentTag):
							currentTag = self.activeProfile.properties[k].tagType
							if(firstLine):
								file.write("{}\n".format(currentTag))
								firstLine = False
							else:
								file.write("\n{}\n".format(currentTag))
						file.write("{} = {}\n".format(self.activeProfile.properties[k].name, self.activeProfile.properties[k].value))
				file.close()
	
	def extractValueFromProfile(self, name):
		for i in range(0, len(self.activeProfile.properties)):
			if(self.activeProfile.properties[i].name == name):
				return self.activeProfile.properties[i].value
		return "" 
	
	def extractMaterialKey(self, name, key, index):
		index_ = self.materialText.find("<{}".format(name), index)
		index_ = self.materialText.find(key, index_) + len(key) + 2
		index2 = self.materialText.find("\"", index_)
		return self.materialText[index_:index2]
		
	def extractTag(self, name):
		for i in range(0, len(TAGS)):
			if(TAGS[i] == name):
				return self.tags[i]
		return ""
	
	def extractSetting(self, name):
		for i in range(0, len(SETTINGS)):
			if(SETTINGS[i] == name):
				return self.settings[i]
		return ""

class Profile():
	def __init__(self):
		self.properties = []
		self.name = ""
		self.variant = ""
		self.quality_type = ""
		self.profileName = ""

class Property():
	def __init__(self, name, value, tagType):
		self.name = name
		self.value = value
		self.tagType = tagType

if __name__ == "__main__":
	app = wx.App()
	MainFrame().Show()
	app.MainLoop()