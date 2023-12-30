using System;
using MQTTnet;
using MQTTnet.Client;
using MQTTnet.Protocol;
using System.Threading.Tasks;
using System.Text;

class Program
{
    static async Task Main(string[] args)
    {
        var mqttFactory = new MqttFactory();
        var mqttClient = mqttFactory.CreateMqttClient();

        var options = new MqttClientOptionsBuilder()
            .WithTcpServer("192.168.1.11", 1883)
            .WithCredentials("mqttu", "mqttp")
            .Build();

        mqttClient.ConnectedAsync += async e =>
        {
            Console.WriteLine("Connected to MQTT Broker!");
            await mqttClient.SubscribeAsync("ahub/debug", MqttQualityOfServiceLevel.AtLeastOnce);
            Console.WriteLine("Subscribed to topic ahub/debug");
        };

        mqttClient.DisconnectedAsync += async e =>
        {
            Console.WriteLine("Disconnected from MQTT Broker");
        };

        mqttClient.ApplicationMessageReceivedAsync += async e =>
        {
            var message = e.ApplicationMessage;
            if (message.Topic == "ahub/debug")
            {
                var delayTime = Convert.ToInt32(Encoding.UTF8.GetString(message.Payload));
                Console.WriteLine($"Received delay time: {delayTime} ms");

                var messageDry = new MqttApplicationMessageBuilder()
                    .WithTopic("ahub/sump/ahub_ato_main_water_level_sensor/out")
                    .WithPayload("dry")
                    .Build();

                await mqttClient.PublishAsync(messageDry, CancellationToken.None);
                await Task.Delay(delayTime);

                var messageWet = new MqttApplicationMessageBuilder()
                    .WithTopic("ahub/sump/ahub_ato_main_water_level_sensor/out")
                    .WithPayload("wet")
                    .Build();

                await mqttClient.PublishAsync(messageWet, CancellationToken.None);
            }
        };

        await mqttClient.ConnectAsync(options);
        Console.WriteLine("Press any key to exit");
        Console.ReadLine();
        await mqttClient.DisconnectAsync();
    }
}
