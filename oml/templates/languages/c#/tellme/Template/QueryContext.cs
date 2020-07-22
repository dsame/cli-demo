using System.Collections.Generic;

namespace Template
{
    public class QueryContext
    {
        public IEnumerable<CommandInfo> CommandClickedEvents;
        public IEnumerable<ActivityEventInfo> ActivityEvents;
    }
}
