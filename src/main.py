#
# Main app
#

import dearpygui.dearpygui as dpg
import socket

import time
from datetime import datetime

import threading
from pathlib import Path
import os
import yaml


class MainApp:
    def __init__(self, visible_data_patch):
        # data
        self.accel_data_x = []
        self.gyro_data_x = []
        self.PID_data_x = []
        self.setpoint_x = []

        self.accel_data_y = []
        self.gyro_data_y = []
        self.PID_data_y = []
        self.setpoint_y = []

        self.accel_data_z = []
        self.gyro_data_z = []
        self.PID_data_z = []
        self.setpoint_z = []

        self.current_setpoint_x = 0
        self.current_setpoint_y = 0
        self.current_setpoint_z = 0

        self.limit_motor_min = -255.0
        self.limit_motor_max = 255.0

        self.data_x = []

        # app variables
        self.host = "127.0.0.1"
        self.port = 7500
        self.socket_server = None

        self.visible_data_patch = visible_data_patch
        self.time_step = 1

        self.running = False
        self.process = threading.Thread(target=self.update_data)
        self.process.daemon = True
        self.process.start()

        self.connected_to_server = False
        self.current_log_text = ""

    def app_init(self):
        dpg.create_viewport(title='Flyfar fly-test', width=1500, height=1000)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("window", True)
        dpg.start_dearpygui()

    def gui_init(self):
        self.program_path = Path(__file__)
        self.bold_font_path = os.path.join(str(self.program_path.parent), "fonts/OpenSansBold-8wJJ.ttf")

        self.default_font_path = os.path.join(str(self.program_path.parent), "fonts/OpenSansSemibold-wO7w.ttf")

        dpg.create_context()
        with dpg.font_registry():
            self.header_font = dpg.add_font(self.bold_font_path, 30 * 2)
            self.med_header_font = dpg.add_font(self.bold_font_path, 20 * 2)
            self.default_font = dpg.add_font(self.default_font_path, 15 * 2)

        # temp fix for: https://github.com/hoffstadt/DearPyGui/issues/1380
        dpg.set_global_font_scale(0.5)

        with dpg.window(label='Data', tag='window'):
            with dpg.group(horizontal=True):
                with dpg.plot(label='PID X'):
                    # optionally create legend
                    dpg.add_plot_legend()

                    # REQUIRED: create x and y axes, set to auto scale.
                    x_axis = dpg.add_plot_axis(dpg.mvXAxis,
                                               label='x',
                                               tag='x_axis_x')
                    y_axis = dpg.add_plot_axis(dpg.mvYAxis,
                                               label='y',
                                               tag='y_axis_x')

                    # series belong to a y axis. Note the tag name is used in the update
                    # function update_data
                    dpg.add_line_series(x=list(self.data_x),
                                        y=list(self.accel_data_x),
                                        label='Accel data',
                                        parent='y_axis_x',
                                        tag='accel_x')

                    dpg.add_line_series(x=list(self.data_x),
                                        y=list(self.gyro_data_x),
                                        label='Gyro data',
                                        parent='y_axis_x',
                                        tag='gyro_x')

                    dpg.add_line_series(x=list(self.data_x),
                                        y=list(self.PID_data_x),
                                        label='PID data',
                                        parent='y_axis_x',
                                        tag='pid_x')

                    dpg.add_line_series(x=list(self.data_x),
                                        y=list(self.setpoint_x),
                                        label='Setpoint',
                                        parent='y_axis_x',
                                        tag='setpoint_x')

                with dpg.plot(label='PID Y'):
                    # optionally create legend
                    dpg.add_plot_legend()

                    # REQUIRED: create x and y axes, set to auto scale.
                    x_axis = dpg.add_plot_axis(dpg.mvXAxis,
                                               label='x',
                                               tag='x_axis_y')
                    y_axis = dpg.add_plot_axis(dpg.mvYAxis,
                                               label='y',
                                               tag='y_axis_y')

                    # series belong to a y axis.
                    # Note the tag name is used in the update
                    # function update_data
                    dpg.add_line_series(x=list(self.data_x),
                                        y=list(self.accel_data_y),
                                        label='Accel data',
                                        parent='y_axis_y',
                                        tag='accel_y')

                    dpg.add_line_series(x=list(self.data_x),
                                        y=list(self.gyro_data_y),
                                        label='Gyro data',
                                        parent='y_axis_y',
                                        tag='gyro_y')

                    dpg.add_line_series(x=list(self.data_x),
                                        y=list(self.PID_data_y),
                                        label='PID data',
                                        parent='y_axis_y',
                                        tag='pid_y')

                with dpg.plot(label='PID Z'):
                    # optionally create legend
                    dpg.add_plot_legend()

                    # REQUIRED: create x and y axes, set to auto scale.
                    x_axis = dpg.add_plot_axis(dpg.mvXAxis,
                                               label='x',
                                               tag='x_axis_z')
                    y_axis = dpg.add_plot_axis(dpg.mvYAxis,
                                               label='y',
                                               tag='y_axis_z')

                    # series belong to a y axis.
                    # Note the tag name is used in the update
                    # function update_data
                    dpg.add_line_series(x=list(self.data_x),
                                        y=list(self.accel_data_z),
                                        label='Accel data',
                                        parent='y_axis_z',
                                        tag='accel_z')

                    dpg.add_line_series(x=list(self.data_x),
                                        y=list(self.gyro_data_z),
                                        label='Gyro data',
                                        parent='y_axis_z',
                                        tag='gyro_z')

                    dpg.add_line_series(x=list(self.data_x),
                                        y=list(self.PID_data_z),
                                        label='PID data',
                                        parent='y_axis_z',
                                        tag='pid_z')

            self.header_sim = dpg.add_text("Simulation menu:")

            with dpg.group(horizontal=True):
                dpg.add_button(label="Start", callback=self.start)
                dpg.add_button(label="Stop", callback=self.stop)
                dpg.add_button(label="Reset all values", callback=self.reset)

            with dpg.group(horizontal=True, width=125):
                self.input_timeout = dpg.add_input_text(default_value="1")
                dpg.add_button(label="Set receive timeout", callback=self.set_timeout)

            default_p = 15.5
            default_i = 15.5
            default_d = 15.5

            self.header_drone = dpg.add_text("Drone control:")

            self.med_header_pid = dpg.add_text("PID:")
            with dpg.group(horizontal=True, width=300):
                dpg.add_text("P")
                self.input_p = dpg.add_input_text(label="", default_value=default_p)
            with dpg.group(horizontal=True, width=300):
                dpg.add_text("I")
                self.input_i = dpg.add_input_text(label="", default_value=default_i)
            with dpg.group(horizontal=True, width=300):
                dpg.add_text("D")
                self.input_d = dpg.add_input_text(label="", default_value=default_d)
            dpg.add_button(label="Send new PID", callback=self.send_new_pid_data)

            self.med_header_setpoint = dpg.add_text("Setpoints:")
            with dpg.group(horizontal=True, width=300):
                dpg.add_text("Setpoint X")
                self.input_setpoint_x = dpg.add_input_text(default_value="0")
            with dpg.group(horizontal=True, width=300):
                dpg.add_text("Setpoint Y")
                self.input_setpoint_y = dpg.add_input_text(default_value="0")
            with dpg.group(horizontal=True, width=300):
                dpg.add_text("Setpoint Z")
                self.input_setpoint_z = dpg.add_input_text(default_value="0")

            dpg.add_button(label="Send new Setpoint",
                           callback=self.send_new_setpoint)

            self.med_header_limit = dpg.add_text("Limits:")
            with dpg.group(horizontal=True, width=300):
                dpg.add_text("Motor output limit min")
                self.input_limit_motor_min = dpg.add_input_text(
                                    default_value=str(self.limit_motor_min))
            with dpg.group(horizontal=True, width=300):
                dpg.add_text("Motor output limit max")
                self.input_limit_motor_max = dpg.add_input_text(default_value=str(self.limit_motor_max))
            dpg.add_button(label="Send new limits", callback=self.send_new_limit)

            #
            # File dialog
            #
            with dpg.file_dialog(directory_selector=False,
                                 show=False,
                                 callback=self.dialog_callback,
                                 cancel_callback=self.cancel_dialog_callback,
                                 tag="file_dialog",
                                 width=700,
                                 height=400):
                dpg.add_file_extension(".*")
                dpg.add_file_extension(".yml", color=(0, 255, 0, 255))

            self.header_app = dpg.add_text("App menu:")
            self.input_addr = dpg.add_input_text(label="server address", default_value="127.0.0.1", tag="host")
            self.input_port = dpg.add_input_text(label="server port", default_value="7500", tag="port")
            with dpg.group(horizontal=True):
                dpg.add_button(label="Load config.yml", callback=lambda: dpg.show_item("file_dialog"))
                dpg.add_button(label="Connect to server", callback=self.connect_to_server)
                dpg.add_button(label="Disconnect from server", callback=self.disconnect_from_server)

            self.server_status = dpg.add_text("Not connected to server")

            self.header_command_log = dpg.add_text("App logs:")
            self.log_field = dpg.add_input_text(width=800, height=200, multiline=True, readonly=True)

            # bind header font
            dpg.bind_item_font(self.header_app, self.header_font)
            dpg.bind_item_font(self.header_drone, self.header_font)
            dpg.bind_item_font(self.header_sim, self.header_font)
            dpg.bind_item_font(self.header_command_log, self.header_font)

            # bind medium header font
            dpg.bind_item_font(self.med_header_setpoint, self.med_header_font)
            dpg.bind_item_font(self.med_header_pid, self.med_header_font)
            dpg.bind_item_font(self.med_header_limit, self.med_header_font)

            # bind default font
            dpg.bind_font(self.default_font)

    # file dialog
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

    def log(self, text):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%H:%M:%S")

        self.current_log_text += f"[{formatted_time}]: {text}\n"
        dpg.set_value(self.log_field, self.current_log_text)

    def send_to_socket_server(self, message):
        if self.socket_server:
            self.socket_server.send(message.encode("utf-8"))
        else:
            self.log("client: Not connected to server")

    def update_data(self):
        self.iter = 0
        while True:
            if self.running and self.socket_server:
                # Getting data from sensors
                data = self.socket_server.recv(1024).decode()
                data_arr = data.split(",")

                try:
                    y_accel = 0
                    y_gyro = float(data_arr[0])
                    y_PID = float(data_arr[1])
                except ValueError:
                    continue

                self.data_x.append(self.iter)

                # update PID X
                self.setpoint_x.append(self.current_setpoint_x)
                self.accel_data_x.append(y_accel)
                self.gyro_data_x.append(y_gyro)
                self.PID_data_x.append(y_PID)

                # update PID Y
                self.setpoint_y.append(self.current_setpoint_y)

                # update PID Z
                self.setpoint_z.append(self.current_setpoint_z)

                # set values for PID X (TODO, add more values)
                dpg.set_value('accel_x', [
                    self.data_x[-self.visible_data_patch:],
                    self.accel_data_x[-self.visible_data_patch:]])
                dpg.set_value('gyro_x', [
                    self.data_x[-self.visible_data_patch:],
                    self.gyro_data_x[-self.visible_data_patch:]])
                dpg.set_value('pid_x', [
                    self.data_x[-self.visible_data_patch:],
                    self.PID_data_x[-self.visible_data_patch:]])
                dpg.set_value('setpoint_x', [
                    self.data_x[-self.visible_data_patch:],
                    self.setpoint_x[-self.visible_data_patch:]])

                dpg.fit_axis_data('x_axis_x')
                dpg.fit_axis_data('y_axis_x')

                time.sleep(self.time_step)
                self.iter += 1

    #
    # App handlers (etc.)
    #
    def start(self):
        self.running = True

        self.send_to_socket_server("run")

    def stop(self):
        self.running = False

        self.send_to_socket_server("end")

    def set_timeout(self):
        value_time = float(dpg.get_value(self.input_timeout))
        self.time_step = value_time

    def send_new_pid_data(self):
        try:
            value_p = float(dpg.get_value(self.input_p))
            value_i = float(dpg.get_value(self.input_i))
            value_d = float(dpg.get_value(self.input_d))
        except ValueError:
            self.log("client: Invalid value")
            return

        self.send_to_socket_server(f"pid {value_p},{value_i},{value_d}")
        self.log("client: Sent new PID data")

    def send_new_setpoint(self):
        try:
            value_setpoint_x = float(dpg.get_value(self.input_setpoint_x))
            value_setpoint_y = float(dpg.get_value(self.input_setpoint_y))
            value_setpoint_z = float(dpg.get_value(self.input_setpoint_z))

            self.current_setpoint_x = value_setpoint_x
            self.current_setpoint_y = value_setpoint_y
            self.current_setpoint_z = value_setpoint_z
        except ValueError:
            self.log("client: Invalid value")
            return

        self.send_to_socket_server(f"set {value_setpoint_x}")
        # TODO send more setpoints when Andri says so
        self.log("client: Sent new Setpoint data")

    def send_new_limit(self):
        try:
            value_limit_min = float(dpg.get_value(self.input_limit_motor_min))
            self.limit_motor_min = value_limit_min
            value_limit_max = float(dpg.get_value(self.input_limit_motor_max))
            self.limit_motor_max = value_limit_max

            self.send_to_socket_server(f"lim {self.limit_motor_min}, {self.limit_motor_max}")

        except ValueError:
            self.log("client: Invalid value")
            return

    def reset(self):

        self.data_x = []
        self.accel_data_x = []
        self.gyro_data_x = []
        self.PID_data_x = []

        self.iter = 0

        dpg.set_value('accel_x', [self.data_x, self.accel_data_x])
        dpg.set_value('gyro_x', [self.data_x, self.gyro_data_x])
        dpg.set_value('pid_x', [self.data_x, self.PID_data_x])

    def app_exit(self):
        exit(0)

    def connect_to_server(self):
        if not self.connected_to_server:
            self.host = dpg.get_value(self.input_addr)
            self.port = int(dpg.get_value(self.input_port))

            # connect to server
            self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket_server.connect((self.host, self.port))
            except ConnectionRefusedError:
                self.log("client: ERROR: Connection refused")
                return

            dpg.set_value(self.server_status, "Connected to server")
            self.log("client: Connected to server")
            self.connected_to_server = True
        else:
            self.log("client: Already connected to the server")

    def disconnect_from_server(self):
        if self.connected_to_server:
            self.socket_server.close()
            del self.socket_server

            dpg.set_value(self.server_status, "Not connected to server")
            self.log("client: Disconnected from server")
            self.connected_to_server = False
        else:
            self.log("client: Not connected to the server")


def run_app():
    app = MainApp(visible_data_patch=100)
    app.gui_init()
    app.app_init()
    dpg.destroy_context()


if __name__ == "__main__":
    run_app()
