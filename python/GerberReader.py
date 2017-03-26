import re
# import turtle
import sys

# Event Handling
class Event( object ):
	"""
	Generic event to use with EventDispatcher.
	"""

	def __init__(self, event_type, data=None):
		"""
		The constructor accepts an event type as string and a custom data
		"""
		self._type = event_type
		self._data = data

	@property
	def type(self):
		"""
		Returns the event type
		"""
		return self._type

	@property
	def data(self):
		"""
		Returns the data associated to the event
		"""
		return self._data

class EventDispatcher( object ):
	"""
	Generic event dispatcher which listen and dispatch events
	"""

	def __init__(self):
		self._events = dict()

	def __del__(self):
		"""
		Remove all listener references at destruction time
		"""
		self._events = None

	def has_listener(self, event_type, listener):
		"""
		Return true if listener is register to event_type
		"""
		# Check for event type and for the listener
		if event_type in self._events.keys():
			return listener in self._events[ event_type ]
		else:
			return False

	def dispatch_event(self, event):
		"""
		Dispatch an instance of Event class
		"""
		# Dispatch the event to all the associated listeners
		if event.type in self._events.keys():
			listeners = self._events[ event.type ]

			for listener in listeners:
				listener( event )

	def add_event_listener(self, event_type, listener):
		"""
		Add an event listener for an event type
		"""
		# Add listener to the event type
		if not self.has_listener( event_type, listener ):
			listeners = self._events.get( event_type, [] )

			listeners.append( listener )

			self._events[ event_type ] = listeners

	def remove_event_listener(self, event_type, listener):
		"""
		Remove event listener.
		"""
		# Remove the listener from the event type
		if self.has_listener( event_type, listener ):
			listeners = self._events[ event_type ]

			if len( listeners ) == 1:
				# Only this listener remains so remove the key
				del self._events[ event_type ]

			else:
				# Update listeners chain
				listeners.remove( listener )

				self._events[ event_type ] = listeners

class OperationEvent(Event):
	DRAW = 'draw'
	MOVE = 'move'
	FLASH = 'flash'
	APERTURE = 'aperture'
	ACK = 'ack'

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
reGnn = '^G[1-9][0-9]*$'
reG04 = '(?<=G4).*|(?<=G04).*'

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

# Aperture Macro helpers
def EvalVar(var,modifiers):
	for i in range(len(modifiers)):
		var=var.replace('$'+str(i+1),modifiers[i])
	var=var.replace('X','*')
	return float(eval(var))


def EvalMacro(macro,modifiers):
	result = macro
	# Primitive: Code, Name, Modifiers
	for p in result['Primitives']:
		pname = p['Name']
		if pname == primitive[0]:
		# Comment
			p[primitive[0]] = p['Modifiers'][0]
		elif pname == primitive[1]:
		# Circle
			# Exposure
			if p['Modifiers'][0]=='0':
				exp = 'OFF'
			elif p['Modifiers'][0]=='1':
				exp = 'ON'
			else:
				exp = ''
			# Diameter
			dia = EvalVar(p['Modifiers'][1],modifiers)
			# Center X Coord
			x = EvalVar(p['Modifiers'][2],modifiers)
			# Center Y Coord
			y = EvalVar(p['Modifiers'][3],modifiers)
			p[primitive[1]] = {
				'exposure':exp,
				'diameter':dia,
				'centerpoint':{
					'X':x,
					'Y':y
				}
			}

		# Vector Line
		# Center Line
		# Lower Left Line
		# Outline

		elif pname == primitive[5]:
		# Polygon
			# Exposure
			if p['Modifiers'][0]=='0':
				exp = 'OFF'
			elif p['Modifiers'][0]=='1':
				exp = 'ON'
			else:
				exp = ''
			# Vertices
			vert = int(EvalVar(p['Modifiers'][1],modifiers))
			# Center X Coord
			x = EvalVar(p['Modifiers'][2],modifiers)
			# Center Y Coord
			y = EvalVar(p['Modifiers'][3],modifiers)
			# Diameter
			dia = EvalVar(p['Modifiers'][4],modifiers)
			# Rotation Angle
			ang = EvalVar(p['Modifiers'][5],modifiers)
			p[primitive[5]] = {
				'exposure':exp,
				'vertices':vert,
				'centerpoint':{
					'X':x,
					'Y':y
				},
				'diameter':dia,
				'angle':ang
			}
		# Moire
		# Thermal
	return result

