#![no_std]

use core::fmt::Debug;

use nb::block;
use stm32f3xx_hal::{self as hal, pac, prelude::*};
use stm32f3xx_hal::gpio::{Alternate, Gpioa, Output, Pin, PushPull, U};
use stm32f3xx_hal::serial::Serial;
use crate::pac::USART1;

pub fn setup() -> (Serial<USART1, (Pin<Gpioa, U<9>, Alternate<PushPull, 7>>, Pin<Gpioa, U<10>, Alternate<PushPull, 7>>)>, Pin<Gpioa, U<12>, Output<PushPull>>) {
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
    (serial, trigger)
}

pub fn read_u32<T>(rx: &mut T) -> u32
    where
        T: embedded_hal::serial::Read<u8>,
        <T as embedded_hal::serial::Read<u8>>::Error: Debug {
    let b1 = block!(rx.read()).unwrap();
    let b2 = block!(rx.read()).unwrap();
    let b3 = block!(rx.read()).unwrap();
    let b4 = block!(rx.read()).unwrap();
    u32::from_le_bytes([b1, b2, b3, b4])
}
