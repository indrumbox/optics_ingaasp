# -*- coding: cp1251 -*-
import os
import pprint
import random
import sys
import wx
import matplotlib
import dsci
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


class ModifiedSpinControl(wx.Panel):
    def __init__(self, parent, ID, label, init_value):
        wx.Panel.__init__(self, parent, -1)

        self.label = wx.StaticText(self, -1, label)
        self.text = wx.TextCtrl(self, -1, str(init_value), size=(45, -1)) # (30, 50), (60, -1)
        h = self.text.GetSize().height + self.text.GetPosition().y
        w = self.text.GetSize().width + self.text.GetPosition().x + 1

        self.spin = wx.SpinButton(self, -1,
                                  (w, self.text.GetPosition().y),
                                  (h, h),
                                  wx.SP_VERTICAL)
        self.spin.SetRange(-100, 100)
        self.spin.SetValue(init_value)

        self.Bind(wx.EVT_SPIN_UP, self.OnSpinUp, self.spin)
        self.Bind(wx.EVT_SPIN_DOWN, self.OnSpinDn, self.spin)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.label, 0, wx.ALL | wx.CENTER, 1)
        sizer.Add(self.text, 0, wx.ALL | wx.CENTER, 1)
        sizer.Add(self.spin, 0, wx.ALL | wx.CENTER, 1)
        self.SetSizer(sizer)
        sizer.Fit(self)

    def OnSpinUp(self, event):
        current_value = float(self.text.GetValue())
        next_value = current_value+0.01
        self.text.SetValue(str(next_value))

    def OnSpinDn(self, event):
        current_value = float(self.text.GetValue())
        next_value = current_value-0.01
        self.text.SetValue(str(next_value))


class SpinSection(wx.Panel):
    def __init__(self, parent, ID, label, xmin=0., xmax=0., ymin=0., ymax=0.):
        wx.Panel.__init__(self, parent, ID)
        box = wx.StaticBox(self, -1, label)

        self.xmin = ModifiedSpinControl(self, -1, u"xmin: ", xmin)
        self.xmax = ModifiedSpinControl(self, -1, u"xmax: ", xmax)
        self.ymin = ModifiedSpinControl(self, -1, u"ymin: ", ymin)
        self.ymax = ModifiedSpinControl(self, -1, u"ymax: ", ymax)

        self.cb_fixed = wx.CheckBox(self, -1, u"фиксированные", style=wx.ALIGN_RIGHT)
        #self.Bind(wx.EVT_CHECKBOX, self.on_cb_fixed, self.cb_fixed)
        self.cb_fixed.SetValue(False)

        self.apply_button = wx.Button(self, -1, u"Применить")

        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        sizer.Add(self.xmin, 0, wx.ALL, 3)
        sizer.Add(self.xmax, 0, wx.ALL, 3)
        sizer.Add(self.ymin, 0, wx.ALL, 3)
        sizer.Add(self.ymax, 0, wx.ALL, 3)
        sizer.Add(self.cb_fixed, 0, wx.ALL, 3)
        sizer.Add(self.apply_button, 0, wx.ALL, 3)
        self.SetSizer(sizer)
        sizer.Fit(self)

    def set_values(self, data):
        # устанавливаем значения границ в едитах
        x_values = list(data.get_xdata())
        y_values = list(data.get_ydata())
        x_min_value = round(min(x_values), 2)
        x_max_value = round(max(x_values), 2)
        y_min_value = round(min(y_values), 2)
        y_max_value = round(max(y_values), 2)
        self.xmin.text.SetValue(str(x_min_value))
        self.xmax.text.SetValue(str(x_max_value))
        self.ymin.text.SetValue(str(y_min_value))
        self.ymax.text.SetValue(str(y_max_value))

    def fixed_plot(self):
        return self.cb_fixed.GetValue()


