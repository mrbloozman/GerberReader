import GerberReader

class Controller( object ):
	"""
	Second class who respond to ASK events
	"""
	def __init__(self, event_dispatcher):
		# Save event dispatcher reference
		self.event_dispatcher = event_dispatcher

		# Listen for ASK event type
		self.event_dispatcher.add_event_listener(
			GerberReader.OperationEvent.DRAW, self.on_draw_event
		)

		self.event_dispatcher.add_event_listener(
			GerberReader.OperationEvent.MOVE, self.on_move_event
		)

		self.event_dispatcher.add_event_listener(
			GerberReader.OperationEvent.FLASH, self.on_flash_event
		)

	def on_draw_event(self, event):
		"""
		Event handler for ASK event type
		"""
		print 'DRAW'
		self.event_dispatcher.dispatch_event(
			GerberReader.OperationEvent ( GerberReader.OperationEvent.ACK, self )
		)

	def on_move_event(self, event):
		"""
		Event handler for ASK event type
		"""
		print 'MOVE'
		self.event_dispatcher.dispatch_event(
			GerberReader.OperationEvent ( GerberReader.OperationEvent.ACK, self )
		)

	def on_flash_event(self, event):
		"""
		Event handler for ASK event type
		"""
		print 'FLASH'
		self.event_dispatcher.dispatch_event(
			GerberReader.OperationEvent ( GerberReader.OperationEvent.ACK, self )
		)

dispatcher = GerberReader.EventDispatcher()
g = GerberReader.gerber(dispatcher)
c = Controller(dispatcher)
with open('../data/example','r+') as f:
	g.Loads(f.read())