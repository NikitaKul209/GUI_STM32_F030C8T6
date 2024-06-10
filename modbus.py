import asyncio
import serial
import pymodbus.client as ModbusClient
from pymodbus import (
    ExceptionResponse,
    Framer,
    ModbusException,
    pymodbus_apply_logging_config,

)
class ModbusRTU:
    def __init__(self):
        self.client = None


    def run_sync_simple_client(self,port, framer=Framer.SOCKET.RTU):
        """Run sync client."""
        # activate debugging
        # pymodbus_apply_logging_config("DEBUG")

        print("get client")


        self.client = ModbusClient.ModbusSerialClient(
            port,
            framer=framer,
            # timeout=10,
            # retries=3,
            # retry_on_empty=False,
            # strict=True,
            baudrate=38400,
            bytesize=8,
            parity="E",
            stopbits=1,
            # handle_local_echo=False,
        )
        print("connect to server")
        return self.client.connect()

    def client_read_data(self):
        print("get and verify data")
        try:
            rr = self.client.read_input_registers(0, 4, slave=64)

        except ModbusException as exc:
            print(f"Received ModbusException({exc}) from library")
            self.client.close()
            return exc
        if rr.isError():
            print(f"Received Modbus library error({rr})")
            self.client.close()

            return rr
        if isinstance(rr, ExceptionResponse):
            print(f"Received Modbus library exception ({rr})")
            # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
            self.client.close()
            return rr

        return rr



# if __name__ == "__main__":
#     run_sync_simple_client("tcp", "127.0.0.1", "5020")
