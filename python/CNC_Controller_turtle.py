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
			StandardCircle(aperture['Standard']['C'],event.data.Graphics['CurrentPoint'])
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
	posx = turtle.position()[0]
	posy = turtle.position()[1]
	screenx = screen.screensize()[0]
	screeny = screen.screensize()[1]
	if abs(posx)*2 >= screenx:
		screen.screensize(canvwidth=2*posx+1)
	if abs(posy)*2 >= screeny:
		screen.screensize(canvheight=2*posy+1)

def PrimitiveComment(c):
	print c
	return

def PrimitiveCircle(c,point):
	print 'Draw Circle: '+str(c)
	turtle.penup()
	setExposure(c['Exposure'])
	radius = c['Diameter']/2
	startpoint = {
		'X':c['CenterPoint']['X']+point['X']+radius,
		'Y':c['CenterPoint']['Y']+point['Y']
	}
	goto(startpoint)
	turtle.begin_fill()
	turtle.pendown()
	turtle.circle(radius=scale*radius)
	turtle.penup()
	turtle.end_fill()

def PrimitiveVectorLine(vl,point):
	print 'Draw VectorLine: '+str(vl)
	turtle.penup()
	setExposure(vl['Exposure'])
	turtle.width(scale*vl['Width'])
	startpoint = {
		'X':vl['StartPoint']['X']+point['X'],
		'Y':vl['StartPoint']['Y']+point['Y']
	}
	endpoint = {
		'X':vl['EndPoint']['X']+point['X'],
		'Y':vl['EndPoint']['Y']+point['Y']
	}
	goto(startpoint)
	turtle.begin_fill()
	turtle.pendown()
	goto(endpoint)
	turtle.penup()
	turtle.end_fill()
	return

def PrimitiveCenterLine(cl,point):
	print 'Draw CenterLine: ' + str(cl)
	turtle.penup()
	setExposure(cl['Exposure'])
	turtle.width(1)
	point1 = {
		'X':cl['CenterPoint']['X']-(cl['Width']/2)+point['X'],
		'Y':cl['CenterPoint']['Y']-(cl['Height']/2)+point['Y']
	}
	point2 = {
		'X':cl['CenterPoint']['X']+(cl['Width']/2)+point['X'],
		'Y':cl['CenterPoint']['Y']-(cl['Height']/2)+point['Y']
	}
	point3 = {
		'X':cl['CenterPoint']['X']+(cl['Width']/2)+point['X'],
		'Y':cl['CenterPoint']['Y']+(cl['Height']/2)+point['Y']
	}
	point4 = {
		'X':cl['CenterPoint']['X']-(cl['Width']/2)+point['X'],
		'Y':cl['CenterPoint']['Y']+(cl['Height']/2)+point['Y']
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

def PrimitiveLowerLeftLine(lll,point):
	print 'Draw LowerLeftLine: ' + str(lll)
	turtle.penup()
	setExposure(lll['Exposure'])
	turtle.width(1)
	point1 = {
		'X':lll['LowerLeftPoint']+point['X'],
		'Y':lll['LowerLeftPoint']+point['Y']
		}
	point2 = {
		'X':lll['LowerLeftPoint']['X']+lll['Width']+point['X'],
		'Y':lll['LowerLeftPoint']['Y']+point['Y']
		}
	point3 = {
		'X':lll['LowerLeftPoint']['X']+lll['Width']+point['X'],
		'Y':lll['LowerLeftPoint']['Y']+lll['Height']+point['Y']
		}
	point4 = {
		'X':lll['LowerLeftPoint']['X']+point['X'],
		'Y':lll['LowerLeftPoint']['Y']+lll['Height']+point['Y']
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

def PrimitiveOutline(ol,point):
	print 'Draw Outline: ' + str(ol)
	turtle.penup()
	setExposure(ol['Exposure'])
	turtle.width(1)
	startpoint = {
		'X':ol['Points'][0]['X']+point['X'],
		'Y':ol['Points'][0]['Y']+point['Y']
		}
	goto(startpoint)
	turtle.begin_fill()
	turtle.pendown
	for p in ol['Points']:
		p = {
		'X':p['X']+point['X'],
		'Y':p['Y']+point['Y']
		}
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

def PrimitiveMoire(m,point):
	return

def PrimitiveThermal(t,point):
	return

def StandardCircle(c,point):
	radius = c['Diameter']/2
	startpoint = {
		'X':((turtle.position()[0]/scale)+radius),
		'Y':(turtle.position()[1]/scale)
	}
	goto(startpoint)
	turtle.pendown()
	turtle.circle(radius=scale*radius)

def StandardRectangle(r,point):
	return

def StandardObround(o,point):
	return

def StandardPolygon(poly,point):
	return

dispatcher = GerberReader.EventDispatcher()
g = GerberReader.gerber(dispatcher)
c = Controller(dispatcher)
screen = turtle.Screen()
turtle.mode('logo')
turtle.speed('fastest')
turtle.penup()
with open('../data/G04 Ucamco ex. 2 Shapes','r+') as f:
	g.Loads(f.read())

# print g.Graphics['ApertureMacros']

turtle.exitonclick()