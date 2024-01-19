using System;
using InTheHand.Net.Sockets;
using InTheHand.Net.Bluetooth;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace AquaHub.MobiusController
{
    public class MobiusDevice
    {
        private BluetoothClient bluetoothClient;
        private ILogger _logger;

        public MobiusDevice(ILogger logger)
        {
            bluetoothClient = new BluetoothClient();
            _logger = logger;
        }

        public async Task ScanAndConnectAsync()
        {
            _logger.LogInformation("Scanning for Bluetooth devices...");
            //BluetoothDeviceInfo[] devices = bluetoothClient.DiscoverDevicesInRange();

            //foreach (BluetoothDeviceInfo device in devices)
            //{
            //    _logger.LogInformation($"Found Device: {device.DeviceName}, Address: {device.DeviceAddress}");
            //    if (device.DeviceName == "YourMobiusDeviceName") // Replace with your device's name
            //    {
            //        _logger.LogInformation($"Connecting to {device.DeviceName}...");
            //        await ConnectToDeviceAsync(device);
            //        break;
            //    }
            //}
        }

        private async Task ConnectToDeviceAsync(BluetoothDeviceInfo device)
        {
            try
            {
                //bluetoothClient.BeginConnect(device.DeviceAddress, BluetoothService.SerialPort, ConnectCallback, device);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error connecting to device: {ex.Message}");
            }
        }

        private void ConnectCallback(IAsyncResult result)
        {
            try
            {
                //bluetoothClient.EndConnect(result);
                _logger.LogInformation("Connected to device.");

                // Here you can interact with the device, e.g., read/write data
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error during connection: {ex.Message}");
            }
        }

        public void Disconnect()
        {
            if (bluetoothClient.Connected)
            {
                bluetoothClient.Close();
                _logger.LogInformation("Disconnected.");
            }
        }
    }
}
