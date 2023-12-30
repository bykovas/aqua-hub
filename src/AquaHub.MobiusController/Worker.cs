using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace AquaHub.MobiusController
{
    public class Worker : BackgroundService
    {
        private readonly ILogger<Worker> _logger;
        private MobiusDevice mobiusDevice;

        public Worker(ILogger<Worker> logger)
        {
            _logger = logger;
            mobiusDevice = new MobiusDevice(_logger);
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            while (!stoppingToken.IsCancellationRequested)
            {
                _logger.LogInformation("Worker running at: {time}", DateTimeOffset.Now);

                try
                {
                    await mobiusDevice.ScanAndConnectAsync();
                    // Add logic to interact with MobiusDevice

                    // After interaction
                    mobiusDevice.Disconnect();
                }
                catch (Exception ex)
                {
                    _logger.LogError($"An error occurred: {ex.Message}");
                }

                await Task.Delay(10000, stoppingToken); // Delay for 10 seconds
            }
        }
    }
}