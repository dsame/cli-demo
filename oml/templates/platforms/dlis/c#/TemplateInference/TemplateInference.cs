using System;
using DeepLearning;

namespace Template
{
    public class TemplateInference : IDLWindowsModelV2
    {
        private Model model;

        public override void Initialize()
        {
            model = new Model();
        }

        public override string ExecuteString(string input) => model.Predict(input);

        public override ArraySegment<byte> ExecuteBinary(ArraySegment<byte> input) => throw new NotImplementedException();
    }
}
