using System;
using System.Threading;

namespace Template
{
    class Program
    {
        static void Main(string[] args)
        {
            // Simulates systemContext and executionContext for DLIS V3 interface.
            var systemContext = new LocalSystemContext();
            var executionContext = new LocalExecutionContext();
            var model = new Model(systemContext, executionContext);

            string option;
            string data = "";
            // Running exe
            if (args.Length > 0)
            {
                option = args[0];
                if (args.Length > 1)
                {
                    data = args[1];
                }
                Execute(model, option, data, systemContext);
            }
            // Running from VS as console
            else
            {
                while (true)
                {
                    option = "predict";
                    Console.WriteLine("Enter the input for the prediction:");
                    data = Console.ReadLine();
                    Execute(model, option, data, systemContext);
                }
            }
        }

        static void Execute(Model model, string option, string data, LocalSystemContext systemContext)
        {
            switch (option)
            {
                case "predict":
                    var output = model.Predict(data);
                    Console.WriteLine(output);
                    // Example of how to print properties used in DLIS systemContext and executionContext
                    var counterFactory = (LocalCounterFactory)systemContext.CounterFactory;
                    foreach (LocalCounter c in counterFactory.Counters)
                    {
                        Console.WriteLine(c.CounterName + ": " + c.Value);
                    }
                    foreach (var field in systemContext.AdditionalFields)
                    {
                        Console.WriteLine(field.Key + ": " + field.Value);
                    }
                    return;
                case "predictBinary":
                    // To test on a console, the binary input data can be converted to base64 
                    // string and then passed with predictBinary option. 
                    var binaryData = new ArraySegment<byte>(Convert.FromBase64String(data));
                    var binaryOutput = model.Predict(binaryData);
                    Console.WriteLine(Convert.ToBase64String(binaryOutput.Array));
                    return;
                case "eval":
                    model.Eval();
                    return;
                default:
                    Console.WriteLine("Call with params predict or eval");
                    return;
            }
        }
    }
}
