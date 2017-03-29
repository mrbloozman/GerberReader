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
		aperture = event.data.Graphics['CurrentAperture']
		if 'C' in aperture['Standard']:
			turtle.width(scale*aperture['Standard']['C']['Diameter'])
		print 'DRAW: ' + str(point)
		turtle.pendown()
		goto(point)
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
		goto(point)
		self.event_dispatcher.dispatch_event(
			GerberReader.OperationEvent ( GerberReader.OperationEvent.ACK, self )
		)

	def on_flash_event(self, event):
		"""
		Event handler for FLASH event type
		"""
		# goto(event.data.Graphics['CurrentPoint'])
		aperture = event.data.Graphics['CurrentAperture']
		if 'C' in aperture['Standard']:
			StandardCircle(aperture['Standard']['C'])
		if 'Primitives' in aperture:
			for p in aperture['Primitives']:
				if 'Comment' in p:
					PrimitiveComment(p['Comment'])
				elif 'Circle' in p:
					PrimitiveCircle(p['Circle'],event.data.Graphics['CurrentPoint'])
				elif 'VectorLine' in p:
					PrimitiveVectorLine(p['VectorLine'],event.data.Graphics['CurrentPoint'])
				elif 'CenterLine' in p:
					PrimitiveCenterLine(p['CenterLine'],event.data.Graphics['CurrentPoint'])
				elif 'LowerLeftLine' in p:
					PrimitiveLowerLeftLine(p['LowerLeftLine'],event.data.Graphics['CurrentPoint'])
				elif 'Outline' in p:
					PrimitiveOutline(p['Outline'],event.data.Graphics['CurrentPoint'])
				elif 'Polygon' in p:
					PrimitivePolygon(p['Polygon'],event.data.Graphics['CurrentPoint'])
				elif 'Moire' in p:
					PrimitiveMoire(p['Moire'],event.data.Graphics['CurrentPoint'])
				elif 'Thermal' in p:
					PrimitiveThermal(p['Thermal'],event.data.Graphics['CurrentPoint'])
		self.event_dispatcher.dispatch_event(
			GerberReader.OperationEvent ( GerberReader.OperationEvent.ACK, self )
		)

	def on_aperture_event(self, event):
		aperture = event.data.Graphics['CurrentAperture']
		# print 'APERTURE: '+ str(aperture)
		# turtle.pen(fillcolor="black", pencolor="black", pensize=int(100*float(aperture['Modifiers'][0])))
		turtle.pen(fillcolor="black", pencolor="black")
		self.event_dispatcher.dispatch_event(
			GerberReader.OperationEvent ( GerberReader.OperationEvent.ACK, self )
		)

def setExposure(exp):
	if exp == 'ON':
		turtle.pen(pencolor='black')
		turtle.color('black')
	elif exp == 'OFF':
		turtle.pen(pencolor='white')
		turtle.color('white')

scale = 200

def goto(point):
	turtle.goto(scale*point['X'],scale*point['Y'])

def PrimitiveComment(c):
	print c
	return

def PrimitiveCircle(c):
	print 'Draw Circle: '+str(c)
	turtle.penup()
	setExposure(c['Exposure'])
	radius = c['Diameter']/2
	startpoint = {
		'X':c['CenterPoint']['X']+radius,
		'Y':c['CenterPoint']['Y']
	}
	goto(startpoint)
	turtle.begin_fill()
	turtle.pendown()
	turtle.circle(radius=scale*radius)
	turtle.penup()
	turtle.end_fill()

def PrimitiveVectorLine(vl):
	print 'Draw VectorLine: '+str(vl)
	turtle.penup()
	setExposure(vl['Exposure'])
	turtle.width(scale*vl['Width'])
	goto(vl['StartPoint'])
	turtle.begin_fill()
	turtle.pendown()
	goto(vl['EndPoint'])
	turtle.penup()
	turtle.end_fill()
	return

def PrimitiveCenterLine(cl):
	print 'Draw CenterLine: ' + str(cl)
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
	print 'Draw LowerLeftLine: ' + str(lll)
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
	print 'Draw Outline: ' + str(ol)
	turtle.penup()
	setExposure(ol['Exposure'])
	turtle.width(1)
	startpoint = ol['Points'][0]
	goto(startpoint)
	turtle.begin_fill()
	turtle.pendown
	for p in ol['Points']:
		goto(p)
	goto(startpoint)
	turtle.penup()
	turtle.end_fill()
	return

def PrimitivePolygon(poly,point):
	print 'Draw Polygon: ' + str(poly)
	turtle.penup()
	setExposure(poly['Exposure'])
	turtle.width(1)
	radius = poly['Diameter']/2
	startpoint = {
		'X':point['X']+radius,
		'Y':point['Y']
	}
	goto(startpoint)
	turtle.begin_fill()
	turtle.pendown()
	turtle.circle(radius=scale*radius,steps=poly['Vertices'])
	turtle.penup()
	turtle.end_fill()
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
turtle.mode('logo')
turtle.speed('fastest')
turtle.penup()
with open('../data/example','r+') as f:
	g.Loads(f.read())

# print g.Graphics['ApertureMacros']

turtle.exitonclick()