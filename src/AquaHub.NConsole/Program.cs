using MQTTnet;
using MQTTnet.Client;
using System.Text;
using Microsoft.ApplicationInsights;
using Microsoft.ApplicationInsights.Extensibility;

#pragma warning disable CS8618 // Non-nullable field must contain a non-null value when exiting constructor. Consider declaring as nullable.

namespace AquaHub.NConsole
{
    internal class Program
    {
        private static IMqttClient _mqttClient;
        private static MqttClientOptions _mqttOptions;
        private static TelemetryClient _telemetryClient;

        static async Task Main(string[] args)
        {
            // Initialize Application Insights
            var config = TelemetryConfiguration.CreateDefault();
            config.ConnectionString = Environment.GetEnvironmentVariable("APPLICATION_INSIGHTS_CONNECTION_STRING");
            _telemetryClient = new TelemetryClient(config);

            // Track custom event in Application Insights
            _telemetryClient.TrackEvent("AquaHubNConsoleServiceRunning");

            try
            {
                // Initialize the MQTT client
                var factory = new MqttFactory();
                _mqttClient = factory.CreateMqttClient();

                // Define MQTT connection options
                _mqttOptions = new MqttClientOptions
                {
                    ClientId = "Client1",
                    Credentials = new MqttClientCredentials("mqttu", Encoding.UTF8.GetBytes("mqttp")),
                    ChannelOptions = new MqttClientTcpOptions
                    {
                        Server = "192.168.1.11"
                    }
                };

                // Handler for MQTT client disconnection
                _mqttClient.DisconnectedAsync += async e =>
                {
                    Console.WriteLine("Disconnected from MQTT broker. Trying to reconnect...");
                    await Task.Delay(TimeSpan.FromSeconds(100));
                    await ConnectMqttClientAsync();
                };

                // Handler for MQTT client connection
                _mqttClient.ConnectedAsync += async e =>
                {
                    Console.WriteLine("Connected to MQTT broker.");
                    // You can add topic subscriptions or other logic here upon connection
                };

                // Attempt to connect to the MQTT broker
                await ConnectMqttClientAsync();

                // Main loop
                while (true)
                {
                    var values = Schedule.get_current_values();
                    var message =
                        $"{DateTime.Now.ToShortTimeString()} - Blue plus: {values[0]}, Coral plus: {values[1]}";
                    Console.WriteLine(message);

                    // Publish to MQTT
                    var messageBuilder = new MqttApplicationMessageBuilder()
                        .WithTopic("ahub/light/t5coral/in")
                        .WithPayload(Encoding.UTF8.GetBytes(values[1].ToString()))
                        .WithRetainFlag();

                    await _mqttClient.PublishAsync(messageBuilder.Build(), CancellationToken.None);

                    messageBuilder.WithTopic("ahub/light/t5blue/in")
                        .WithPayload(Encoding.UTF8.GetBytes(values[0].ToString()));

                    await _mqttClient.PublishAsync(messageBuilder.Build(), CancellationToken.None);

                    Thread.Sleep(10000); // Delay between iterations
                }
            }
            catch (Exception ex)
            {
                _telemetryClient.TrackException(ex);
            }
            finally
            {
                _telemetryClient.Flush();
                Task.Delay(5000).Wait();  // Give time for flushing
            }
        }

        // Method to connect to the MQTT broker
        private static async Task ConnectMqttClientAsync()
        {
            try
            {
                await _mqttClient.ConnectAsync(_mqttOptions, CancellationToken.None);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Connection failed: {ex.Message}");
                // Wait before retrying to connect
                await Task.Delay(TimeSpan.FromSeconds(100));
                await ConnectMqttClientAsync();
            }
        }
    }
}
