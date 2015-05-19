# -*- coding: cp1251 -*-
import math
from parameters_calc_show import calculate_parameter_for_xy as calc

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


class Structure():

    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.lambdas_pack = [i*0.01 for i in range(1, 500)]
        self.energies_pack = [self.get_energy(lam) for lam in self.lambdas_pack]
        self.sellmeiers_pack = [self.sellmeier(lam) for lam in self.lambdas_pack]
        self.refraction_g_pack = []
        self.refraction_x_pack = []
        self.refraction_l_pack = []
        self.full_refraction_pack = []

        # [A] [B1] [B11] [G] [C] [Gamma] [D] [E0] [delta0] [E1] [delta1] [E2]
#       так не сработает:
#        for param in ["A", "B1", "B11", "G", "C", "Gamma", "D", "E0", "delta0", "E1", "delta1", "E2"]:
#            self.param = calc(param, self.x, self.y)
        self.A = calc("A", self.x, self.y)
        self.B1 = calc("B1", self.x, self.y)
        self.B11 = calc("B11", self.x, self.y)
        self.G = calc("G", self.x, self.y)
        self.C = calc("C", self.x, self.y)
        self.Gamma = calc("Gamma", self.x, self.y)
        self.D = calc("D", self.x, self.y)
        self.E0 = calc("E0", self.x, self.y)
        self.delta0 = calc("delta0", self.x, self.y)
        self.E1 = calc("E1", self.x, self.y)
        self.delta1 = calc("delta1", self.x, self.y)
        self.E2 = calc("E2", self.x, self.y)

    def get_energy(self, lambda_value):
        return (6.6256E-34 * 2.99E8) / (1.6e-19 * 1.0e-6 * lambda_value)

    def get_lambdas(self):
        return self.lambdas_pack

    def get_energies(self):
        return self.energies_pack

    def sellmeier(self, lambda_value):
        # работает на согласованном с подложкой материале!
        A = 7.255 + 1.15 * self.y + 0.489 * self.y * self.y
        B = 2.316 + 0.604 * self.y - 0.493 * self.y * self.y
        C = 0.3922 + 0.396 * self.y + 0.158 * self.y * self.y
        epsilon = A + (B * lambda_value * lambda_value) / (lambda_value * lambda_value - C)
        return math.sqrt(abs(epsilon))

    def get_sellmeier_pack(self):
        return self.sellmeiers_pack

    def get_refr_g_pack(self):
        self.refraction_g_pack = []
        for lambda_ in self.lambdas_pack:
            self.refraction_g_pack.append(math.sqrt(self.epsilon0(lambda_)))
        return self.refraction_g_pack

    def get_refr_l_pack(self):
        self.refraction_l_pack = []
        for lambda_ in self.lambdas_pack:
            self.refraction_l_pack.append(math.sqrt(self.epsilon1(lambda_)))
        return self.refraction_l_pack

    def get_refr_x_pack(self):
        self.refraction_x_pack = []
        for lambda_ in self.lambdas_pack:
            self.refraction_x_pack.append(math.sqrt(self.epsilon2(lambda_)))
        return self.refraction_x_pack

    def get_full_refr_pack(self):
        self.full_refraction_pack = []
        for counter in range(len(self.refraction_g_pack)):
            self.full_refraction_pack.append(self.refraction_g_pack[counter] + self.refraction_l_pack[counter] + self.refraction_x_pack[counter])
        #sum_ = lambda x1, x2, x3: x1+x2+x3
        #self.full_refraction_pack = map[sum_, self.refraction_g_pack, self.refraction_l_pack, self.refraction_x_pack]
        return self.full_refraction_pack

    def g(self, otn_energy):
        if otn_energy < 1.:
            func = (2 - math.sqrt(1+otn_energy) - math.sqrt(1-otn_energy)) / (otn_energy**2)
        else:
            func = (2 - math.sqrt(1+otn_energy)) / (otn_energy**2)
        return func

    def epsilon0(self, lambda_value):
        current_energy = self.get_energy(lambda_value)
        ksi00 = current_energy / self.E0
        ksi01 = current_energy / (self.E0 + self.delta0)
        coeff = self.A / pow(self.E0, 1.5)
        eps00 = self.g(ksi00) + self.g(ksi01) * 0.5 * pow(self.E0 / (self.E0+self.delta0), 1.5)
        if eps00 < 0.:
            eps00 = 0.
        return coeff * eps00

    def epsilon1(self, lambda_value):
        current_energy = self.get_energy(lambda_value)
        func = 0
        ksi10 = current_energy / self.E1
        ksi11 = current_energy / (self.E1 + self.delta1)
        if not ksi10 > 1.:
            func = func - (self.B1 / (ksi10*ksi10)) * math.log(1 - ksi10*ksi10)
        if not ksi11 > 1.:
            func = func - (self.B11 / (ksi11*ksi11)) * math.log(1 - ksi11*ksi11)
        return func

    def epsilon2(self, lambda_value):
        current_energy = self.get_energy(lambda_value)
        ksi20 = current_energy / self.E2
        func = 0
        if not ksi20 > 1.:
            func = self.C * (1 - ksi20*ksi20) / ( (1-ksi20**2)**2 + self.Gamma**2 * ksi20**2 )
        return func




y = 0.0
x = x_on_InP(y)
test = Structure(x, y)
print test.get_sellmeier_pack()
print len(test.get_sellmeier_pack())