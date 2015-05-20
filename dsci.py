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

def H(x):
    return 0 if x < 0 else 1

def f(ksi):
    if 1-ksi<0:
        return (1 / (ksi*ksi)) * (2 - math.sqrt(1+ksi))
    return (1 / (ksi*ksi)) * (2 - math.sqrt(1+ksi) - H(1-ksi)*math.sqrt(1-ksi))

class Structure():

    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.lambdas_pack = [i*0.01 for i in range(1, 500)]
        self.energies_pack = [self.get_energy(lam) for lam in self.lambdas_pack]
        self.sellmeiers_pack = [self.sellmeier(lam) for lam in self.lambdas_pack]
        self.epsilon_g_pack = []
        self.epsilon_x_pack = []
        self.epsilon_l_pack = []
        self.full_epsilon_pack = []
        self.full_refraction_pack = []

        # [A] [B1] [B11] [G] [C] [Gamma] [D] [E0] [delta0] [E1] [delta1] [E2]
#       так не сработает:
#        for param in ["A", "B1", "B11", "G", "C", "Gamma", "D", "E0", "delta0", "E1", "delta1", "E2"]:
#            self.param = calc(param, self.x, self.y)
        self.A = calc("A", self.x, self.y)
        self.B1 = calc("B1", self.x, self.y)
        self.B2 = calc("B2", self.x, self.y)
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
        # немного тупая реализация, но эти данные уходят на отрисовку;
        # чтобы значения для энергий были нормальные!
        self.lambdas_pack = [i*0.01 for i in range(1, 500)]
        self.energies_pack = [self.get_energy(lam) for lam in self.lambdas_pack]
        return self.lambdas_pack

    def get_energies(self):
        self.energies_pack = [i*0.01 for i in range(20, 1002, 2)] # 0.2...10.0 эВ
        self.lambdas_pack = [self.get_energy(lam) for lam in self.energies_pack]
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

    def get_epsilon_g_pack(self):
        self.epsilon_g_pack = []
        for lambda_ in self.lambdas_pack:
            self.epsilon_g_pack.append(self.eps0(lambda_, "eps1"))
        return self.epsilon_g_pack

    def get_epsilon_l_pack(self):
        self.epsilon_l_pack = []
        for lambda_ in self.lambdas_pack:
            self.epsilon_l_pack.append(self.eps1(lambda_, "eps1"))
        return self.epsilon_l_pack

    def get_epsilon_x_pack(self):
        self.epsilon_x_pack = []
        for lambda_ in self.lambdas_pack:
            self.epsilon_x_pack.append(self.eps2(lambda_, "eps1"))
        return self.epsilon_x_pack

    def get_full_epsilon_pack(self):
        self.full_epsilon_pack = []
        for lambda_ in self.lambdas_pack:
            self.full_epsilon_pack.append(self.eps_full(lambda_, "eps1"))
        return self.full_epsilon_pack

    def get_refraction_pack(self):
        self.full_refraction_pack = []
        for lambda_ in self.lambdas_pack:
            self.full_refraction_pack.append(self.refraction(lambda_))
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
        func = 0.
        ksi10 = current_energy / self.E1
        ksi11 = current_energy / (self.E1 + self.delta1)
        # if not ksi10 > 1.:
        #     func = func - (self.B1 / (ksi10*ksi10)) * math.log(1 - ksi10*ksi10)
        # if not ksi11 > 1.:
        #     func = func - (self.B11 / (ksi11*ksi11)) * math.log(1 - ksi11*ksi11)
        arg1 = 1 - ksi10*ksi10 if not ksi10 > 1. else 1e-30
        arg2 = 1 - ksi11*ksi11 if not ksi11 > 1. else 1e-30

        func = 0. - (self.B1 * math.log(arg1) / (ksi10*ksi10)) - (self.B2 * math.log(arg2) / (ksi11*ksi11))
        return func

    def epsilon2(self, lambda_value):
        current_energy = self.get_energy(lambda_value)
        ksi20 = current_energy / self.E2
        func = 0
        if not ksi20 > 1.:
            func = self.C * (1 - ksi20*ksi20) / ( (1-ksi20**2)**2 + self.Gamma**2 * ksi20**2 )
        return func

    def eps0(self, lambda_value, param):
        current_energy = self.get_energy(lambda_value)
        ksi0 = current_energy / self.E0
        ksi0s = current_energy / (self.E0 + self.delta0)
        epsilon_2 = (self.A / (current_energy**2)) * (H(ksi0-1) * math.sqrt(abs(current_energy-self.E0)) + 0.5 * H(ksi0s-1) * math.sqrt(abs(current_energy - self.E0 - self.delta0)))
        epsilon_1 = self.A * (self.E0 ** -1.5) * ( f(ksi0) + 0.5 * f(ksi0s) * ((self.E0 / (self.E0 + self.delta0))**1.5) )
        if param == "eps1":
            return epsilon_1
        elif param == "eps2":
            return epsilon_2
        else:
            return ValueError

    def eps1(self, lambda_value, param):
        current_energy = self.get_energy(lambda_value)
        ksi1 = current_energy / self.E1
        ksi1s = current_energy / (self.E1 + self.delta1)
        epsilon_2_1 = self.B1 * math.pi / (ksi1 * ksi1) if ksi1 - 1. > 0. else 0.
        epsilon_2_2 = self.B2 * math.pi / (ksi1s * ksi1s) if ksi1s - 1. > 0. else 0.
        epsilon_2 = epsilon_2_1 + epsilon_2_2
        epsilon_1 = 0. - self.B1 * math.log(1e-5 + abs(1 - ksi1*ksi1)) / (ksi1 * ksi1) - self.B2 * math.log(1e-33 + abs(1 - ksi1s*ksi1s)) / (ksi1s * ksi1s)
        # получили значения для epsilon_1 и epsilon_2
        if param == "eps1":
            return epsilon_1
        elif param == "eps2":
            return epsilon_2
        else:
            return ValueError

    def eps2(self, lambda_value, param):
        current_energy = self.get_energy(lambda_value)
        ksi2 = current_energy / self.E2
        epsilon_2 = self.C * self.Gamma * ksi2 / ((1-ksi2**2)**2 + (self.Gamma*ksi2)**2)
        epsilon_1 = self.C * (1-ksi2**2) / ((1-ksi2**2)**2 + (self.Gamma*ksi2)**2)
        if param == "eps1":
            return epsilon_1
        elif param == "eps2":
            return epsilon_2
        else:
            return ValueError

    def eps_full(self, lambda_value, param):
        return self.eps0(lambda_value, param) + self.eps1(lambda_value, param) + self.eps2(lambda_value, param)

    def refraction(self, lambda_value):
        e1 = self.eps_full(lambda_value, "eps1")
        e2 = self.eps_full(lambda_value, "eps2")
        return math.sqrt(0.5 * (e1 + math.sqrt(e1*e1 + e2*e2)))


y = 0.0
x = x_on_InP(y)
test = Structure(x, y)
print test.get_sellmeier_pack()
print len(test.get_sellmeier_pack())