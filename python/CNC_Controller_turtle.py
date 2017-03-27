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
			Standard_Circle(aperture['Standard']['C'])
		if 'Primitives' in aperture['Macro']:
			for p in aperture['Macro']['Primitives']:
				if 'Circle' in p:
					Primitive_Circle(p['Circle'])
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
	turtle.penup()
	turtle.goto(scale*point['X'],scale*point['Y'])
	turtle.setheading(0)

def Primitive_Circle(c):
	turtle.penup()
	setExposure(c['exposure'])
	centerpoint = c['centerpoint']
	radius = c['diameter']/2
	goto(centerpoint)
	turtle.pendown()
	turtle.circle(radius=scale*c['diameter']/2)

def Standard_Circle(c):
	radius = c['diameter']/2
	turtle.pendown()
	turtle.circle(radius=scale*radius)

dispatcher = GerberReader.EventDispatcher()
g = GerberReader.gerber(dispatcher)
c = Controller(dispatcher)
with open('../data/example_aperture_macro_primitives','r+') as f:
	g.Loads(f.read())


turtle.exitonclick()