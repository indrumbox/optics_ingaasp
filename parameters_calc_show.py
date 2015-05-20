# -*- coding: cp1251 -*-
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import random
import math
import sys
# лечим кириллицу в графиках
from matplotlib import rc
font = {'family': 'Verdana', 'weight': 'normal'}
rc('font', **font)


# Adachi [4]
Structures = {'GaAs': {'A': 3.45, 'B1': 2.731, 'B2': 2.407, 'G': 0.10, 'C': 2.39,
                       'Gamma': 0.146, 'D': 24.2, 'E0': 1.42, 'delta0': 0.35,
                       'E1': 2.90, 'delta1': 0.23, 'E2': 4.7},
              'InP': {'A': 6.57, 'B1': 2.414, 'B2': 2.234, 'G': 0.10, 'C': 1.49,
                      'Gamma': 0.094, 'D': 60.4, 'E0': 1.35, 'delta0': 0.1,
                      'E1': 3.10, 'delta1': 0.15, 'E2': 4.7},
              'InAs': {'A': 0.61, 'B1': 3.014, 'B2': 2.525, 'G': 0.21, 'C': 1.78,
                       'Gamma': 0.108, 'D': 20.8, 'E0': 0.36, 'delta0': 0.4,
                       'E1': 2.50, 'delta1': 0.28, 'E2': 4.45},
              'GaP': {'A': 13.76, 'B1': 2.166, 'B2': 2.101, 'G': 0.06, 'C': 2.08,
                      'Gamma': 0.132, 'D': 4.6, 'E0': 2.74, 'delta0': 0.1,
                      'E1': 3.70, 'delta1': 0.07, 'E2': 5.0}}


class Structure_edge():

    def __init__(self, x, y):
        self.x = x
        self.y = y
        # номер структуры: GaAs: 0, InP: 1, InAs: 2, GaP: 3
        self.ID = 1 + 2 * self.x + self.y
        if self.ID == 4:
            self.ID = 0

        # вытаскиваем название структуры и набор значений по параметрам и энергиям
        self.core = Structures.keys()[self.ID]
        self.values = Structures.values()[self.ID]

        #return None

    def __str__(self):
        return Structures.keys()[self.ID]

    def print_parameters(self):
        # для контроля - печать всех параметров материала
        values = self.values
        for item in values:
            print item, '=', values[item]
        return None

    def find_parameter(self, parameter):
        return self.values[parameter]

    def find_by_xy(self, x, y):
        # проходя по наборам составов (x, y), ищем соответствующий бинарник
        if self.x == x and self.y == y:
            return True
        else:
            return False


def show_linear(axes):
    # генерим структуру на подложке InP
    x = lambda y: 0.1894 * y / (0.4184 - 0.013 * y)
    A = lambda y: 6.57 - 4.2 * y
    Yarr = [i * 0.1 for i in range(11)]
    Xarr = []
    Zarr = [A(i*0.1) for i in range(11)]
    for y in Yarr:
      Xarr.append(x(y))
    X, Y = np.meshgrid(Xarr, Yarr)
    inp = np.array([0 for x,y in zip(np.ravel(X), np.ravel(Y))])
    print inp
    Z = inp.reshape(X.shape)

    surf = axes.plot(Xarr, Yarr, Zarr)


def get_name_by_xy(collection, x, y):
    for element in collection:
        if element.find_by_xy(x, y):
            return element.core


def edges(collection, x, y, flag_parameter):
    for element in collection:
        if element.find_by_xy(x, y):
            return element.find_parameter(flag_parameter)
#print edges(0, 1, 'Gamma') - задаём составы материалов и параметр, который нужно найти


def Vegard(edge_values, x, y):
    GaAs_value, GaP_value, InAs_value, InP_value = edge_values
    return x*y*GaAs_value + x*(1-y)*GaP_value + y*(1-x)*InAs_value + (1-y)*(1-x)*InP_value

