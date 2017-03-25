import re
import turtle
import sys

# Regex matching strings
# reExtended = '((?<=%).*(?=%))|((?<=%).*$)'
# reExtendedStart = '(?<=%).*'
# reExtendedEnd = '.*(?=%)'
reAttributeTF = '(?<=^TF).*'
reAttributeTA = '(?<=^TA).*'
reAttributeTD = '(?<=^TD).*'
reGraphicFS = '(?<=^FS).*'
reGraphicFSZeroMode = '^L|T'
reGraphicFSCoordNotation = '(?<=^L|T)A|I'
reGraphicFSXFormat = '(?<=X)[0-9][0-9]'
reGraphicFSYFormat = '(?<=Y)[0-9][0-9]'
reGraphicMO = '(?<=^MO).*'
reGraphicMOUnit = 'IN|MM'
reGraphicAD = '(?<=^AD).*'
reGraphicADDCode = '^D[1-9][0-9]'
reGraphicADName = '(?<=^D[1-9][0-9]).*(?=,)|(?<=^D[1-9][0-9]).*$'
reGraphicADModifiers = '(?<=,).*'
reGraphicAM = '(?<=^AM).*'
reGraphicAMExpr = '^\$.*'
reGraphicSR = '(?<=^SR).*'
reGraphicSRX = '(?<=X).*(?=Y)'
reGraphicSRY = '(?<=Y).*(?=I)'
reGraphicSRI = '(?<=I).*(?=J)'
reGraphicSRJ = '(?<=J).*$'
reGraphicLP = '(?<=^LP).*'
reGraphicLPCD = '^C|D'
reCoord = '(G[0-3]*|X[0-9+-]*|Y[0-9+-]*|I[0-9+-]*|J[0-9+-]*)*(D01$|D1$|D02$|D2$|D03$|D3$)'
reCoordX = '(?<=X)[0-9+-]*'
reCoordY = '(?<=Y)[0-9+-]*'
reCoordI = '(?<=I)[0-9+-]*'
reCoordJ = '(?<=J)[0-9+-]*'
reCoordD = 'D01|D1|D02|D2|D03|D3'
reCoordG = 'G01|G1|G02|G2|G03|G3'
reDnn = '^D[1-9][0-9]*$'

def regex(ex,s):
	try:
		r = re.search(ex,s).group(0)
		return r
	except AttributeError:
		return

# Aperture Primitive Enum
primitive = {
	0:'Comment',
	1:'Circle',
	2:'Vector Line',
	20:'Vector Line',
	21:'Center Line',
	22:'Lower Left Line',
	4:'Outline',
	5:'Polygon',
	6:'Moire',
	7:'Thermal'
}

