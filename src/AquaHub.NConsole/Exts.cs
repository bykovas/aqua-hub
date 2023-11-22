using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Web;

namespace AquaHub.NConsole
{
    public interface IQueryStringSerializer
    { }

    public static class Exts
    {
        public static string ToQueryString(this IQueryStringSerializer obj)
        {
            var sb = new StringBuilder();
            var properties = obj.GetType().GetProperties();

            foreach (var p in properties)
            {
                if (!p.CanRead) continue;
                var value = p.GetValue(obj, null);
                if (value == null || IsDefaultValue(value)) continue;
                if (sb.Length > 0) sb.Append("&");

                sb.Append(p.Name).Append("=").Append(HttpUtility.UrlEncode(value.ToString()));
            }

            return sb.ToString();
        }

        private static bool IsDefaultValue(object value)
        {
            var type = value.GetType();
            return type.IsValueType && Equals(value, Activator.CreateInstance(type));
        }
    }
}
