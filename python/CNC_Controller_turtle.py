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
			GerberReader.OperationEvent.REGION, self.on_region_event
		)

		self.event_dispatcher.add_event_listener(
			GerberReader.OperationEvent.INTERPOLATION, self.on_interpolation_event
		)

		self.event_dispatcher.add_event_listener(
			GerberReader.OperationEvent.LEVELPOLARITY, self.on_levelpolarity_event
		)

		self.event_dispatcher.add_event_listener(
			GerberReader.OperationEvent.QUADRANT, self.on_quadrant_event
		)

		self.event_dispatcher.add_event_listener(
			GerberReader.OperationEvent.APERTURE, self.on_aperture_event
		)

		self.onColor = 'black'
		self.offColor = 'white'



	def on_region_event(self, event):
		setRegion(event.data.Graphics['RegionMode'])

		self.event_dispatcher.dispatch_event(
			GerberReader.OperationEvent ( GerberReader.OperationEvent.ACK, self )
		)

	def on_interpolation_event(self, event):

		self.event_dispatcher.dispatch_event(
			GerberReader.OperationEvent ( GerberReader.OperationEvent.ACK, self )
		)

	def on_levelpolarity_event(self, event):
		setLevelPolarity(event.data.Graphics['LevelPolarity'])

		self.event_dispatcher.dispatch_event(
			GerberReader.OperationEvent ( GerberReader.OperationEvent.ACK, self )
		)

	def on_quadrant_event(self, event):

		self.event_dispatcher.dispatch_event(
			GerberReader.OperationEvent ( GerberReader.OperationEvent.ACK, self )
		)

	def on_draw_event(self, event):
		"""
		Event handler for DRAW event type
		"""
		point = event.data.Graphics['CurrentPoint']
		aperture = event.data.Graphics['CurrentAperture']
		setLevelPolarity(event.data.Graphics['LevelPolarity'])
		setExposure('ON')
		if 'C' in aperture['Standard']:
			turtle.width(scale*aperture['Standard']['C']['Diameter'])
		else:
			turtle.width(1)
		print 'DRAW: ' + str(point) + ' Interpolation: ' + str(event.data.Graphics['InterpolationMode']) + ' Region: ' + str(event.data.Graphics['RegionMode']) + ' Quadrant: '+ str(event.data.Graphics['QuadrantMode'])
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
		setLevelPolarity(event.data.Graphics['LevelPolarity'])
		aperture = event.data.Graphics['CurrentAperture']
		if 'C' in aperture['Standard']:
			StandardCircle(aperture['Standard']['C'],event.data.Graphics['CurrentPoint'])
		if 'R' in aperture['Standard']:
			StandardRectangle(aperture['Standard']['R'],event.data.Graphics['CurrentPoint'])
		if 'O' in aperture['Standard']:
			StandardObround(aperture['Standard']['O'],event.data.Graphics['CurrentPoint'])
		if 'P' in aperture['Standard']:
			StandardPolygon(aperture['Standard']['P'],event.data.Graphics['CurrentPoint'])
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
		# turtle.pen(fillcolor="black", pencolor="black")
		self.event_dispatcher.dispatch_event(
			GerberReader.OperationEvent ( GerberReader.OperationEvent.ACK, self )
		)

def setRegion(r):
	if r=='ON':
		# if turtle.fill() == False:
		print 'REGION: ' + r
		turtle.begin_fill()
	elif r=='OFF':
		# if turtle.fill() == True:
		print 'REGION: ' + r
		turtle.end_fill()

def setExposure(exp):
	print 'EXPOSURE: '+exp
	if exp == 'ON':
		turtle.color(c.onColor,c.onColor)
	elif exp == 'OFF':
		turtle.color(c.offColor,c.offColor)

def setLevelPolarity(lp):
	if lp == 'DARK':
		print 'LEVELPOLARIY: '+lp
		c.onColor='black'
		c.offColor='white'
		turtle.color(c.onColor,c.onColor)
	elif lp == 'CLEAR':
		print 'LEVELPOLARIY: '+lp
		c.onColor='white'
		c.offColor='black'
		turtle.color(c.onColor,c.onColor)


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
	print 'Draw Circle: '+str(c) + ' at point: '+ str(point)
	setExposure(c['Exposure'])
	radius = c['Diameter']/2.0
	startpoint = {
		'X':c['CenterPoint']['X']+point['X'],
		'Y':c['CenterPoint']['Y']+point['Y']-radius
	}
	print str(startpoint)
	goto(startpoint)
	turtle.begin_fill()
	turtle.pendown()
	turtle.circle(radius=scale*radius)
	turtle.penup()
	turtle.end_fill()

