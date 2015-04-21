# -*- coding: cp1251 -*-
import os
import pprint
import random
import sys
import wx
import matplotlib
matplotlib.use('WXAgg')  # бэкенд WXAgg - совместное использование wx и mpl
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab
from matplotlib import rc # лечим кириллицу в графиках
font = {'family': 'Verdana', 'weight': 'normal'}
rc('font', **font)


class DataGen(object):
    """ A silly class that generates pseudo-random data for
        display in the plot.
    """
    def __init__(self, init=50):
        self.data = self.init = init

    def next(self):
        self._recalc_data()
        return self.data

    def _recalc_data(self):
        delta = random.uniform(-0.5, 0.5)
        r = random.random()

        if r > 0.9:
            self.data += delta * 15
        elif r > 0.8:
            # attraction to the initial value
            delta += (0.5 if self.init > self.data else -0.5)
            self.data += delta
        else:
            self.data += delta


class CompoundBox(wx.Panel):
    """ Блок выбора материала и состава материала (если выбран InGaAsP).
    """
    def __init__(self, parent, ID, label):
        wx.Panel.__init__(self, parent, ID)
        
        #self.value = initval
        
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        self.compounds = [u"InP", u"InAs", u"GaP", u"GaAs", u"InGaAsP"]
        self.materialCombo = wx.ComboBox(self, -1, u"InP", choices=self.compounds, size=(120, -1))
        self.Bind(wx.EVT_COMBOBOX, self.chooseCompound,  self.materialCombo)
        self.compositionLabel = wx.StaticText(self, -1, u"Состав материала:")
        self.compositionEdit = wx.TextCtrl(self, -1, u"0.0", size=(120, -1))
        self.Bind(wx.EVT_TEXT, self.setComposition,  self.compositionEdit)


        # при запуске выбирается InP
        self.compound_checked_id = 0
        self.compound_checked_name = self.compounds[self.compound_checked_id]
        self.composition = 0

        sizer.Add(self.materialCombo, 0, wx.ALL, 3)
        sizer.Add(self.compositionLabel, 0, wx.ALL, 3)
        sizer.Add(self.compositionEdit, 0, wx.ALL, 3)
        #sizer.Add(manual_box, 0, wx.ALL, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)

    def chooseCompound(self, evt):
        self.compound_checked_id = evt.GetSelection()
        self.compound_checked_name = self.compounds[self.compound_checked_id]
        return self.compound_checked_name, self.compound_checked_id

    def setComposition(self, evt):
        self.composition = evt.GetString()


