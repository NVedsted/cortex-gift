import os
import sys

import chipwhisperer as cw
import zarr
from chipwhisperer.capture.scopes import OpenADC
from chipwhisperer.capture.targets import SimpleSerial
from tqdm import tqdm

DEFAULT_CHUNKS = (25, None)


# def reset_target(scope: OpenADC, target: SimpleSerial):
#     scope.io.nrst = 'low'
#     time.sleep(0.05)
#     scope.io.nrst = 'high_z'
#     time.sleep(0.05)
#     num_char = target.in_waiting()
#     while num_char > 0:
#         target.read(num_char, 10)
#         time.sleep(0.01)
#         num_char = target.in_waiting()


def encrypt_plaintext(scope: OpenADC, target: SimpleSerial, plaintext: bytes):
    scope.arm()
    target.write(plaintext)
    scope.capture()
    return scope.get_last_trace()


def encrypt_masked_plaintext(scope: OpenADC, target: SimpleSerial, plaintext: bytes):
    scope.arm()
    target.write(plaintext)
    target.write(os.urandom(16 * 2))
    scope.capture()
    return scope.get_last_trace()


def test_unmasked(scope: OpenADC, target: SimpleSerial, n: int):
    scope.adc.samples = 24400
    cw.program_target(scope, cw.programmers.STM32FProgrammer, "programs/unmasked.hex")
    plaintext1 = bytes([0xe3, 0x9c, 0x14, 0x1f, 0xa5, 0x7d, 0xba, 0x43,
                        0xf0, 0x8a, 0x85, 0xb6, 0xa9, 0x1f, 0x86, 0xc1])
    data1 = zarr.open_array(f'data/{n}_unmasked_fixed.zarr', 'w-', shape=(n, scope.adc.samples), chunks=DEFAULT_CHUNKS)
    for i in tqdm(range(n), "Unmasked - Group 1 (fixed plaintext)"):
        data1[i] = encrypt_plaintext(scope, target, plaintext1)

    data2 = zarr.open_array(f'data/{n}_unmasked_random.zarr', 'w-', shape=(n, scope.adc.samples), chunks=DEFAULT_CHUNKS)
    for i in tqdm(range(n), "Unmasked - Group 2 (random plaintext)"):
        plaintext2 = os.urandom(16)
        data2[i] = encrypt_plaintext(scope, target, plaintext2)


def test_masked(scope: OpenADC, target: SimpleSerial, n: int):
    cw.program_target(scope, cw.programmers.STM32FProgrammer, "programs/masked.hex")
    plaintext1 = bytes([0xe3, 0x9c, 0x14, 0x1f, 0xa5, 0x7d, 0xba, 0x43,
                        0xf0, 0x8a, 0x85, 0xb6, 0xa9, 0x1f, 0x86, 0xc1])
    data1 = zarr.open_array(f'data/{n}_masked_fixed.zarr', 'w-', shape=(n, scope.adc.samples), chunks=DEFAULT_CHUNKS)
    for i in tqdm(range(n), "Masked - Group 1 (fixed plaintext)"):
        data1[i] = encrypt_masked_plaintext(scope, target, plaintext1)

    data2 = zarr.open_array(f'data/{n}_masked_random.zarr', 'w-', shape=(n, scope.adc.samples), chunks=DEFAULT_CHUNKS)
    for i in tqdm(range(n), "Masked - Group 2 (random plaintext)"):
        plaintext2 = os.urandom(16)
        data2[i] = encrypt_masked_plaintext(scope, target, plaintext2)


def start():
    n = int(sys.argv[1])
    scope = cw.scope()
    scope.default_setup()
    scope.adc.samples = 24400
    target = cw.target(scope)
    test_unmasked(scope, target, n)
    test_masked(scope, target, n)


if __name__ == '__main__':
    start()
