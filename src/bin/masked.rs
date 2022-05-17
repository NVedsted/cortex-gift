#![no_std]
#![no_main]

use cortex_m_rt::entry;
use nb::block;
use panic_halt as _;
use stm32f3xx_hal::prelude::*;

use cortex_time::{read_u32, setup};

#[entry]
fn main() -> ! {
    let (serial, mut trigger) = setup();

    let (mut tx, mut rx) = serial.split();

    let key = [
        0xd0, 0xf5, 0xc5, 0x9a, 0x77, 0x00, 0xd3, 0xe7,
        0x99, 0x02, 0x8f, 0xa9, 0xf9, 0x0a, 0xd8, 0x37,
    ];

    loop {
        let mut plaintext = [0; 16];
        for p in plaintext.iter_mut() {
            *p = block!(rx.read()).unwrap();
        }
        let state_masks = (
            read_u32(&mut rx),
            read_u32(&mut rx),
            read_u32(&mut rx),
            read_u32(&mut rx)
        );
        let key_masks = (
            read_u32(&mut rx),
            read_u32(&mut rx),
            read_u32(&mut rx),
            read_u32(&mut rx)
        );
        let mut ciphertext = [0; 16];
        cortex_m::interrupt::free(|_| {
            trigger.set_high().unwrap();
            fixsliced_gift::gift128::encrypt_masked(&plaintext, &[state_masks], &key, &mut ciphertext, key_masks);
            trigger.set_low().unwrap();
        });
        for c in ciphertext {
            block!(tx.write(c)).unwrap();
        }
    }
}