def PrimitiveVectorLine(vl,point):
	print 'Draw VectorLine: '+str(vl)
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
	print 'Draw Moire: '+str(m)
	turtle.width(1)
	radius = m['Diameter']/2.0
	rings = 1

	while (rings < m['MaxRings']) and (radius > 0):
		outerring = {
			'Exposure':'ON',
			'Diameter':radius*2.0,
			'CenterPoint':m['CenterPoint']
		}
		PrimitiveCircle(outerring,point)
		radius = radius - m['RingThickness']
		innerring = {
			'Exposure':'OFF',
			'Diameter':radius*2.0,
			'CenterPoint':m['CenterPoint']
		}
		PrimitiveCircle(innerring,point)
		radius = radius - m['RingGap']

	xhair = {
		'Exposure':'ON',
		'Width':m['CrosshairLength'],
		'Height':m['CrosshairThickness'],
		'CenterPoint':m['CenterPoint'],
		'Angle':0.0
	}
	PrimitiveCenterLine(xhair,point)

	yhair = {
		'Exposure':'ON',
		'Width':m['CrosshairThickness'],
		'Height':m['CrosshairLength'],
		'CenterPoint':m['CenterPoint'],
		'Angle':0.0
	}
	PrimitiveCenterLine(yhair,point)
	return

def PrimitiveThermal(t,point):
	outerring = {
		'Exposure':'ON',
		'Diameter':t['OuterDiameter'],
		'CenterPoint':t['CenterPoint']
	}
	PrimitiveCircle(outerring,point)

	innerring = {
		'Exposure':'OFF',
		'Diameter':t['InnerDiameter'],
		'CenterPoint':t['CenterPoint']
	}
	PrimitiveCircle(innerring,point)

	xhair = {
		'Exposure':'OFF',
		'Width':t['OuterDiameter'],
		'Height':t['GapThickness'],
		'CenterPoint':t['CenterPoint'],
		'Angle':0.0
	}
	PrimitiveCenterLine(xhair,point)

	yhair = {
		'Exposure':'OFF',
		'Width':t['GapThickness'],
		'Height':t['OuterDiameter'],
		'CenterPoint':t['CenterPoint'],
		'Angle':0.0
	}
	PrimitiveCenterLine(yhair,point)
	return

def StandardHole(h,point):
	if len(h)==1:
		hole = {
			'Exposure':'OFF',
			'Diameter':h['Diameter'],
			'CenterPoint':{'X':0.0,'Y':0.0}
		}
		PrimitiveCircle(hole,point)
	elif len(h)==2:
		hole = {
			'Exposure':'OFF',
			'Width':h['XSize'],
			'Height':h['YSize'],
			'CenterPoint':{'X':0.0,'Y':0.0},
			'Angle':0.0
		}
		PrimitiveCenterLine(hole,point)
	return

def StandardCircle(c,point):
	circ = {
		'Exposure':'ON',
		'Diameter':c['Diameter'],
		'CenterPoint':{'X':0.0,'Y':0.0}
	}
	PrimitiveCircle(circ,point)
	StandardHole(c['Hole'],point)
	return

def StandardRectangle(r,point):
	rect = {
		'Exposure':'ON',
		'Width':r['XSize'],
		'Height':r['YSize'],
		'CenterPoint':{'X':0.0,'Y':0.0},
		'Angle':0.0
	}
	PrimitiveCenterLine(rect,point)
	StandardHole(r['Hole'],point)
	return

def StandardObround(o,point):
	if o['XSize']>=o['YSize']:
		dia = o['YSize']
		c1point = {
			'X':-(o['XSize']-dia)/2.0,
			'Y':0.0
			}
		c2point = {
			'X':(o['XSize']-dia)/2.0,
			'Y':0.0
			}
		r = {
			'XSize':o['XSize']-dia,
			'YSize':o['YSize'],
			'Hole':o['Hole']
			}
	else:
		dia = o['XSize']
		c1point = {
			'Y':-(o['YSize']-dia)/2.0,
			'X':0.0
			}
		c2point = {
			'Y':(o['YSize']-dia)/2.0,
			'X':0.0
			}
		r = {
			'XSize':o['XSize'],
			'YSize':o['YSize']-dia,
			'Hole':o['Hole']
			}
	c1 = {
		'Exposure':'ON',
		'Diameter':dia,
		'CenterPoint':c1point
	}
	c2 = {
		'Exposure':'ON',
		'Diameter':dia,
		'CenterPoint':c2point
	}
	PrimitiveCircle(c1,point)
	PrimitiveCircle(c2,point)
	StandardRectangle(r,point)
	return

def StandardPolygon(poly,point):
	return

dispatcher = GerberReader.EventDispatcher()
g = GerberReader.gerber(dispatcher)
c = Controller(dispatcher)
screen = turtle.Screen()
scale = 1
screen.reset()
turtle.setworldcoordinates(-1,-1,5,5)
turtle.mode('world')
turtle.speed('fastest')
turtle.hideturtle()
turtle.penup()
with open('../data/G04 Ucamco ex. 2 Shapes','r+') as f:
	g.Loads(f.read())

# print g.Graphics['ApertureMacros']

turtle.exitonclick()