#![no_std]
#![no_main]

use cortex_m_rt::entry;
use fixsliced_gift::gift128::key_schedule::mask_key;
use fixsliced_gift::gift128::mask_block;
use nb::block;
use panic_halt as _;
use stm32f3xx_hal::prelude::*;

use cortex_time::setup;

#[entry]
fn main() -> ! {
    let (serial, mut trigger) = setup();

    let (_, mut rx) = serial.split();

    let key = [
        0xd0, 0xf5, 0xc5, 0x9a, 0x77, 0x00, 0xd3, 0xe7,
        0x99, 0x02, 0x8f, 0xa9, 0xf9, 0x0a, 0xd8, 0x37,
    ];

    loop {
        let masked_plaintext = {
            let mut plaintext = [0; 16];
            for p in plaintext.iter_mut() {
                *p = block!(rx.read()).unwrap();
            }
            let mut plaintext_masks = [0; 16];
            for p in plaintext_masks.iter_mut() {
                *p = block!(rx.read()).unwrap();
            }
            mask_block(&plaintext, &plaintext_masks)
        };

        let masked_key = {
            let mut key_masks = [0; 16];
            for p in key_masks.iter_mut() {
                *p = block!(rx.read()).unwrap();
            }
            mask_key(&key, &key_masks)
        };

        let mut masked_ciphertext = [Default::default(); 16];
        cortex_m::interrupt::free(|_| {
            trigger.set_high().unwrap();
            fixsliced_gift::gift128::encrypt_masked(&masked_plaintext, &masked_key, &mut masked_ciphertext);
            trigger.set_low().unwrap();
        });
    }
}
