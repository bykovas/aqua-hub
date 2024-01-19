using System.Text.Json;
using System.Text.Json.Serialization;

namespace AquaHub.NConsole
{
    public static class Schedule
    {
        private static DateTime? _demoModeExpireTime = null;
        private static List<ScheduleEntry> _currentSchedule;
        private static readonly FileSystemWatcher watcher = new();

        static Schedule()
        {
            watcher.Path = Directory.GetCurrentDirectory();
            watcher.Filter = "schedule.json";
            watcher.NotifyFilter = NotifyFilters.LastWrite;
            watcher.Changed += OnChanged;
            watcher.EnableRaisingEvents = true;

            _currentSchedule = LoadSchedule("ReefMoreBlue");
        }

        private static void OnChanged(object sender, FileSystemEventArgs e)
        {
            _currentSchedule = LoadSchedule("ReefMoreBlue");
        }

        public static Dictionary<string, int> get_current_values()
        {
            return CalculateCurrentValues(_currentSchedule);
        }

        private static List<ScheduleEntry> LoadSchedule(string scheduleName)
        {
            var json = File.ReadAllText("schedule.json");
            var schedules = JsonSerializer.Deserialize<Dictionary<string, List<ScheduleEntry>>>(json);
            foreach (var entry in schedules?[scheduleName]!)
                entry.ParsedTime = TimeSpan.Parse(entry.Time);
            return schedules[scheduleName];
        }

        private static Dictionary<string, int> CalculateCurrentValues(IReadOnlyList<ScheduleEntry> schedule)
        {
            var now = DateTime.Now.TimeOfDay;
            int? currentBluePlus = null;
            int? currentCoralPlus = null;
            int? currentPhotoRed = null;

            for (var i = 0; i < schedule.Count - 1; i++)
            {
                var start = schedule[i].ParsedTime;
                var end = schedule[i + 1].ParsedTime;

                if (start <= now && now <= end)
                {
                    if (schedule[i].BluePlus.HasValue || schedule[i + 1].BluePlus.HasValue)
                        currentBluePlus = (int)Interpolate(schedule[i].BluePlus, schedule[i + 1].BluePlus, start, end, now);

                    if (schedule[i].CoralPlus.HasValue || schedule[i + 1].CoralPlus.HasValue)
                        currentCoralPlus = (int)Interpolate(schedule[i].CoralPlus, schedule[i + 1].CoralPlus, start, end, now);

                    if (schedule[i].PhotoRed.HasValue || schedule[i + 1].PhotoRed.HasValue)
                        currentPhotoRed = (int)Interpolate(schedule[i].PhotoRed, schedule[i + 1].PhotoRed, start, end, now);
                }
            }

            var sched = new Dictionary<string, int>
            {
                { "BluePlus", currentBluePlus ?? 0 },
                { "CoralPlus", currentCoralPlus ?? 0 },
                { "PhotoRed", currentPhotoRed ?? 0 }
            };

            //return new int[] { currentBluePlus ?? 0, currentCoralPlus ?? 0, currentPhotoRed ?? 0 };
            return sched;
        }

        private static double Interpolate(int? startValue, int? endValue, TimeSpan startTime, TimeSpan endTime, TimeSpan currentTime)
        {
            startValue ??= 0;
            endValue ??= 0;

            double fraction = (currentTime - startTime).TotalSeconds / (endTime - startTime).TotalSeconds;
            return startValue.Value + (endValue.Value - startValue.Value) * fraction;
        }

        public static void set_demo_mode(double? seconds = null)
        {
            _demoModeExpireTime = DateTime.Now.AddSeconds(seconds ?? 30);
        }

        public static bool is_demo_mode()
        {
            return _demoModeExpireTime > DateTime.Now;
        }
    }

    public class ScheduleEntry
    {
        [JsonPropertyName("t")]
        public string Time { get; set; }

        public int? CoralPlus { get; set; }

        public int? BluePlus { get; set; }

        public int? PhotoRed { get; set; }

        [JsonIgnore]
        public TimeSpan ParsedTime { get; set; }
    }
}