# Attribute Match
class gerber:
	Attributes = {
		'.FileFunction':[],
		'.Part':[],
		'.MD5':[],
		'.AperFunction':[],
		'.DrillTolerance':[]
	}

	# define file attribute
	def TF(self,ExCode):
		for DataBlock in ExCode:
			tf = regex(reAttributeTF,DataBlock)
			if tf:
				name = tf.split(',')[0]
				value = tf.split(',')[1:]
				self.Attributes[name]=value
			else:
				print str(ExCode)+': Could not parse TF!'
				return False
		return True

	# add aperture attribute
	def TA(self,ExCode):
		for DataBlock in ExCode:
			ta = regex(reAttributeTA,DataBlock)
			if ta:
				name = ta.split(',')[0]
				value = ta.split(',')[1:]
				self.Attributes[name]=value
			else:
				print str(ExCode)+': Could not parse TA!'
				return False
		return True

	# delete aperture attribute
	def TD(self,ExCode):
		for DataBlock in ExCode:
			td = regex(reAttributeTD,DataBlock)
			if td:
				self.Attributes[td]=[]
			else:
				print str(ExCode)+': Could not parse TD!'
				return False
		return True

	Graphics = {
		'CoordinateFormat':{
			'ZeroOmissionMode':'',
			'CoordinateValuesNotation':'',
			'XFormat':'',
			'YFormat':''
		},
		'Unit':'',
		'ApertureDefinitions':[],
		'ApertureMacros':[],
		'StepAndRepeat':{
			'X':1,
			'Y':1,
			'I':0.0,
			'J':0.0
		},
		'LevelPolarity':'D',
		'CurrentAperture':{},
		'QuadrantMode':'',
		'InterpolationMode':'', # LIN, CW, CCW
		'CurrentPoint':{
			'X':0.0,
			'Y':0.0
		},
		'RegionMode':'Off'
	}

	# Coordinates = {
	# 	'X':0.0,
	# 	'Y':0.0,
	# 	'I':0.0,
	# 	'J':0.0
	# }

	def FS(self,fs):
		# FS(L|T)(A|I)X<Format>Y<Format>*
		for db in fs:
			fs = regex(reGraphicFS,db)
			zom = regex(reGraphicFSZeroMode,fs)
			cvn = regex(reGraphicFSCoordNotation,fs)
			xform = regex(reGraphicFSXFormat,fs)
			yform = regex(reGraphicFSYFormat,fs)

			if zom and cvn and xform and yform and xform==yform:
				self.Graphics['CoordinateFormat']={
				'ZeroOmissionMode':zom,
				'CoordinateValuesNotation':cvn,
				'XFormat':xform,
				'YFormat':yform
				}
			else:
				print fs+': Format Specification not parseable!'
				return False
		return True

	def MO(self,mo):
		# MO(IN|MM)*
		for db in mo:
			mo = regex(reGraphicMO,db)
			unit = regex(reGraphicMOUnit,mo)

			if unit:
				self.Graphics['Unit'] = unit
			else:
				print mo+': Unit not parseable!'
		return True

	def AD(self,ad):
		# ADD<D-code number><Aperture name>[,<Modifiers set>]*
		for db in ad:
			ad = regex(reGraphicAD,db)
			dcode = regex(reGraphicADDCode,ad)
			name = regex(reGraphicADName,ad)
			mods = regex(reGraphicADModifiers,ad)

			if dcode and name:
				d = {
					'DCode':dcode,
					'Name':name,
					'Function':self.Attributes['.AperFunction']
				}
			else:
				print ad+': Could not parse aperture!'
				return False

			if mods:
				d['Modifiers']=mods.split('X')

			self.Graphics['ApertureDefinitions'].append(d)
		return True

	def AM(self,am):
		# %AMDONUTVAR*1,1,$1,$2,$3*1,0,$4,$2,$3*%
		name = am[0]
		primitives = []
		for p in am[1:]:
			expr = regex(reGraphicAMExpr,p)
			if expr:
				pCode = None
				pName = 'Expression'
				pMods = [expr]
			else:
				pCode = int(p.split(',')[0])
				pName = primitive[pCode]
				pMods = p.split(',')[1:]
			prim = {
				'Code':pCode,
				'Name':pName,
				'Modifiers':pMods
				}
			primitives.append(prim)
		macro = {'Name':name,'Primitives':primitives}
		self.Graphics['ApertureMacros'].append(macro)
		return True

	def SR(self,sr):
		# %SRX3Y2I5.0J4.0*%
		for db in sr:
			sr = regex(reGraphicSR,db)
			x = regex(reGraphicSRX,sr)
			y = regex(reGraphicSRY,sr)
			i = regex(reGraphicSRI,sr)
			j = regex(reGraphicSRJ,sr)

			if x and y and i and j:
				self.Graphics['StepAndRepeat']={
					'X':int(x),
					'Y':int(y),
					'I':float(i),
					'J':float(j)
				}
			else:
				print sr+': Could not parse step and repeat!'
				return False
		return True

	def LP(self,lp):
		for db in lp:
			lp = regex(reGraphicLP,db)
			lpol = regex(reGraphicLPCD,lp)
			if lpol:
				self.Graphics['LevelPolarity'] = lpol
			else:
				print lp+': Could not parse level polarity!'
				return False
		return True

	def D01(self,x,y,i,j):
		# create event handler for physical movements?
		turtle.pendown()
		turtle.goto(x,y)
		turtle.penup()
		self.Graphics['CurrentPoint']['X'] = x
		self.Graphics['CurrentPoint']['Y'] = y
		# self.Coordinates['I'] = i
		# self.Coordinates['J'] = j
		return

	def D02(self,x,y,i,j):
		turtle.penup()
		turtle.goto(x,y)
		self.Graphics['CurrentPoint']['X'] = x
		self.Graphics['CurrentPoint']['Y'] = y
		# self.Coordinates['I'] = i
		# self.Coordinates['J'] = j
		return

	def D03(self,x,y,i,j):
		self.Graphics['CurrentPoint']['X'] = x
		self.Graphics['CurrentPoint']['Y'] = y
		# self.Coordinates['I'] = i
		# self.Coordinates['J'] = j
		return

	def DNN(self,dnn):
		# Event Handler for tool change?
		apertureDefinition = filter(lambda item: item['DCode'] == dnn, self.Graphics['ApertureDefinitions'])[0]
		print 'Change aperture to: ' + str(apertureDefinition)
		self.Graphics['CurrentAperture'] = apertureDefinition
		turtle.pen(fillcolor="black", pencolor="black", pensize=int(100*float(apertureDefinition['Modifiers'][0])))
		return True

	def parseCoordinate(self,coord):
		x = regex(reCoordX,coord)
		y = regex(reCoordY,coord)
		i = regex(reCoordI,coord)
		j = regex(reCoordJ,coord)
		d = regex(reCoordD,coord)
		g = regex(reCoordG,coord)

		if g in(['G01','G1']):
			self.Graphics['InterpolationMode'] = 'LIN'
		elif g in(['G02','G2']):
			self.Graphics['InterpolationMode'] = 'CW'
		elif g in(['G03','G3']):
			self.Graphics['InterpolationMode'] = 'CCW'

		if x:
			x = self.coord2float(x,self.Graphics['CoordinateFormat']['XFormat'])
		else:
			x = self.Graphics['CurrentPoint']['X']
		if y:
			y = self.coord2float(y,self.Graphics['CoordinateFormat']['YFormat'])
		else:
			y = self.Graphics['CurrentPoint']['Y']
		if i:
			i = self.coord2float(i,self.Graphics['CoordinateFormat']['XFormat'])
		else:
			i = 0.0
		if j:
			j = self.coord2float(j,self.Graphics['CoordinateFormat']['XFormat'])
		else:
			j = 0.0

		if d in(['D1','D01']):
			self.D01(x,y,i,j)
			return True
		elif d in(['D2','D02']):
			self.D02(x,y,i,j)
			return True
		elif d in(['D3','D03']):
			self.D03(x,y,i,j)
			return True
		else:
			print coord+': Could not parse coordinate!'
			return False

	def coord2float(self,c,format):
		# L = omit leading zeros
		# T = omit trailing zeros
		i = int(format[0])
		d = int(format[1])

		if c[0] in(['+','-']):
			if self.Graphics['CoordinateFormat']['ZeroOmissionMode']=='L':
				return float(c[0:len(c)-d]+'.'+c[len(c)-d:])
			elif self.Graphics['CoordinateFormat']['ZeroOmissionMode']=='T':
				return float(c[0:i+1]+'.'+c[i+1:])
		else:
			if self.Graphics['CoordinateFormat']['ZeroOmissionMode']=='L':
				return float(c[0:len(c)-d]+'.'+c[len(c)-d:])
			elif self.Graphics['CoordinateFormat']['ZeroOmissionMode']=='T':
				return float(c[0:i]+'.'+c[i:])
			else:
				print c+': Cannot parse coordinate using format: '+format
				return 0.0

	def ProcessExCode(self,ExCode):
		print 'Process ExCode: ' + str(ExCode)
		if regex(reAttributeTF,ExCode[0]):
			self.TF(ExCode)
		elif regex(reAttributeTA,ExCode[0]):
			self.TA(ExCode)
		elif regex(reAttributeTD,ExCode[0]):
			self.TF(ExCode)
		elif regex(reGraphicFS,ExCode[0]):
			self.FS(ExCode)
		elif regex(reGraphicMO,ExCode[0]):
			self.MO(ExCode)
		elif regex(reGraphicAD,ExCode[0]):
			self.AD(ExCode)
		elif regex(reGraphicAM,ExCode[0]):
			self.AM(ExCode)
		elif regex(reGraphicSR,ExCode[0]):
			self.SR(ExCode)
		elif regex(reGraphicLP,ExCode[0]):
			self.LP(ExCode)

		else:
			print str(ExCode)+': Extended Code not parseable!'
			return False

	def ProcessDataBlock(self,DataBlock):
		print 'Process DataBlock: ' + DataBlock
		coord = regex(reCoord,DataBlock)
		dnn = regex(reDnn,DataBlock)
		if coord:
			self.parseCoordinate(coord)
			return True
		elif dnn:
			self.DNN(dnn)
		else:
			print DataBlock+': Could not parse data block!'
			return False

	def Loads(self,s):
		RecordExCode = False
		ExCode = ''
		DataBlock = ''

		for c in s:
			if c == '\n':
				pass
			elif c == '%':
				if RecordExCode:
					self.ProcessExCode(ExCode.split('*')[:-1])
					ExCode = ''
					RecordExCode = False
				else:
					RecordExCode = True
			elif c == '*' and RecordExCode == False:
				self.ProcessDataBlock(DataBlock)
				DataBlock = ''
			elif RecordExCode:
				ExCode = ExCode + c
			else:
				DataBlock = DataBlock + c
	