class RefractionBox(wx.Panel):
    """ Блок выбора вкладов в показатель преломления.
    """
    def __init__(self, parent, ID, label):
        wx.Panel.__init__(self, parent, ID)

        self.g_transitions_flag = False
        self.l_transitions_flag = False
        self.x_transitions_flag = False
        self.indirect_transitions_flag = False

        # создаём чекбоксы:
        self.checkbox_g_transitions = wx.CheckBox(self, -1, u"Вклад Г-переходов", style=wx.ALIGN_LEFT)
        self.Bind(wx.EVT_CHECKBOX, self.check_g_transitions, self.checkbox_g_transitions)
        self.checkbox_g_transitions.SetValue(self.g_transitions_flag)

        self.checkbox_l_transitions = wx.CheckBox(self, -1, u"Вклад L-переходов", style=wx.ALIGN_LEFT)
        self.Bind(wx.EVT_CHECKBOX, self.check_l_transitions, self.checkbox_l_transitions)
        self.checkbox_l_transitions.SetValue(self.l_transitions_flag)

        self.checkbox_x_transitions = wx.CheckBox(self, -1, u"Вклад X-переходов", style=wx.ALIGN_LEFT)
        self.Bind(wx.EVT_CHECKBOX, self.check_x_transitions, self.checkbox_x_transitions)
        self.checkbox_x_transitions.SetValue(self.x_transitions_flag)

        self.checkbox_indirect_transitions = wx.CheckBox(self, -1, u"Вклад непрямых переходов", style=wx.ALIGN_LEFT)
        self.Bind(wx.EVT_CHECKBOX, self.check_indirect_transitions, self.checkbox_indirect_transitions)
        self.checkbox_indirect_transitions.SetValue(self.indirect_transitions_flag)

        # создаём кнопки
        self.show_transactions_button = wx.Button(self, -1, u"Показать графики вкладов")
        self.Bind(wx.EVT_BUTTON, self.show_transactions, self.show_transactions_button)

        self.show_refraction_button = wx.Button(self, -1, u"Распределение показателя преломления")
        self.Bind(wx.EVT_BUTTON, self.show_refraction, self.show_refraction_button)

        # работаем с сайзерами
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        grid = wx.GridSizer(2, 2, 0, 0)

        grid.Add(self.checkbox_g_transitions, 0, wx.ALL, 3)
        grid.Add(self.checkbox_l_transitions, 0, wx.ALL, 3)
        grid.Add(self.checkbox_x_transitions, 0, wx.ALL, 3)
        grid.Add(self.checkbox_indirect_transitions, 0, wx.ALL, 3)

        sizer.Add(grid, 0, wx.ALL, 0)
        sizer.Add(self.show_transactions_button, border=3, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)
        sizer.Add(self.show_refraction_button, border=3, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def check_g_transitions(self, evt):
        self.g_transitions_flag = self.checkbox_g_transitions.GetValue()
        print self.g_transitions_flag

    def check_l_transitions(self, evt):
        self.l_transitions_flag = self.checkbox_l_transitions.GetValue()
        print self.l_transitions_flag

    def check_x_transitions(self, evt):
        self.x_transitions_flag = self.checkbox_x_transitions.GetValue()
        print self.x_transitions_flag

    def check_indirect_transitions(self, evt):
        self.indirect_transitions_flag = self.checkbox_indirect_transitions.GetValue()
        print self.indirect_transitions_flag

    def show_transactions(self, evt):
        #todo: разобраться, как учитывать различные вклады
        pass

    def show_refraction(self, evt):
        pass


class MainFrame(wx.Frame):
    """ Основной фрейм приложения
    """
    title = u'Моделирование оптических параметров материалов InGaAsP/InP'
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)

        self.datagen = DataGen()
        self.data = [self.datagen.next()]
        self.paused = False

        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()

        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)
        self.redraw_timer.Start(100)

    def create_menu(self):
        self.menubar = wx.MenuBar()
        
        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, "&Сохранить график\tCtrl-S", "Сохранить график в файл")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "Выход\tCtrl-X", "Выход")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
                
        self.menubar.Append(menu_file, "Файл")
        self.SetMenuBar(self.menubar)

    def create_main_panel(self):
        self.panel = wx.Panel(self)

        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)

        self.compound_control = CompoundBox(self.panel, -1, u'Выбор материала')
        self.refraction_block = RefractionBox(self.panel, -1, u'Показатель преломления')

        self.bandgap_button = wx.Button(self.panel, -1, u"Ширина запрещенной зоны")
        self.Bind(wx.EVT_BUTTON, self.show_bandgap, self.bandgap_button)
        #self.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)
        self.redlambda_button = wx.Button(self.panel, -1, u"Граничная длина волны")
        self.Bind(wx.EVT_BUTTON, self.show_redlambda, self.redlambda_button)

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.bandgap_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(5)
        self.hbox1.Add(self.redlambda_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.compound_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.refraction_block, border=5, flag=wx.ALL)

        # устанавливаем сайзеры
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)        
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)

    def show_bandgap(self, evt):
        pass

    def show_redlambda(self, evt):
        pass

    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((3.0, 3.0), dpi=self.dpi)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_bgcolor('white')

        self.axes.set_title('Very important random data', size=12)
        
        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

        # plot the data as a line series, and save the reference 
        # to the plotted line series
        #
        self.plot_data = self.axes.plot(
            self.data, 
            linewidth=1,
            color=(0, 0, 0),
            )[0]

    def draw_plot(self):
        """ Redraws the plot
        """
        # when xmin is on auto, it "follows" xmax to produce a 
        # sliding window effect. therefore, xmin is assigned after
        # xmax.
        #
        #if self.xmax_control.is_auto():
        xmax = len(self.data) if len(self.data) > 50 else 50
        #else:
        #    xmax = int(self.xmax_control.manual_value())
            
        #if self.xmin_control.is_auto():
        xmin = xmax - 50
        #else:
        #    xmin = int(self.xmin_control.manual_value())

        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        # 
        # note that it's easy to change this scheme to the 
        # minimal/maximal value in the current display, and not
        # the whole data set.
        # 
        #if self.ymin_control.is_auto():
        ymin = round(min(self.data), 0) - 1
        #else:
        #    ymin = int(self.ymin_control.manual_value())
        
        #if self.ymax_control.is_auto():
        ymax = round(max(self.data), 0) + 1
        #else:
        #    ymax = int(self.ymax_control.manual_value())

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)
        
        # anecdote: axes.grid assumes b=True if any other flag is
        # given even if b is set to False.
        # so just passing the flag into the first statement won't
        # work.
        #
        #if self.cb_grid.IsChecked():
        self.axes.grid(True, color='gray')
        #else:
        #    self.axes.grid(False)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly 
        # iterate, and setp already handles this.
        #  
        pylab.setp(self.axes.get_xticklabels(), 
            visible=True)
        
        self.plot_data.set_xdata(np.arange(len(self.data)))
        self.plot_data.set_ydata(np.array(self.data))
        
        self.canvas.draw()
    
    def on_pause_button(self, event):
        self.paused = not self.paused
    
    def on_update_pause_button(self, event):
        label = "Resume" if self.paused else "Pause"
        #self.pause_button.SetLabel(label)
    
    def on_cb_grid(self, event):
        self.draw_plot()
    
    def on_cb_xlab(self, event):
        self.draw_plot()
    
    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)
    
    def on_redraw_timer(self, event):
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)
        #
        if not self.paused:
            self.data.append(self.datagen.next())
        
        self.draw_plot()
    
    def on_exit(self, event):
        self.Destroy()
    
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER, 
            self.on_flash_status_off, 
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')


if __name__ == '__main__':
    app = wx.PySimpleApp()
    app.frame = MainFrame()
    app.frame.Show()
    app.MainLoop()

