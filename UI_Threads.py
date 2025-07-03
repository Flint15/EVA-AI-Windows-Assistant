from PyQt5.QtCore import QThread, pyqtSignal, QMutexLocker
import logging
import time
from reorganizer import reorganize_by_extension
import image_processing
from open_exe import open_application
from scaning import scan_for_program
import config

class LLMStreamingThread(QThread):
	"""
	A background thread that handles LLM streaming to prevent UI blocking.
	
	This thread processes LLM responses in chunks and updates the UI through signals.
	The thread can be stopped by calling the stop() method.
	
	Attributes:
		chunk_ready (pyqtSignal): Signal emitted when a new text chunk is ready
		streaming_started (pyqtSignal): Signal emitted when streaming begins
		streaming_finished (pyqtSignal): Signal emitted when streaming completes
	"""
	# UI update signals
	chunk_ready = pyqtSignal(str)
	streaming_started = pyqtSignal()
	streaming_finished = pyqtSignal()

	functions_registry: dict = {
		'opening': open_application,
		'deletion': scan_for_program,
		'reorganization': reorganize_by_extension,
		'image processing': image_processing.grayscaling_image
	}

	def __init__(self,
			     chat_page=None, processed_result: str = '',
				 user_message_type: str = ''
		):
		"""
		Initialize the LLM streaming thread.

		Args:
			chat_page: The UI page to update with streaming chunks
			is_task_case (bool): Whether this is a task case requiring special formatting
			message (str): The message to process through the LLM
		"""
		super().__init__()
		self.chat_page = chat_page
		self.processed_result = processed_result
		self.user_message_type = user_message_type
		self.logger = logging.getLogger(__name__)

		# Connect signals to page methods
		self.chunk_ready.connect(self.chat_page.add_llm_chunk)
		self.streaming_started.connect(self.chat_page.start_llm_streaming)
		self.streaming_finished.connect(self.chat_page.finish_llm_streaming)

		# To track is streaming started ot not
		self.streaming_is_started: bool = False

	def handle_error(self) -> None:
		"""
		Handle errors that occur during LLM streaming.
		
		Args:
			error_details (str): Optional error details to log
		"""

		if not self.streaming_is_started:
			self.streaming_started.emit()
			time.sleep(1)
		
		error_message: str = 'Error occurs, try to send your message again. If it\'s doesn\'t help, idk not send it'

		self.chunk_ready.emit(error_message) 
		time.sleep(1)

		self.streaming_finished.emit()
		self.stop()

	def _llm_request(self, stream_method, message_to_llm: str):
		try:
			for chunk in stream_method(message_to_llm):
				if self.isInterruptionRequested():
					break
				self.chunk_ready.emit(chunk)
		except Exception as e:
			self.logger.error(f'Error occurs while trying to send a request to llm')
			self.handle_error()

	def _long_term_task_execution(self, processed_result):
		task_to_execute = processed_result[0]
		arg = processed_result[1]

		task = self.functions_registry[task_to_execute]
		if task_to_execute == 'deletion':
			task(arg, should_delete=True)
		else:
			task(arg)

		while config.message_to_display == '':
			return 'Everythings is complited!'
		return config.message_to_display

	def run(self) -> None:
		"""
		Main execution method for the thread.
		
		Processes the LLM response in chunks and updates the UI through signals.
		The stream type is determined by is_task_case.
		"""
		self.logger.info('LLM streaming thread started')
		try:
			# Select appropriate stream method based on case type
			try:
				stream_method = (
					self.chat_page.llm.message_formater_stream 
					if self.user_message_type != 'Chatting'
					else self.chat_page.llm.claude_stream
				)
			except Exception as e:
				self.logger.error(f'Error occurs while trying to initialize `stream_method`')
				self.handle_error()

			self.streaming_started.emit()
			self.streaming_is_started = True

			if self.user_message_type == 'Instantanious Task':
				self._llm_request(stream_method, self.processed_result)
			elif self.user_message_type == 'Long-Term Task':
				message_to_llm = self._long_term_task_execution(self.processed_result)
				self._llm_request(stream_method, message_to_llm)
				config.message_to_display = '' # Reset to base state
			else:
				self._llm_request(stream_method, self.processed_result)

			self.streaming_finished.emit()

			self.stop()

		except Exception as e:
			self.logger.error(f'Error in LLM streaming thread: {e}')
		finally:
			self.logger.info('LLM streaming thread finished')
			self.stop()

	def stop(self) -> None:
		"""
		Request the thread to stop by setting the interruption flag.
		
		This method sets the interruption flag, causing the thread to exit
		its loop in the next iteration.
		"""
		self.requestInterruption()

class AlarmMonitorThread(QThread):
	"""
	A background thread that monitors the alarm flag and emits a signal when triggered.

	This thread continuously checks `config.alarm_flag` in a loop. When the flag is `True`,
	it emits the `alarm_triggered` signal and resets the flag to `False`. 
	The thread runs untul interrupted via the `stop()` method, which requests interruption.
	Acces to `config.alarm_flag` is protected by a mutex (`config.alarm_mutex`) to ensure thread safety in a multy-threaded environment.

	Atr:
		alarm_triggered (pyqtSignal): Signal emitted when the alarm flag is detected as True.
	"""
	alarm_triggered = pyqtSignal()

	def __init__(self):
		"""
		Initializes the alarm monitor thread.

		Sets up logging for tracking thread activity and errors. 
		Logging is configured with a basic INFO level
		"""
		super().__init__()
		self.logger = logging.getLogger(__name__)

	def run(self) -> None:
		"""
		Executes the thread's main loop.

		Continuously moitors `config.alarm_flag`. If the flag is `True`,
		emits the `alarm_triggered` signal and resets the flag to `False`.
		Sleeps for 100ms between check.
		The loop exist when interruption is requested via `stop()`.
		Exceptions are caught and logged to prevent thread termination, ensuring robustness.
		"""
		self.logger.info('Alarm monitor thread started')
		while not self.isInterruptionRequested():
			try:
				with QMutexLocker(config.alarm_mutex):
					if config.alarm_flag:
						self.alarm_triggered.emit()
						config.alarm_flag = False
				QThread.msleep(100) # Sleep for 100 milliseconds
			except Exception as e:
				self.logger.error(f'Error in alarm monitor thread: {e}')
		self.logger.info('Alarm monitor thread stopping')

	def stop(self) -> None:
		"""
		Requests the thread to stop.

		Sets the interruption flag, causing the `run()` method's loop to exit in the next iteration.
		The thread stops gracefully after completing its current cycle.
		"""
		self.requestInterruption()

class GrayscalingThreadMonitor(QThread):
	"""
	Check does grayscaling is over or not
	"""
	grayscaling_thread_ended = pyqtSignal()

	def __init__(self):
		super().__init__()
		self.logger = logging.getLogger(__name__)

	def run(self) -> None:
		self.logger.info('Grayscaling Thread is started')
		while not self.isInterruptionRequested():
			try:
				if config.grayscaling_flag:
					self.grayscaling_thread_ended.emit()
					config.grayscaling_flag = False
				QThread.msleep(100)
			except Exception as e: 
				self.logger.error(f'Error in grayscaling monitor thread, error - {e}')
		self.logger.info('Grayscaling Thread is stopped')

	def stop(self) -> None:
		self.requestInterruption()
