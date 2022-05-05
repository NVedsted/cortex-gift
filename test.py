import os
import time

import chipwhisperer as cw
import matplotlib.pyplot as plt
import numpy as np
from chipwhisperer.capture.scopes import OpenADC
from chipwhisperer.capture.targets import SimpleSerial
# from cwtvla.analysis import t_test, check_t_test
from tqdm import tqdm


def reset_target(scope: OpenADC, target: SimpleSerial):
    scope.io.nrst = 'low'
    time.sleep(0.05)
    scope.io.nrst = 'high_z'
    time.sleep(0.05)
    num_char = target.in_waiting()
    while num_char > 0:
        target.read(num_char, 10)
        time.sleep(0.01)
        num_char = target.in_waiting()


def encrypt_plaintext(scope: OpenADC, target: SimpleSerial, plaintext: bytes):
    reset_target(scope, target)
    scope.arm()
    target.write(plaintext)
    scope.capture()
    # time.sleep(0.3)
    # print([hex(ord(c)) for c in target.read(num_char=16)])
    return scope.get_last_trace()


def test():
    scope = cw.scope()
    scope.default_setup()
    scope.adc.samples = 1000
    target = cw.target(scope)
    # cw.program_target(scope, cw.programmers.STM32FProgrammer, "memes.hex")
    plaintext1 = bytes([0xe3, 0x9c, 0x14, 0x1f, 0xa5, 0x7d, 0xba, 0x43,
                        0xf0, 0x8a, 0x85, 0xb6, 0xa9, 0x1f, 0x86, 0xc1])
    data1 = []
    for _ in tqdm(range(10), "Group 1 (fixed plaintext)"):
        # data1.append(encrypt_plaintext(scope, target, plaintext1))
        plt.plot(encrypt_plaintext(scope, target, plaintext1))
    plt.savefig("output.png")

    # data2 = []
    # for _ in tqdm(range(100), "Group 2 (random plaintext)"):
    #     plaintext2 = os.urandom(16)
    #     data2.append(encrypt_plaintext(scope, target, plaintext2))
    #
    # t_val = t_test(np.array(data1), np.array(data2))
    # plt.plot(t_val[0])
    # plt.plot(t_val[1])
    # plt.savefig('ttest.png')
    # fail_points = check_t_test(t_val)
    # print(fail_points)


if __name__ == '__main__':
    test()
