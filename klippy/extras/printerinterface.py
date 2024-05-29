


class AxisEnum:
    X_AXIS = 0
    A_AXIS = 0
    Y_AXIS = 1
    B_AXIS = 1
    Z_AXIS = 2
    C_AXIS = 2
    E_AXIS = 3
    X_HEAD = 4
    Y_HEAD = 5
    Z_HEAD = 6
    E0_AXIS = 3
    E1_AXIS = 4
    E2_AXIS = 5
    E3_AXIS = 6
    E4_AXIS = 7
    E5_AXIS = 8
    E6_AXIS = 9
    E7_AXIS = 10
    ALL_AXES = 0xFE
    NO_AXIS = 0xFF


class HMI_value_t:
    E_Temp = 0
    Bed_Temp = 0
    Fan_speed = 0
    print_speed = 100
    Max_Feedspeed = 0.0
    Max_Acceleration = 0.0
    Max_Jerk = 0.0
    Max_Step = 0.0
    Move_X_scale = 0.0
    Move_Y_scale = 0.0
    Move_Z_scale = 0.0
    Move_E_scale = 0.0
    offset_value = 0.0
    show_mode = 0  # -1: Temperature control    0: Printing temperature


class HMI_Flag_t:
    language = 0
    pause_flag = False
    pause_action = False
    print_finish = False
    done_confirm_flag = False
    select_flag = False
    home_flag = False
    heat_flag = False  # 0: heating done  1: during heating
    ETempTooLow_flag = False
    leveling_offset_flag = False
    feedspeed_axis = AxisEnum()
    acc_axis = AxisEnum()
    jerk_axis = AxisEnum()
    step_axis = AxisEnum()

class xyze_t:
    x = 0.0
    y = 0.0
    z = 0.0
    e = 0.0
    home_x = False
    home_y = False
    home_z = False

    def homing(self):
        self.home_x = False
        self.home_y = False
        self.home_z = False

class buzz_t:
    def tone(self, t, n):
        pass

class material_preset_t:
    def __init__(self, name, hotend_temp, bed_temp, fan_speed=100):
        self.name = name
        self.hotend_temp = hotend_temp
        self.bed_temp = bed_temp
        self.fan_speed = fan_speed

class printerinterface:
    event_loop = None
    HAS_HOTEND = True
    HOTENDS = 1
    HAS_HEATED_BED = True
    HAS_FAN = False
    HAS_ZOFFSET_ITEM = True
    HAS_ONESTEP_LEVELING = True
    HAS_PREHEAT = True
    HAS_BED_PROBE = True
    PREVENT_COLD_EXTRUSION = True
    EXTRUDE_MINTEMP = 170
    EXTRUDE_MAXLENGTH = 200

    HEATER_0_MAXTEMP = 275
    HEATER_0_MINTEMP = 5
    HOTEND_OVERSHOOT = 15

    MAX_E_TEMP = HEATER_0_MAXTEMP - (HOTEND_OVERSHOOT)
    MIN_E_TEMP = HEATER_0_MINTEMP

    BED_OVERSHOOT = 10
    BED_MAXTEMP = 150
    BED_MINTEMP = 5

    BED_MAX_TARGET = BED_MAXTEMP - (BED_OVERSHOOT)
    MIN_BED_TEMP = BED_MINTEMP

    X_MIN_POS = 0.0
    Y_MIN_POS = 0.0
    Z_MIN_POS = 0.0
    Z_MAX_POS = 200

    Z_PROBE_OFFSET_RANGE_MIN = -20
    Z_PROBE_OFFSET_RANGE_MAX = 20

    buzzer = buzz_t()

    BABY_Z_VAR = 0
    feedrate_percentage = 100
    temphot = 0
    tempbed = 0
    HMI_ValueStruct = HMI_value_t()
    HMI_flag = HMI_Flag_t()

    current_position = xyze_t()

    thermalManager = {
        "temp_bed": {"celsius": 20, "target": 120},
        "temp_hotend": [{"celsius": 20, "target": 120}],
        "fan_speed": [100],
    }

    material_preset = [
        material_preset_t("PLA", 200, 60),
        material_preset_t("ABS", 210, 100),
    ]
    files = None
    MACHINE_SIZE = "220x220x250"
    SHORT_BUILD_VERSION = "1.00"
    CORP_WEBSITE_E = "www.klipper3d.org"

    def __init__(self, config):
        self.printer = config.get('printer')
        self.names = []

    def GetFiles(self):
        sdcard = self.printer.lookup_object('virtual_sdcard')
        files = sdcard.get_file_list(True)
        self.names = []
        for file, _ in files:
            self.names.append(file)
        return self.names
    
    def OpenAndPrintFile(self, filenum):
        sdcard = self.printer.lookup_object('virtual_sdcard')
        files = sdcard.cmd_SDCARD_PRINT_FILE(self.names[filenum])

    def SendGCode(self, Gcode):
        gcode = self.printer.lookup_object('gcode')
        gcode._process_commands([Gcode])

    def probe_calibrate(self):
        self.SendGCode('G28') # home the printer
        self.SendGCode('PRTOUCH_PROBE_OFFSET CLEAR_NOZZLE=0 APPLY_Z_ADJUST=1') # use the prtouch to find the z offset and apply it

    def resume_job(self):
        self.SendGCode('RESUME') # resume the print

    def pause_job(self):
        self.SendGCode('PAUSE') # pause the print
        
    def cancel_job(self):
        self.SendGCode('CANCEL_PRINT') # cancel the print

    def set_feedrate(self, value):
        self.SendGCode('M220 S' + str(value)) # set the feedrate through the M220 gcode command

    def moveAbsolute(self, axis, pos, feedrate):
        self.SendGCode('M82') # change to absolute positioning
        self.SendGCode('G1 {}{} F{}'.format(axis, str(pos), str(feedrate))) # move the specified axis at the set feedrate

    def save_settings(self):
        self.SendGCode('SAVE_CONFIG') # save the current configuration changes

    def setExtTemp(self, target):
        self.SendGCode('M104 S' + str(target))

    def setZOffset(self, offset):
        self.SendGCode('SET_GCODE_OFFSET Z={} MOVE=1'.format(str(offset)))

    def add_mm(self, axis, zoffset):
        self.SendGCode('TESTZ Z=' + str(zoffset))

def load_config(config):
    return printerinterface(config)