class CompoundBox(wx.Panel):
    """ Блок выбора материала и состава материала (если выбран InGaAsP).
    """
    def __init__(self, parent, ID, label):
        wx.Panel.__init__(self, parent, ID)
        
        #self.value = initval
        
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        self.compounds = [u"InP", u"InAs", u"GaP", u"GaAs", u"InGaAsP"]
        self.materialCombo = wx.ComboBox(self, -1, u"", choices=self.compounds, size=(120, -1))
        self.materialCombo.SetSelection(4)
        self.Bind(wx.EVT_COMBOBOX, self.chooseCompound,  self.materialCombo)
        self.compositionLabel = wx.StaticText(self, -1, u"Состав материала:")

        self.x_compositionLabel = wx.StaticText(self, -1, u"X:")
        self.x_compositionEdit = wx.TextCtrl(self, -1, u"0.0", size=(40, -1))
        self.Bind(wx.EVT_TEXT, self.setXComposition,  self.x_compositionEdit)
        self.y_compositionLabel = wx.StaticText(self, -1, u"Y:")
        self.y_compositionEdit = wx.TextCtrl(self, -1, u"0.0", size=(40, -1))
        self.Bind(wx.EVT_TEXT, self.setYComposition,  self.y_compositionEdit)


        # при запуске выбирается InP
        self.compound_checked_id = 0
        self.compound_checked_name = self.compounds[self.compound_checked_id]
        self.composition = 0

        self.compo_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.compo_sizer.Add(self.x_compositionLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.compo_sizer.Add(self.x_compositionEdit, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.compo_sizer.Add(self.y_compositionLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.compo_sizer.Add(self.y_compositionEdit, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        sizer.Add(self.materialCombo, 0, wx.ALL, 3)
        sizer.Add(self.compositionLabel, 0, wx.ALL, 3)
        #sizer.Add(self.compositionEdit, 0, wx.ALL, 3)
        sizer.Add(self.compo_sizer, 0, wx.ALL, 3)
        #sizer.Add(manual_box, 0, wx.ALL, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)

    def chooseCompound(self, evt):
        self.compound_checked_id = evt.GetSelection()
        self.compound_checked_name = self.compounds[self.compound_checked_id]
        if self.compound_checked_name == "InGaAsP":
            pass
            self.x_compositionEdit.Enable()
            self.y_compositionEdit.Enable()
        else:
            self.x_compositionEdit.Disable()
            self.y_compositionEdit.Disable()
        return self.compound_checked_name, self.compound_checked_id

    def setYComposition(self, evt):
        self.y_composition = evt.GetString()
        print self.y_composition

    def setXComposition(self, evt):
        self.x_composition = evt.GetString()
        print self.x_composition

    def getCompound(self):
        return [float(self.x_compositionEdit.Value), float(self.y_compositionEdit.Value)]


class SellmeierBox(wx.Panel):
    """ Блок моделирования зависимости Селлмейера для материалов InP и InGaAsP/InP.
    """
    def __init__(self, parent, ID, label):
        wx.Panel.__init__(self, parent, ID)

        box = wx.StaticBox(self, -1, label)
        self.compositionLabel = wx.StaticText(self, -1, u"Состав материала:")
        self.compositionEdit = wx.TextCtrl(self, -1, u"0.0", size=(90, -1))
        self.Bind(wx.EVT_TEXT, self.setComposition,  self.compositionEdit)
        self.composition = 0.

        self.on_wave = wx.RadioButton(self, -1, u'По длине волны', style=wx.RB_GROUP)
        self.on_energy = wx.RadioButton(self, -1, u'По энергии')

        composition_sizer = wx.BoxSizer(wx.HORIZONTAL)
        composition_sizer.Add(self.compositionLabel, 0, wx.ALL | wx.CENTER, 1)
        composition_sizer.Add(self.compositionEdit, 0, wx.ALL | wx.CENTER, 1)

        radio_sizer = wx.BoxSizer(wx.HORIZONTAL)
        radio_sizer.Add(self.on_wave, 0, wx.ALL, 1)
        radio_sizer.Add(self.on_energy, 0, wx.ALL, 1)

        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer.Add(composition_sizer, 0, wx.ALL, 3)
        sizer.Add(radio_sizer, 0, wx.ALL, 3)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def push_sellmeier_data(self):
        # отрисовка графика зависимости
        compound = dsci.Structure(dsci.x_on_InP(self.composition), self.composition)

        if self.lambda_checked():
            # выбрана реализация по длине волны
            x_pack = compound.get_lambdas()
        else:
            # выбрана отрисовка по энергии
            x_pack = compound.get_energies()
        y_pack = compound.get_sellmeier_pack()
        return x_pack, y_pack


    def lambda_checked(self):
        return self.on_wave.GetValue()

    def setComposition(self, evt):
        self.composition = float(evt.GetString())


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

    def show_refraction(self, evt):
        pass


class MainFrame(wx.Frame):
    """ Основной фрейм приложения
    """
    title = u'Моделирование оптических параметров материалов InGaAsP/InP'
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)

        self.data = [0, 1, 3, 1]
        self.structure_data = dsci.Structure(0., 0.)

        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()

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
        self.sellmeier_block = SellmeierBox(self.panel, -1, u'Зависимость Селлмейера')
        self.spinsection = SpinSection(self.panel, -1, u'')

        self.bandgap_button = wx.Button(self.panel, -1, u"Ширина запрещенной зоны")
        self.Bind(wx.EVT_BUTTON, self.show_bandgap, self.bandgap_button)
        #self.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)
        self.redlambda_button = wx.Button(self.panel, -1, u"Граничная длина волны")
        self.Bind(wx.EVT_BUTTON, self.show_redlambda, self.redlambda_button)
        self.calculate_sellmeier_button = wx.Button(self.panel, -1, u"Зависимость Селлмейера")
        self.Bind(wx.EVT_BUTTON, self.show_sellmeier, self.calculate_sellmeier_button)
        self.Bind(wx.EVT_BUTTON, self.refresh_plot, self.spinsection.apply_button)

        self.Bind(wx.EVT_BUTTON, self.show_transactions, self.refraction_block.show_transactions_button)


        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.bandgap_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(5)
        self.hbox1.Add(self.redlambda_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(5)
        self.hbox1.Add(self.calculate_sellmeier_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.compound_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.refraction_block, border=5, flag=wx.ALL)
        self.hbox2.Add(self.sellmeier_block, border=5, flag=wx.ALL)
        self.hbox2.Add(self.spinsection, border=5, flag=wx.ALL)

        # устанавливаем сайзеры
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)        
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)

    def show_bandgap(self, evt):
        compositions_y = np.arange(0, 1, 0.01)
        Eg_pack = [dsci.Eg_on_InP(dsci.x_on_InP(y), y) for y in compositions_y]
        Eg_transformed = np.array(Eg_pack)
        x_label = u"Состав "+r"$y$"+u" соединения "+r"$In_{1-x}Ga_{x}As_{y}P_{1-y}/InP$"
        y_label = u"Ширина запрещенной зоны, эВ"
        main_label = u"Ширина запрещенной зоны"

        self.draw_plot(compositions_y, Eg_transformed, title_main=main_label,
                       title_y=y_label, title_x=x_label)

    def show_redlambda(self, evt):
        compositions_y = np.arange(0, 1, 0.01)
        lambda_pack = [dsci.lambda_red_on_inp(dsci.x_on_InP(y), y) for y in compositions_y]
        lambda_pack_transformed = np.array(lambda_pack)
        x_label = u"Состав "+r"$y$"+u" соединения "+r"$In_{1-x}Ga_{x}As_{y}P_{1-y}/InP$"
        y_label = u"Граничная длина волны, мкм"
        main_label = u"Граничная длина волны"

        self.draw_plot(compositions_y, lambda_pack_transformed, title_main=main_label,
                       title_y=y_label, title_x=x_label)

    def show_sellmeier(self, evt):
        x_pack, y_pack = self.sellmeier_block.push_sellmeier_data()
        y_label = u"Показатель преломления"
        main_label = u"Модель показателя преломления (зависимость Селлмейера)"
        if self.sellmeier_block.lambda_checked():
            x_label = u"Длина волны, мкм"
        else:
            x_label = u"Энергия излучения, эВ"
        self.draw_plot(x_pack, y_pack, title_main=main_label, title_y=y_label, title_x=x_label)

    def show_transactions(self, evt):
        [x_, y_] = self.compound_control.getCompound()
        # создаём структуру с заданными значениями x и y
        compound = dsci.Structure(x_, y_)
        # у структуры заполнены все данные и можно рассчитать любые вклады по функциям
        # допустим, пока показываются графики только по длине волны .get_lambdas()

        y_label = u"Диэлектрическая постоянная"
        main_label = u"Модель диэлектрической проницаемости"

        # todo: пока немного дурная реализация, вынести в отдельный блок чекбоксы
        if self.sellmeier_block.lambda_checked():
            # выбрана реализация по длине волны
            x_pack = compound.get_lambdas()
            x_label = u"Длина волны, мкм"
        else:
            # выбрана отрисовка по энергии
            x_pack = compound.get_energies()
            x_label = u"Энергия излучения, эВ"

        # сначала показываем вклады в диэлектрическую проницаемость
        # y_pack = compound.get_epsilon_g_pack()
        # self.draw_plot(x_pack, y_pack, selected_plot=self.plot_data_g, title_main=main_label, title_y=y_label, title_x=x_label)
        # y_pack = compound.get_epsilon_l_pack()
        # self.draw_plot(x_pack, y_pack, selected_plot=self.plot_data_l, title_main=main_label, title_y=y_label, title_x=x_label)
        # y_pack = compound.get_epsilon_x_pack()
        # self.draw_plot(x_pack, y_pack, selected_plot=self.plot_data_x, title_main=main_label, title_y=y_label, title_x=x_label)
        # потом всё целиком - диэлектрическая проницаемость
        #y_pack = compound.get_full_epsilon_pack()

        # а вот и отрисовка показателя преломления!
        # todo: разобраться, почему получаются столь низкие значения показателя преломления (должны быть больше трёх)
        y_pack = compound.get_refraction_pack()
        #y_pack = compound.get_absorption_pack()
        #y_pack = compound.get_extinction_pack()
        self.draw_plot(x_pack, y_pack, title_main=main_label, title_y=y_label, title_x=x_label)


    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((3.0, 3.0), dpi=self.dpi)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_bgcolor('white')

        self.axes.set_title('', size=12)
        
        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

        self.axes.grid(True, color='gray')
        self.plot_data = self.axes.plot([0], linewidth=1, color=(0, 0, 0))[0]
        self.plot_data_g = self.axes.plot([0], linewidth=1, color='r')[0]
        self.plot_data_l = self.axes.plot([0], linewidth=1, color='g')[0]
        self.plot_data_x = self.axes.plot([0], linewidth=1, color='b')[0]

        pylab.setp(self.axes.get_xticklabels(), visible=True)

    def draw_plot(self, x_arr, y_arr, selected_plot="default", title_main="", title_x="", title_y=""):
        if selected_plot == "default":
            selected_plot = self.plot_data
        selected_plot.set_xdata(np.array(x_arr))
        selected_plot.set_ydata(np.array(y_arr))

        self.axes.set_xbound(lower=min(x_arr), upper=max(x_arr))
        self.axes.set_ybound(lower=min(y_arr), upper=max(y_arr))
        self.axes.set_title(title_main, size=12)
        self.axes.set_xlabel(title_x)
        self.axes.set_ylabel(title_y)
        self.axes.set_position([0.07, 0.15, 0.91, 0.75])
        self.canvas.draw()
        # а вот следующее-устанавливаем в спинах границы, которые можно крутить туда-сюда
        self.spinsection.set_values(self.plot_data)

    def refresh_plot(self, evt):
        if not self.spinsection.fixed_plot():
            x_min_new = float(self.spinsection.xmin.text.GetValue())
            x_max_new = float(self.spinsection.xmax.text.GetValue())
            y_min_new = float(self.spinsection.ymin.text.GetValue())
            y_max_new = float(self.spinsection.ymax.text.GetValue())
            self.axes.set_xbound(lower=x_min_new, upper=x_max_new)
            self.axes.set_ybound(lower=y_min_new, upper=y_max_new)
            self.canvas.draw()

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
    
    def on_exit(self, event):
        self.Destroy()
    
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)

    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')


if __name__ == '__main__':
    app = wx.App()
    app.frame = MainFrame()
    app.frame.Show()
    app.MainLoop()