class gerber:
	def __init__(self, event_dispatcher):
		# Save a reference to the event dispatch
		self.event_dispatcher = event_dispatcher

		# Listen for the RESPOND event type
		self.event_dispatcher.add_event_listener(
			OperationEvent.ACK, self.on_answer_event
		)

	def on_answer_event(self, event):
		return

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
		'QuadrantMode':'', # SINGLE, MULTI
		'InterpolationMode':'', # LIN, CW, CCW
		'CurrentPoint':{
			'X':0.0,
			'Y':0.0
		},
		'RegionMode':'OFF' # ON, OFF
	}

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
		name = regex(reGraphicAM,am[0])
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
		# turtle.pendown()
		# turtle.goto(x,y)
		# turtle.penup()
		self.Graphics['CurrentPoint']['X'] = x
		self.Graphics['CurrentPoint']['Y'] = y
		# self.Coordinates['I'] = i
		# self.Coordinates['J'] = j
		self.event_dispatcher.dispatch_event(
            OperationEvent( OperationEvent.DRAW, self )
        )
		return

	def D02(self,x,y,i,j):
		# turtle.penup()
		# turtle.goto(x,y)
		self.Graphics['CurrentPoint']['X'] = x
		self.Graphics['CurrentPoint']['Y'] = y
		# self.Coordinates['I'] = i
		# self.Coordinates['J'] = j
		self.event_dispatcher.dispatch_event(
            OperationEvent( OperationEvent.MOVE, self )
        )
		return

	def D03(self,x,y,i,j):
		self.Graphics['CurrentPoint']['X'] = x
		self.Graphics['CurrentPoint']['Y'] = y
		# self.Coordinates['I'] = i
		# self.Coordinates['J'] = j
		self.event_dispatcher.dispatch_event(
            OperationEvent( OperationEvent.FLASH, self )
        )
		return

	def DNN(self,dnn):
		# Event Handler for tool change?
		apertureDefinition = filter(lambda item: item['DCode'] == dnn, self.Graphics['ApertureDefinitions'])[0]
		macro = filter(lambda item: item['Name'] == apertureDefinition['Name'], self.Graphics['ApertureMacros'])[0]
		apertureDefinition['Macro'] = EvalMacro(macro,apertureDefinition['Modifiers'])
		print 'Change aperture to: ' + str(apertureDefinition)
		self.Graphics['CurrentAperture'] = apertureDefinition
		self.event_dispatcher.dispatch_event(
			OperationEvent(OperationEvent.APERTURE, self)
		)
		# turtle.pen(fillcolor="black", pencolor="black", pensize=int(100*float(apertureDefinition['Modifiers'][0])))
		return True

	def GNN(self,gnn):
		if gnn in(['G01','G1']):
			self.Graphics['InterpolationMode'] = 'LIN'
		elif gnn in(['G02','G2']):
			self.Graphics['InterpolationMode'] = 'CW'
		elif gnn in(['G03','G3']):
			self.Graphics['InterpolationMode'] = 'CCW'
		elif gnn == 'G74':
			self.Graphics['QuadrantMode'] = 'SINGLE'
		elif gnn == 'G75':
			self.Graphics['QuadrantMode'] = 'MULTI'
		elif gnn == 'G36':
			self.Graphics['RegionMode'] = 'ON'
		elif gnn == 'G37':
			self.Graphics['RegionMode'] = 'OFF'

	def G04(self,g04):
		print 'Comment: '+g04
		return True

	def M02(self):
		print 'EOF'
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
		gnn = regex(reGnn,DataBlock)
		g04 = regex(reG04,DataBlock)
		if coord:
			self.parseCoordinate(coord)
			return True
		elif dnn:
			self.DNN(dnn)
		elif gnn:
			self.GNN(gnn)
		elif g04:
			self.G04(g04)
		elif DataBlock == 'M02':
			self.M02()
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
	

# g = gerber()

# with open('../data/example','r+') as f:
# 	g.Loads(f.read())

# print g.Attributes
# print g.Graphics

# turtle.exitonclick()
