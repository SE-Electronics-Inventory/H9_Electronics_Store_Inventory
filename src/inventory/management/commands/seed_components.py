"""
Management command to seed realistic electronic components (FR-04, TC-INV-02, TC-AVAIL-01)
"""
from django.core.management.base import BaseCommand
from decimal import Decimal
from inventory.models import Component


SAMPLE_COMPONENTS = [
    {
        "component_id": "RES-10K-01",
        "name": "10k Ohm Metal Film Resistor 1/4W",
        "category": "Passives",
        "description": "Standard 10k ohm 1/4W 1% tolerance through-hole resistors.",
        "price": Decimal("2.50"),
        "quantity": 150,
        "minimum_stock": 25,
    },
    {
        "component_id": "CAP-100U-01",
        "name": "100uF 25V Electrolytic Capacitor",
        "category": "Passives",
        "description": "Radial lead electrolytic capacitor suitable for power filtering.",
        "price": Decimal("8.00"),
        "quantity": 80,
        "minimum_stock": 20,
    },
    {
        "component_id": "ESP32-WROOM",
        "name": "ESP32-WROOM-32D Development Board",
        "category": "Microcontrollers",
        "description": "Dual-core Wi-Fi & Bluetooth microcontroller module with CP2102.",
        "price": Decimal("380.00"),
        "quantity": 18,
        "minimum_stock": 5,
    },
    {
        "component_id": "ARD-UNO-R3",
        "name": "Arduino Uno R3 Compatible Board",
        "category": "Microcontrollers",
        "description": "ATmega328P microcontroller board with USB cable.",
        "price": Decimal("450.00"),
        "quantity": 4,
        "minimum_stock": 8,  # Low stock!
    },
    {
        "component_id": "SEN-DHT11",
        "name": "DHT11 Temperature & Humidity Sensor",
        "category": "Sensors",
        "description": "Basic, ultra low-cost digital temperature and humidity sensor.",
        "price": Decimal("95.00"),
        "quantity": 5,
        "minimum_stock": 10,  # Low stock!
    },
    {
        "component_id": "SEN-HCSR04",
        "name": "HC-SR04 Ultrasonic Distance Sensor",
        "category": "Sensors",
        "description": "Ultrasonic distance ranging module 2cm-400cm.",
        "price": Decimal("75.00"),
        "quantity": 30,
        "minimum_stock": 10,
    },
    {
        "component_id": "IC-555-TMR",
        "name": "NE555 Precision Timer IC",
        "category": "Semiconductors",
        "description": "Standard 8-pin DIP precision timer IC.",
        "price": Decimal("15.00"),
        "quantity": 60,
        "minimum_stock": 15,
    },
    {
        "component_id": "IC-L298N-DRV",
        "name": "L298N Dual H-Bridge Motor Driver Module",
        "category": "Semiconductors",
        "description": "High power dual motor driver module for stepper and DC motors.",
        "price": Decimal("160.00"),
        "quantity": 0,  # Out of stock!
        "minimum_stock": 5,
    },
    {
        "component_id": "OPT-LED-RED",
        "name": "5mm Red Diffused LED (Pack of 10)",
        "category": "Optoelectronics",
        "description": "Standard 5mm high brightness red indicator LEDs.",
        "price": Decimal("20.00"),
        "quantity": 200,
        "minimum_stock": 30,
    },
    {
        "component_id": "OPT-OLED-096",
        "name": "0.96 inch I2C OLED Display 128x64 Blue",
        "category": "Optoelectronics",
        "description": "Monochrome 128x64 I2C interface OLED graphic display.",
        "price": Decimal("220.00"),
        "quantity": 3,
        "minimum_stock": 6,  # Low stock!
    },
    {
        "component_id": "PWR-ADAPT-12V",
        "name": "12V 2A DC Power Supply Adapter",
        "category": "Power",
        "description": "Regulated switching power supply adapter with 5.5x2.1mm DC barrel plug.",
        "price": Decimal("280.00"),
        "quantity": 0,  # Out of stock!
        "minimum_stock": 5,
    },
]


class Command(BaseCommand):
    help = "Populate database with realistic initial electronic components"

    def handle(self, *args, **options):
        created_count = 0
        for data in SAMPLE_COMPONENTS:
            obj, created = Component.objects.get_or_create(
                component_id=data["component_id"],
                defaults=data
            )
            if created:
                created_count += 1
        self.stdout.write(
            self.style.SUCCESS(f"Successfully seeded {created_count} components. Total components: {Component.objects.count()}")
        )
