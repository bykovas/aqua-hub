using MQTTnet;
using MQTTnet.Client;
using System.Text;

namespace AquaHub.NConsole
{
    internal class Program
    {
        static async Task Main(string[] args)
        {
            var mqttClient = await ConnectMqttClientAsync();

            //var test = new Test();
            //test.Foo();

            Console.WriteLine("Hello, World!");
            while (true)
            {
                var values = Schedule.get_current_values();
                var message = $"{DateTime.Now.ToShortTimeString()} - Blue plus: {values[0]}, Coral plus: {values[1]}";
                Console.WriteLine(message);

                // Publish to MQTT
                var messageBuilder = new MqttApplicationMessageBuilder()
                    .WithTopic("ahub/light/t5coral/in")
                    .WithPayload(Encoding.UTF8.GetBytes(values[1].ToString()))
                    .WithRetainFlag();

                await mqttClient.PublishAsync(messageBuilder.Build(), CancellationToken.None);

                messageBuilder.WithTopic("ahub/light/t5blue/in")
                    .WithPayload(Encoding.UTF8.GetBytes(values[0].ToString()));

                await mqttClient.PublishAsync(messageBuilder.Build(), CancellationToken.None);

                Thread.Sleep(10000);
            }
        }

        private static async Task<IMqttClient> ConnectMqttClientAsync()
        {
            var factory = new MqttFactory();
            var mqttClient = factory.CreateMqttClient();

            var options = new MqttClientOptionsBuilder()
                .WithCredentials("mqttu", "mqttp")
                .WithTcpServer("192.168.1.11")
                .Build();

            await mqttClient.ConnectAsync(options, CancellationToken.None);
            return mqttClient;
        }
    }
}
