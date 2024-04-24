import dearpygui.dearpygui as dpg
import math
import time
import threading
import numpy as np

class MainApp:
    def __init__(self, visible_data_patch, time_step):
        #data
        self.accel_data_y = []
        self.gyro_data_y = []
        self.PID_data_y = []

        self.data_x = []

        self.visible_data_patch = visible_data_patch
        self.time_step = time_step

        self.running = False
        self.thread = threading.Thread(target=self.update_data)
        self.thread.start()

    def app_init(self):
        dpg.create_viewport(title='Flyfar fly-test', width=1500, height=1000)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("window", True)
        dpg.start_dearpygui()

    def gui_init(self):
        dpg.create_context()
        with dpg.window(label='Data', tag='window'):
            with dpg.plot(label='data', height=500, width=750):
                # optionally create legend
                dpg.add_plot_legend()

                # REQUIRED: create x and y axes, set to auto scale.
                x_axis = dpg.add_plot_axis(dpg.mvXAxis, label='x', tag='x_axis')
                y_axis = dpg.add_plot_axis(dpg.mvYAxis, label='y', tag='y_axis')


                # series belong to a y axis. Note the tag name is used in the update
                # function update_data
                dpg.add_line_series(x=list(self.data_x),y=list(self.accel_data_y), 
                                    label='Accel data', parent='y_axis', 
                                    tag='accel')
                
                dpg.add_line_series(x=list(self.data_x),y=list(self.gyro_data_y), 
                                    label='Gyro data', parent='y_axis', 
                                    tag='gyro')
                
                dpg.add_line_series(x=list(self.data_x),y=list(self.PID_data_y), 
                                    label='PID data', parent='y_axis', 
                                    tag='pid')
                                    
            dpg.add_text("Simulation menu:")
            with dpg.group(horizontal=True):
                dpg.add_button(label="Start", callback=self.start)
                dpg.add_button(label="Stop", callback=self.stop)
                dpg.add_button(label="Reset all values", callback=self.reset)

    def update_data(self):
        self.iter = 0
        while True:
            if self.running:

                #Getting data from sensors TODO
                y_accel = np.random.randint(0, 255)
                y_gyro = np.random.randint(0, 255)
                y_PID = np.random.randint(0, 255)

                self.data_x.append(self.iter)

                self.accel_data_y.append(y_accel)
                self.gyro_data_y.append(y_gyro)
                self.PID_data_y.append(y_PID)
                
                #set the series x and y to the last nsamples
                dpg.set_value('accel', [self.data_x[-self.visible_data_patch:], self.accel_data_y[-self.visible_data_patch:]])
                dpg.set_value('gyro', [self.data_x[-self.visible_data_patch:], self.gyro_data_y[-self.visible_data_patch:]])
                dpg.set_value('pid', [self.data_x[-self.visible_data_patch:], self.PID_data_y[-self.visible_data_patch:]])

                dpg.fit_axis_data('x_axis')
                dpg.fit_axis_data('y_axis')
                
                time.sleep(self.time_step)
                self.iter += 1

    
    #
    # App handlers (etc.)
    #
    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def reset(self):

        self.data_x = []
        self.accel_data_y = []
        self.gyro_data_y = []
        self.PID_data_y = []

        self.iter = 0

        dpg.set_value('accel', [self.data_x, self.accel_data_y])
        dpg.set_value('gyro', [self.data_x, self.gyro_data_y])
        dpg.set_value('pid', [self.data_x, self.PID_data_y])

if __name__ == "__main__":
    app = MainApp(visible_data_patch=100, time_step=0.1)
    app.gui_init()
    app.app_init()
    dpg.destroy_context()