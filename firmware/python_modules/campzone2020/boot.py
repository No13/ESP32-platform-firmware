import machine, sys, system, time, display, touchpads

rtc = machine.RTC()
rtc.write(0,0)
rtc.write(1,0)

touchpads.on(touchpads.HOME, system.home)

try:
	import consts
	with open('cache/version.txt', 'w') as file:
		file.write('{"firmware": %d, "badge_type": "%s"}' %
				   (consts.INFO_FIRMWARE_BUILD, consts.INFO_HARDWARE_WOEZEL_NAME))
except BaseException as e:
	sys.print_exception(e)
	system.crashedWarning()

#### Recovery button combinations ####
try:
	import keypad
	state = keypad.get_state()
	outer_corners = ([True] + [False]*2 + [True] + [False]*8 + [True] + [False]*2 + [True])
	if state == outer_corners:
		import system
		print('Reformatting internal flash storage. This can take a few minutes.')
		system.eraseStorage()
except BaseException as e:
	sys.print_exception(e)
	import system
	system.crashedWarning()

#### Application starting ####

# Default app
app = rtc.read_string()
if not app:
	app = machine.nvs_getstr("system", 'default_app')
	if not app:
		app = 'launcher'

# Override with special boot mode apps if necessary
if machine.nvs_getint('system', 'factory_checked') != 2:
	# Factory check mode
	app = "factory_checks"
elif machine.nvs_getint('system', 'splash_played') != 1:
	# Boot splash screen
	app = "bootsplash"

try:
	import os
	os.mountsd()
	del os
except:
	print('Could not mount SD card')
	pass

if app and not app == "shell":
	try:
		print("Starting app '%s'..." % app)
		system.__current_app__ = app
		if app:
			__import__(app) if not app.endswith('.py') else execfile(app)
	except BaseException as e:
		sys.print_exception(e)
		if not machine.nvs_get_u8("system", "ignore_crash"):
			print("Fatal exception in the running app!")
			system.crashedWarning()
			time.sleep(3)
			system.launcher()
