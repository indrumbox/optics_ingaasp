# -*- coding: cp1251 -*-
import math

def Eg_on_InP(x, y):
    return 1.35 + 0.668 * x - 1.17 * y + 0.758 * x * x \
           + 0.18 * y * y - 0.069 * x * y - 0.322 * x * x * y + 0.03 * x * y * y

def lambda_red_on_inp(x, y):
    return 1E6 * 4.136E-15 * 2.99E8 / Eg_on_InP(x, y)


def x_on_InP(y):
    if (y < 0.) or (y > 1.0):
        return 0.
    else:
        return 0.1894 * y / (0.4184 - 0.013 * y)

def g(ksi):
    func = 1 / (ksi * ksi) * (2 - math.sqrt(1 + ksi)) if (1 - ksi < 0) else 1 / (ksi * ksi) * (2 - math.sqrt(1 + ksi) - math.sqrt(1 - ksi))
    return func

class Structure():

    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.lambdas = [i*0.01 for i in range(1, 500)]
        self.energies = [self.get_energy(lam) for lam in self.lambdas]
        self.sellmeiers = [self.sellmeier(lam) for lam in self.lambdas]
        self.refraction_g_pack = []
        self.refraction_x_pack = []
        self.refraction_l_pack = []



    def get_lambdas(self):
        return self.lambdas

    def get_energy(self, lambda_value):
        return (6.6256E-34 * 2.99E8) / (1.6e-19 * 1.0e-6 * lambda_value)

    def get_energies(self):
        return self.energies

    def sellmeier(self, lambda_value):
        # работает на согласованном с подложкой материале!
        A = 7.255 + 1.15 * self.y + 0.489 * self.y * self.y
        B = 2.316 + 0.604 * self.y - 0.493 * self.y * self.y
        C = 0.3922 + 0.396 * self.y + 0.158 * self.y * self.y
        epsilon = A + (B * lambda_value * lambda_value) / (lambda_value * lambda_value - C)
        return math.sqrt(abs(epsilon))

    def get_sellmeier_pack(self):
        return self.sellmeiers

y = 0.0
x = x_on_InP(y)
test = Structure(x, y)
print test.get_sellmeier_pack()
print len(test.get_sellmeier_pack())