using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using DeepLearning;

namespace Template
{
    /// <summary>
    /// Class for emulating DLIS SystemContext to help run model locally
    /// and print values of properties.
    /// </summary>
    public class LocalSystemContext : ISystemContext
    {
        public LocalSystemContext()
        {
            this.Logger = new LocalLogger();
            this.CounterFactory = new LocalCounterFactory();
            this.AdditionalFields = new ConcurrentDictionary<string, object>();
        }

        public ILogger Logger { get; }

        public ICounterFactory CounterFactory { get; }

        public ConcurrentDictionary<string, object> AdditionalFields { get; }
    }

    /// <summary>
    /// Class for emulating DLIS ExecutionContext to help run model locally
    /// and print values of properties.
    /// </summary>
    public class LocalExecutionContext : IExecutionContext
    {
        public LocalExecutionContext()
        {
            this.IsDebug = true;
            this.TraceId = "12345";
            this.CancellationToken = new CancellationToken(false);
            this.AdditionalFields = new ConcurrentDictionary<string, object>();
        }

        public bool IsDebug { get; }

        public string TraceId { get; }

        public CancellationToken CancellationToken { get; }

        public ConcurrentDictionary<string, object> AdditionalFields { get; }
    }

    public class LocalCounter : ICounter
    {
        public LocalCounter(
            string counterName,
            CounterFlag flag,
            Dictionary<string, string> settings,
            List<CounterDimension> dims)
        {
            this.CounterName = counterName;
            this.Flag = flag;
            this.Settings = settings;
            this.Dims = dims;
            this.Value = 0;
        }

        public string CounterName { get; }
        public CounterFlag Flag { get; }
        public Dictionary<string, string> Settings { get; }
        public List<CounterDimension> Dims { get; }
        public long Value { get; private set; }

        public void Increment()
        {
        }

        public void IncrementBy(long value)
        {
        }

        public void Set(long value) => this.Value = value;
    }

    public class LocalCounterFactory : ICounterFactory
    {
        public LocalCounterFactory()
        {
            this.Counters = new List<LocalCounter>();
        }

        public List<LocalCounter> Counters { get; }
        public ICounter GetOrCreateCounter(string counterName, CounterFlag flag) =>
            GetOrCreateCounter(counterName, flag, new Dictionary<string, string>(), new List<CounterDimension>());

        public ICounter GetOrCreateCounter(string counterName, CounterFlag flag, Dictionary<string, string> settings, List<CounterDimension> dims)
        {
            var counter = new LocalCounter(counterName, flag, settings, dims);
            this.Counters.Add(counter);
            return counter;
        }
    }

    public class LocalLogger : ILogger
    {
        public void Log(IExecutionContext context, LogLevel logLevel, string msg) => Console.WriteLine(msg);

        public void Log(IExecutionContext context, LogLevel logLevel, string msgFmt, params object[] args) => Console.WriteLine(msgFmt, args);

        public bool NeedLog(IExecutionContext context, LogLevel logLevel) => true;
    }
}
