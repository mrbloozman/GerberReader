import GerberReader
import turtle

class Controller( object ):
	"""
	Class who responds to Operation events
	"""
	def __init__(self, event_dispatcher):
		# Save event dispatcher reference
		self.event_dispatcher = event_dispatcher

		# Listen for event types
		self.event_dispatcher.add_event_listener(
			GerberReader.OperationEvent.DRAW, self.on_draw_event
		)

		self.event_dispatcher.add_event_listener(
			GerberReader.OperationEvent.MOVE, self.on_move_event
		)

		self.event_dispatcher.add_event_listener(
			GerberReader.OperationEvent.FLASH, self.on_flash_event
		)

		self.event_dispatcher.add_event_listener(
			GerberReader.OperationEvent.APERTURE, self.on_aperture_event
		)

	def on_draw_event(self, event):
		"""
		Event handler for DRAW event type
		"""
		point = event.data.Graphics['CurrentPoint']
		print 'DRAW: ' + str(point)
		turtle.pendown()
		turtle.goto(point['X'],point['Y'])
		turtle.penup()
		self.event_dispatcher.dispatch_event(
			GerberReader.OperationEvent ( GerberReader.OperationEvent.ACK, self )
		)

	def on_move_event(self, event):
		"""
		Event handler for MOVE event type
		"""
		point = event.data.Graphics['CurrentPoint']
		print 'MOVE: ' + str(point)
		turtle.penup()
		turtle.goto(point['X'],point['Y'])
		self.event_dispatcher.dispatch_event(
			GerberReader.OperationEvent ( GerberReader.OperationEvent.ACK, self )
		)

	def on_flash_event(self, event):
		"""
		Event handler for FLASH event type
		"""
		goto(event.data.Graphics['CurrentPoint'])
		aperture = event.data.Graphics['CurrentAperture']
		if 'C' in aperture['Standard']:
			StandardCircle(aperture['Standard']['C'])
		if 'Primitives' in aperture:
			for p in aperture['Primitives']:
				if 'Circle' in p:
					PrimitiveCircle(p['Circle'])
				elif 'VectorLine' in p:
					PrimitiveVectorLine(p['VectorLine'])
				elif 'CenterLine' in p:
					PrimitiveCenterLine(p['CenterLine'])
				elif 'LowerLeftLine' in p:
					PrimitiveLowerLeftLine(p['LowerLeftLine'])
		self.event_dispatcher.dispatch_event(
			GerberReader.OperationEvent ( GerberReader.OperationEvent.ACK, self )
		)

	def on_aperture_event(self, event):
		aperture = event.data.Graphics['CurrentAperture']
		print 'APERTURE: '+ str(aperture)
		# turtle.pen(fillcolor="black", pencolor="black", pensize=int(100*float(aperture['Modifiers'][0])))
		turtle.pen(fillcolor="black", pencolor="black")
		self.event_dispatcher.dispatch_event(
			GerberReader.OperationEvent ( GerberReader.OperationEvent.ACK, self )
		)

def setExposure(exp):
	if exp == 'ON':
		turtle.pen(pencolor='black')
	elif exp == 'OFF':
		turtle.pen(pencolor='white')

scale = 100

def goto(point):
	turtle.goto(scale*point['X'],scale*point['Y'])

def PrimitiveComment(c):
	return

def PrimitiveCircle(c):
	turtle.mode('logo')
	turtle.penup()
	setExposure(c['Exposure'])
	radius = c['Diameter']/2
	startpoint = {
		'X':c['CenterPoint']['X']+radius,
		'Y':c['CenterPoint']['Y']
	}
	goto(startpoint)
	turtle.pendown()
	turtle.circle(radius=scale*radius)
	turtle.penup()

def PrimitiveVectorLine(vl):
	turtle.penup()
	setExposure(vl['Exposure'])
	turtle.width(scale*vl['Width'])
	goto(vl['StartPoint'])
	turtle.pendown()
	goto(vl['EndPoint'])
	turtle.penup()
	return

def PrimitiveCenterLine(cl):
	turtle.penup()
	setExposure(cl['Exposure'])
	turtle.width(1)
	point1 = {
		'X':cl['CenterPoint']['X']-(cl['Width']/2),
		'Y':cl['CenterPoint']['Y']-(cl['Height']/2)
	}
	point2 = {
		'X':cl['CenterPoint']['X']+(cl['Width']/2),
		'Y':cl['CenterPoint']['Y']-(cl['Height']/2)
	}
	point3 = {
		'X':cl['CenterPoint']['X']+(cl['Width']/2),
		'Y':cl['CenterPoint']['Y']+(cl['Height']/2)
	}
	point4 = {
		'X':cl['CenterPoint']['X']-(cl['Width']/2),
		'Y':cl['CenterPoint']['Y']+(cl['Height']/2)
	}
	goto(point1)
	turtle.begin_fill()
	turtle.pendown()
	goto(point2)
	goto(point3)
	goto(point4)
	goto(point1)
	turtle.penup()
	turtle.end_fill()
	return

def PrimitiveLowerLeftLine(lll):
	turtle.penup()
	setExposure(lll['Exposure'])
	turtle.width(1)
	point1 = lll['LowerLeftPoint']
	point2 = {
		'X':lll['LowerLeftPoint']['X']+lll['Width'],
		'Y':lll['LowerLeftPoint']['Y']
	}
	point3 = {
		'X':lll['LowerLeftPoint']['X']+lll['Width'],
		'Y':lll['LowerLeftPoint']['Y']+lll['Height']
	}
	point4 = {
		'X':lll['LowerLeftPoint']['X'],
		'Y':lll['LowerLeftPoint']['Y']+lll['Height']
	}
	goto(point1)
	turtle.begin_fill()
	turtle.pendown()
	goto(point2)
	goto(point3)
	goto(point4)
	goto(point1)
	turtle.penup()
	turtle.end_fill()
	return

def PrimitiveOutline(ol):
	return

def PrimitivePolygon(poly):
	return

def PrimitiveMoire(m):
	return

def PrimitiveThermal(t):
	return

def StandardCircle(c):
	radius = c['Diameter']/2
	startpoint = {
		'X':((turtle.position()[0]/scale)+radius),
		'Y':(turtle.position()[1]/scale)
	}
	goto(startpoint)
	turtle.pendown()
	turtle.circle(radius=scale*radius)

def StandardRectangle(r):
	return

def StandardObround(o):
	return

def StandardPolygon(poly):
	return

dispatcher = GerberReader.EventDispatcher()
g = GerberReader.gerber(dispatcher)
c = Controller(dispatcher)
with open('../data/example_aperture_macro_primitives','r+') as f:
	g.Loads(f.read())


turtle.exitonclick()