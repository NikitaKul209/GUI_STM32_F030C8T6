import asyncio
import serial
import pymodbus.client as ModbusClient
from pymodbus import (
    ExceptionResponse,
    Framer,
    ModbusException,
    pymodbus_apply_logging_config,

)



async def run_async_simple_client(port, framer=Framer.SOCKET):

    client = ModbusClient.AsyncModbusSerialClient(
        port,
        framer,
        # timeout=10,
        # retries=3,
        # retry_on_empty=False,
        # strict=True,
        baudrate=38400,
        bytesize=8,
        parity="N",
        stopbits=1,
        # handle_local_echo=False,
    )

    await client.connect()
    # test client is connected
    assert client.connected
    try:
        rr = await client.read_holding_registers()

    except ModbusException as exc:
        print(f"Received ModbusException({exc}) from library")
        client.close()
        return
    if rr.isError():
        print(f"Received Modbus library error({rr})")
        client.close()
        return
    if isinstance(rr, ExceptionResponse):
        print(f"Received Modbus library exception ({rr})")
        # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
        client.close()

    print("close connection")
    client.close()

