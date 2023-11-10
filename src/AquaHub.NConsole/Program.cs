namespace AquaHub.NConsole
{
    internal class Program
    {
        static void Main(string[] args)
        {
            var test = new Test();
            test.Foo();

            Console.WriteLine("Hello, World!");
            while(true)
            {
                var values = Schedule.get_current_values();
                Console.WriteLine($"{DateTime.Now.ToShortTimeString()} - Blue plus: {values[0]}, Coral plus: {values[1]}");
                Thread.Sleep(10000);
            }
        }
    }
}
