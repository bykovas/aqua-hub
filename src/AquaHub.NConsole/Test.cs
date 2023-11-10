using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Nodes;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace AquaHub.NConsole
{


    public class Test
    {
        public void Foo()
        {
var result = new List<KeyValuePair<string, string>>
{
    new("001", "First Item"),
    new("002", "Second Item"),
    new("003", "Third Item"),
    new("004", "Fourth Item")
};
            var json = JsonConvert.SerializeObject(result.ToList());


        }
    }
}
