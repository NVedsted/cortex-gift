#![no_std]
#![no_main]

use cortex_m_rt::entry;
use nb::block;
use panic_halt as _;
use stm32f3xx_hal::{self as hal, pac, prelude::*};

#[inline(never)]
fn critical_function(input: &[u8], key: &[u8; 16], output: &mut [u8]) {
    fixsliced_gift::gift128::encrypt(input, key, output);
}

#[entry]
fn main() -> ! {
    let dp = pac::Peripherals::take().unwrap();

    let mut flash = dp.FLASH.constrain();
    let mut rcc = dp.RCC.constrain();
    let mut gpioa = dp.GPIOA.split(&mut rcc.ahb);

    let clocks = rcc.cfgr.freeze(&mut flash.acr);

    let tx = gpioa.pa9.into_af_push_pull(&mut gpioa.moder, &mut gpioa.otyper, &mut gpioa.afrh);
    let rx = gpioa.pa10.into_af_push_pull(&mut gpioa.moder, &mut gpioa.otyper, &mut gpioa.afrh);
    let mut trigger = gpioa.pa12.into_push_pull_output(&mut gpioa.moder, &mut gpioa.otyper);
    trigger.set_low().unwrap();

    let serial = hal::serial::Serial::new(
        dp.USART1,
        (tx, rx),
        38_400.Bd(),
        clocks,
        &mut rcc.apb2,
    );

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
        let mut ciphertext = [0; 16];
        cortex_m::interrupt::free(|_| {
            trigger.set_high().unwrap();
            critical_function(&plaintext, &key, &mut ciphertext);
            trigger.set_low().unwrap();
        });
        for c in ciphertext {
            block!(tx.write(c)).unwrap();
        }
    }
}