def return_vegard(parameter, x, y):
    '''
    Возвращает значение параметра parameter для промежуточных значений x и y
    '''
    InP = Structure_edge(x=0, y=0)
    InAs = Structure_edge(x=0, y=1)
    GaP = Structure_edge(x=1, y=0)
    GaAs = Structure_edge(x=1, y=1)

    edge_values = list()
    edge_values.append(GaAs.find_parameter(parameter))
    edge_values.append(GaP.find_parameter(parameter))
    edge_values.append(InAs.find_parameter(parameter))
    edge_values.append(InP.find_parameter(parameter))
    return Vegard(edge_values, x, y)

#print return_vegard("A", 0., 0.)
#print return_vegard("A", 0., 1.)
#print return_vegard("A", 0.5, 0.5)


def show(parameter):
    fig = plt.figure(u"Силовые параметры InGaAsP [{0}]".format(parameter))
    ax = fig.add_subplot(111, projection='3d')
    fig.suptitle(u"Силовые параметры InGaAsP [{0}]".format(parameter))

    #X, Y, Z = axes3d.get_test_data(.05)
    #Z = [[1., 2.], [3., 5.]]

    InP = Structure_edge(x=0, y=0)
    InAs = Structure_edge(x=0, y=1)
    GaP = Structure_edge(x=1, y=0)
    GaAs = Structure_edge(x=1, y=1)
    Collection = [InP, InAs, GaP, GaAs]

    # выводим угловые значения силовых параметров
    X = [0., 1.]
    Y = [0., 1.]
    X, Y = np.meshgrid(X, Y)
    zs = np.array([edges(Collection, x, y, parameter) for x,y in zip(np.ravel(X), np.ravel(Y))])
    Z = zs.reshape(X.shape)
    surf = ax.scatter(X, Y, Z, s=50, c='r', antialiased=False)


    # выводим метки с названиями элементов по краям поверхности
    for iter1 in range(len(Z)):
        for iter2 in range(len(Z[0])):

            element_name = get_name_by_xy(Collection, X[iter1][iter2], Y[iter1][iter2])
            #print X[iter1][iter2], ':', Y[iter1][iter2], ' ~ ', round(Z[iter1][iter2], 1), ' (', element_name, ')'
            ax.text(0.1 + X[iter1][iter2], Y[iter1][iter2], round(Z[iter1][iter2], 1), element_name, zdir=None)

    edge_values = []
    edge_values.append(GaAs.find_parameter(parameter))
    edge_values.append(GaP.find_parameter(parameter))
    edge_values.append(InAs.find_parameter(parameter))
    edge_values.append(InP.find_parameter(parameter))

    X = np.arange(0, 1.1, 0.1)
    Y = np.arange(0, 1.1, 0.1)
    X, Y = np.meshgrid(X, Y)
    zs = np.array([Vegard(edge_values, x, y) for x,y in zip(np.ravel(X), np.ravel(Y))])
    Z = zs.reshape(X.shape)


    #show_linear(ax)

    surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.RdYlGn,
                           linewidth=0, antialiased=False)

    #plot_surface
    #fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.clabel(1, 1, 1)
    plt.show()


def calculate_parameter_for_xy(parameter, x, y):
    '''
    Функция под внешний расчёт параметров по заданным произвольным x и y
    '''
    InP = Structure_edge(x=0, y=0)
    InAs = Structure_edge(x=0, y=1)
    GaP = Structure_edge(x=1, y=0)
    GaAs = Structure_edge(x=1, y=1)
    #Collection = [InP, InAs, GaP, GaAs]
    edge_values = []
    edge_values.append(GaAs.find_parameter(parameter))
    edge_values.append(GaP.find_parameter(parameter))
    edge_values.append(InAs.find_parameter(parameter))
    edge_values.append(InP.find_parameter(parameter))
    return Vegard(edge_values, x, y)


def main():
    #print sys.argv
    if len(sys.argv) > 1:
        param = sys.argv[1]
        show(param)
    else:
        print u"Использование: с параметрами [A] [B1] [B2] [G] [C] [Gamma] [D] [E0] [delta0] [E1] [delta1] [E2]"
        param = "A"
        print u"Параметр по умолчанию: A"
        show(param)

#main()