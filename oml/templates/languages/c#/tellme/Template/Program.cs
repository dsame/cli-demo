using System;

namespace Template
{
    class Program
    {
        static void Main(string[] args)
        {
            var model = new Model();
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
                Execute(model, option, data);
            }
            // Running from VS as console
            else
            {
                while (true)
                {
                    option = "predict";
                    Console.WriteLine("Enter the input for the prediction:");
                    data = Console.ReadLine();
                    Execute(model, option, data);
                }
            }
        }

        static void Execute(Model model, string option, string data)
        {
            switch (option)
            {
                case "predict":
                    var output = model.Predict(data);
                    Console.WriteLine(output);
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
