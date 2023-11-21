using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Nodes;
using System.Threading.Tasks;
using MQTTnet.Client;
using MQTTnet;
using Newtonsoft.Json;

namespace AquaHub.NConsole
{


    public class Test
    {
        public async void Foo()
        {
            var mqttFactory = new MqttFactory();
            using var mqttClient = mqttFactory.CreateMqttClient();

            var options = new MqttClientOptionsBuilder()
                .WithTcpServer("192.168.1.11")
                .Build();

            await mqttClient.ConnectAsync(options, CancellationToken.None);

            while (true)
            {
                double t = (DateTime.UtcNow - DateTime.UnixEpoch).TotalSeconds;
                double t5blueValue = (Math.Sin(2 * Math.PI * t / 20) + 1) * 50;
                double t5coralValue = 100 - t5blueValue;

                await mqttClient.PublishAsync(new MqttApplicationMessageBuilder()
                    .WithTopic("ahub/light/t5blue/in")
                    .WithPayload(((int)t5blueValue).ToString())
                    .Build());

                await mqttClient.PublishAsync(new MqttApplicationMessageBuilder()
                    .WithTopic("ahub/light/t5coral/in")
                    .WithPayload(((int)t5coralValue).ToString())
                    .Build());

                Thread.Sleep(1000);
            }
        }
    }
}