g = gerber()
# g.parseLn('%TF.FileFunction,Legend,Top*%')
# g.parseLn('%TF.Part,CustomerPanel*%')
# g.parseLn('%TF.MD5,6ab9e892830469cdff7e3e346331d404*%')
# g.parseLn('%TACustomAttr*%')
# g.parseLn('%FSTAX42Y42*%')
# g.parseLn('%MOIN*%')
# g.parseLn('%TA.AperFunction,Other,MySpecialDrill*%')
# g.parseLn('%ADD10C,.025*%')
# g.parseLn('%ADD22R,.050X.050X.027*%')
# g.parseLn('%ADD57O,.030X.040X.015*%')
# g.parseLn('%AMDONUTVAR*1,1,$1,$2,$3*1,0,$4,$2,$3*%')
# g.parseLn('%AMDONUTCAL*1,1,$1,$2,$3*$4=$1x0.75*1,0,$4,$2,$3*%')
# g.parseLn('%ADD15CIRC*%')
# g.parseLn('%SRX3Y2I5.0J4.0*%')
# g.parseLn('%LPD*%')
# g.parseLn('X10000Y10000D01*')
# g.parseLn('X-022Y052I+0335J-0125D02*')
# g.parseLn('X-10000Y-10000D01*')
# g.parseLn('%AMDONUTVAR*')
# g.parseLn('1,1,$1,$2,$3*')
# g.parseLn('1,0,$4,$2,$3*%')
with open('example','r+') as f:
	g.Loads(f.read())
# 	for ln in f:
# 		g.parseLn(ln)

# g.Loads('%TF.Part,CustomerPanel*%\n%MOIN*%\n%FSTAX42Y42*%\n%AMDONUTVAR*\n1,1,$1,$2,$3*\n1,0,$4,$2,$3*%\nX10000Y10000D01*\nX-022Y052I+0335J-0125D02*\nM02*')

print g.Attributes
print g.Graphics

turtle.exitonclick()
