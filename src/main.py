#
# Main app
#

import dearpygui.dearpygui as dpg
import socket
import time
import threading
from pathlib import Path
import os
import yaml

class MainApp:
    def __init__(self, visible_data_patch, time_step):
        #data
        self.accel_data_y = []
        self.gyro_data_y = []
        self.PID_data_y = []

        self.data_x = []

        #app variables
        self.host = "127.0.0.1"
        self.port = 7500

        self.visible_data_patch = visible_data_patch
        self.time_step = time_step

        #set logger
        self.verbose = verbose
        self.logger = logger

        self.running = False
        self.process = threading.Thread(target=self.update_data)
        self.process.daemon = True
        self.process.start()

    def app_init(self):
        dpg.create_viewport(title='Flyfar fly-test', width=1500, height=1000)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("window", True)
        #dpg.set_exit_callback(self.app_exit)
        dpg.start_dearpygui()

    def gui_init(self):
        self.program_path = Path(__file__)
        self.bold_font_path = os.path.join(str(self.program_path.parent), "fonts/OpenSansBold-8wJJ.ttf")
        self.default_font_path = os.path.join(str(self.program_path.parent), "fonts/OpenSansSemibold-wO7w.ttf")

        dpg.create_context()
        with dpg.font_registry():
            self.header_font = dpg.add_font(self.bold_font_path, 20)
            self.default_font = dpg.add_font(self.default_font_path, 15)

        with dpg.window(label='Data', tag='window'):
            with dpg.group(horizontal=True):
                with dpg.plot(label='PID X'):
                    # optionally create legend
                    dpg.add_plot_legend()

                    # REQUIRED: create x and y axes, set to auto scale.
                    x_axis = dpg.add_plot_axis(dpg.mvXAxis, label='x', tag='x_axis_x')
                    y_axis = dpg.add_plot_axis(dpg.mvYAxis, label='y', tag='y_axis_x')


                    # series belong to a y axis. Note the tag name is used in the update
                    # function update_data
                    dpg.add_line_series(x=list(self.data_x),y=list(self.accel_data_y), 
                                        label='Accel data', parent='y_axis_x', 
                                        tag='accel_x')
                    
                    dpg.add_line_series(x=list(self.data_x),y=list(self.gyro_data_y), 
                                        label='Gyro data', parent='y_axis_x', 
                                        tag='gyro_x')
                    
                    dpg.add_line_series(x=list(self.data_x),y=list(self.PID_data_y), 
                                        label='PID data', parent='y_axis_x', 
                                        tag='pid_x')
                    
                with dpg.plot(label='PID Y'):
                    # optionally create legend
                    dpg.add_plot_legend()

                    # REQUIRED: create x and y axes, set to auto scale.
                    x_axis = dpg.add_plot_axis(dpg.mvXAxis, label='x', tag='x_axis_y')
                    y_axis = dpg.add_plot_axis(dpg.mvYAxis, label='y', tag='y_axis_y')


                    # series belong to a y axis. Note the tag name is used in the update
                    # function update_data
                    dpg.add_line_series(x=list(self.data_x),y=list(self.accel_data_y), 
                                        label='Accel data', parent='y_axis_y', 
                                        tag='accel_y')
                    
                    dpg.add_line_series(x=list(self.data_x),y=list(self.gyro_data_y), 
                                        label='Gyro data', parent='y_axis_y', 
                                        tag='gyro_y')
                    
                    dpg.add_line_series(x=list(self.data_x),y=list(self.PID_data_y), 
                                        label='PID data', parent='y_axis_y', 
                                        tag='pid_y')
            
                with dpg.plot(label='PID Z'):
                        # optionally create legend
                        dpg.add_plot_legend()

                        # REQUIRED: create x and y axes, set to auto scale.
                        x_axis = dpg.add_plot_axis(dpg.mvXAxis, label='x', tag='x_axis_z')
                        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label='y', tag='y_axis_z')


                        # series belong to a y axis. Note the tag name is used in the update
                        # function update_data
                        dpg.add_line_series(x=list(self.data_x),y=list(self.accel_data_y), 
                                            label='Accel data', parent='y_axis_z', 
                                            tag='accel_z')
                        
                        dpg.add_line_series(x=list(self.data_x),y=list(self.gyro_data_y), 
                                            label='Gyro data', parent='y_axis_z', 
                                            tag='gyro_z')
                        
                        dpg.add_line_series(x=list(self.data_x),y=list(self.PID_data_y), 
                                            label='PID data', parent='y_axis_z', 
                                            tag='pid_z')
                                    
            self.header_sim = dpg.add_text("Simulation menu:")


            with dpg.group(horizontal=True):
                dpg.add_button(label="Start", callback=self.start)
                dpg.add_button(label="Stop", callback=self.stop)
                dpg.add_button(label="Reset all values", callback=self.reset)

            default_p = 15.5
            default_i = 15.5
            default_d = 15.5

            self.header_drone = dpg.add_text("Drone control:")
            self.input_p = dpg.add_input_text(label="P", default_value=default_p)
            self.input_i = dpg.add_input_text(label="I", default_value=default_i)
            self.input_d = dpg.add_input_text(label="D", default_value=default_d)
            dpg.add_button(label="Send new PID", callback=self.send_new_pid_data)

            with dpg.group(horizontal=True, width=300):
                dpg.add_text("Setpoint X")
                self.input_setpoint_x = dpg.add_input_text(label="")

            with dpg.group(horizontal=True, width=300):
                dpg.add_text("Setpoint Y")
                self.input_setpoint_y = dpg.add_input_text(label="")

            with dpg.group(horizontal=True, width=300):
                dpg.add_text("Setpoint Z")
                self.input_setpoint_z = dpg.add_input_text(label="")

            dpg.add_button(label="Send new Setpoint", callback=self.send_new_setpoint)

            #file dialog
            with dpg.file_dialog(directory_selector=False, show=False, callback=self.dialog_callback, cancel_callback=self.cancel_dialog_callback, tag="file_dialog", width=700 ,height=400):
                dpg.add_file_extension(".*")
                dpg.add_file_extension(".yml", color=(0, 255, 0, 255))


            self.header_app = dpg.add_text("App menu:")
            self.input_addr = dpg.add_input_text(label="server address", default_value="127.0.0.1", tag="host")
            self.input_port = dpg.add_input_text(label="server port", default_value="7500", tag="port")
            with dpg.group(horizontal=True):
                dpg.add_button(label="Load config.yml", callback=lambda: dpg.show_item("file_dialog"))
                dpg.add_button(label="Connect to server", callback=self.connect_to_server)
            
            self.server_status = dpg.add_text("Not connected to server")

            #bind every header to header font
            dpg.bind_item_font(self.header_app, self.header_font)
            dpg.bind_item_font(self.header_drone, self.header_font)
            dpg.bind_item_font(self.header_sim, self.header_font)

            #bind default font
            dpg.bind_font(self.default_font)

    #file dialog
    def dialog_callback(sender, app_data, user_data):
        selected_path = list(user_data["selections"].values())[0]
        contents = None
        with open(selected_path) as stream:
            try:
                contents = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                return
        
        host = contents["host"]
        port = contents["port"]

        dpg.set_value("host", host)
        dpg.set_value("port", port)

    def cancel_dialog_callback(sender, app_data):
        print('Cancel was clicked.')
        print("Sender: ", sender)
        print("App Data: ", app_data)

    def update_data(self):
        self.iter = 0
        while True:
            if self.running:

                #Getting data from sensors
                data = self.socket_server.recv(1024).decode()
                print(data)
                data_arr = data.split(",")
                
                try:
                    y_accel = 0
                    y_gyro = float(data_arr[0])
                    y_PID = float(data_arr[1])


                except ValueError:
                    continue
                
                self.data_x.append(self.iter)

                self.accel_data_y.append(y_accel)
                self.gyro_data_y.append(y_gyro)
                self.PID_data_y.append(y_PID)

                #set values for PID X (TODO)
                dpg.set_value('accel_x', [self.data_x[-self.visible_data_patch:], self.accel_data_y[-self.visible_data_patch:]])
                dpg.set_value('gyro_x', [self.data_x[-self.visible_data_patch:], self.gyro_data_y[-self.visible_data_patch:]])
                dpg.set_value('pid_x', [self.data_x[-self.visible_data_patch:], self.PID_data_y[-self.visible_data_patch:]])

                dpg.fit_axis_data('x_axis_x')
                dpg.fit_axis_data('y_axis_x')
                
                time.sleep(self.time_step)
                self.iter += 1

    
    #
    # App handlers (etc.)
    #
    def start(self):
        self.running = True

        self.socket_server.send(b"run")

    def stop(self):
        self.running = False

        self.socket_server.send(b"end")

    def send_new_pid_data(self):
        value_p = float(dpg.get_value(self.input_p))
        value_i = float(dpg.get_value(self.input_i))
        value_d = float(dpg.get_value(self.input_d))

        self.socket_server.send(f"pid {value_p},{value_i},{value_d}".encode())

    def send_new_setpoint(self):
        value_setpoint_x = float(dpg.get_value(self.input_setpoint_x))
        value_setpoint_y = float(dpg.get_value(self.input_setpoint_y))
        value_setpoint_z = float(dpg.get_value(self.input_setpoint_z))

        self.socket_server.send(f"set {value_setpoint_x}".encode())

    def reset(self):

        self.data_x = []
        self.accel_data_y = []
        self.gyro_data_y = []
        self.PID_data_y = []

        self.iter = 0

        dpg.set_value('accel_x', [self.data_x, self.accel_data_y])
        dpg.set_value('gyro_x', [self.data_x, self.gyro_data_y])
        dpg.set_value('pid_x', [self.data_x, self.PID_data_y])

    def app_exit(self):
        exit(0)
    
    def connect_to_server(self):
        self.host = dpg.get_value(self.input_addr)
        self.port = int(dpg.get_value(self.input_port))

        print(self.host)
        print(self.port)

        #connect to server
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_server.connect((self.host, self.port))

        dpg.set_value(self.server_status, "Connected to server")

def run_app(logger, verbose = False):
    app = MainApp(visible_data_patch=100, time_step=0.1)
    app.gui_init()
    app.app_init()
    dpg.destroy_context()

if __name__ == "__main__":
    run_app()