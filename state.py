from deepmerge.always_merger import merge as deepmerge
from copy import deepcopy
import numpy as np

import led
from config import \
	configurations as available_configurations, \
	visualizations as get_visualizations

handlers = list([])
available_visualizations = dict({})
default_config = parse_config('default')

visualization_state = {
	'enabled': False,
	'current_config': default_config,
	'current_visualization_name': None
}

pixels_state = {
	'enabled': False,
	'color': {'r': 0, 'g': 0, 'b': 0, 'w': 0},
	'brightness': 0,
	'timer': 0
}


# Changer API
# -----------------
def get_visualization_names():
	return available_visualizations.keys()

def get_config_names():
	return available_configurations.keys()

def get_pixels_state():
	return pixels_state

def get_visualization_state():
	return visualization_state

def set_visualization(name):
	if (available_visualizations[name] == None):
		print(f'Visualization with name "{name}" is not available!')
	else:
		visualization_state['current_visualization_name'] = name
		_state_changed()

def set_config(name):
	_parse_config(name)

def enable_static():
	visualization_state['enabled'] = False
	pixels_state['enabled'] = True
	_update_pixels()

def enable_visualization():
	pixels_state['enabled'] = False
	visualization_state['enabled'] = True

def disable_visualization():
	visualization_state['enabled'] = False

def disable_static():
	pixels_state['enabled'] = False
	_update_pixels()

def set_static_brightness(value):
	pixels_state['brightness'] = value
	_update_pixels()

def set_static_color(color):
	pixels_state['color'] = value
	_update_pixels()

# Watcher API
# -----------------
def register_on_state_change_hander(handler):
	handlers.append(handler)

def visualization_enabled():
	return enable_visualization

# Internals
# -----------------
def _update_pixels():
	config = visualization_state['current_config']

	if (pixels_state['enabled'] == False):
		return led.send_pixels(np.zeros((4, config.N_PIXELS)))

	c = pixels_state['color']
	b = pixels_state['brightness'] / 255
	output_led = np.ndarray([
		np.fill(config.N_PIXELS, c['r'] * b, dtype=np.uint8),
		np.fill(config.N_PIXELS, c['g'] * b, dtype=np.uint8),
		np.fill(config.N_PIXELS, c['b'] * b, dtype=np.uint8),
		np.fill(config.N_PIXELS, c['w'] * b, dtype=np.uint8),
	])
	led.send_pixels(output_led)

def _state_changed():	
	current_visualization = available_visualizations[visualization_state['current_visualization_name']]
	for handler in handlers:
		handler(visualization_state['current_config'], current_visualization)

def _parse_config(config_name='default'):
	config = available_configurations[config_name]

	if (config == None):
		print(f'Configuration with name "{config_name}" is not available!')
		return visualization_state['current_config']

	config = deepmerge(deepcopy(default_config), config)

	config.fft_samples_per_window = (config.FFT_WINDOW_LENGTH / 1000) * config.SAMPLE_RATE
	config.target_fft_fps = max(config.FPS_LED, config.FPS_GUI);
	config.fft_samples_per_update = int(config.SAMPLE_RATE / config.target_fft_fps)

	if (config.DEBUG):
	    print(f'Sampling audio at {config.SAMPLE_RATE} Hz.')
	    print(f'Target window of {config.FFT_WINDOW_LENGTH} ms -> {config.fft_samples_per_window} samples per window.')
	    print(f'Theoretical minimum frequency of {(1 / (config.FFT_WINDOW_LENGTH / 1000)):.1F} Hz.')
	    faster_output = 'GUI' if config.FPS_GUI > config.FPS_LED else 'LED'
	    print(f'Target fps of {config.target_fft_fps} Hz for {faster_output}.')

	config.fft_samples_per_window = 2**int(np.ceil(np.log2(config.fft_samples_per_window)))

	if (config.DEBUG):
	    config.fft_window_secs = config.fft_samples_per_window / config.SAMPLE_RATE
	    print(f'Increasing fft window to {config.fft_samples_per_window} samples -> \
	    		{(config.fft_window_secs * 1000):.1F} ms, {(1 / config.fft_window_secs):.1F} Hz')
	    print(f'Using audio period size of {config.fft_samples_per_update} samples.')

	available_visualizations = get_visualizations(config)
	return config