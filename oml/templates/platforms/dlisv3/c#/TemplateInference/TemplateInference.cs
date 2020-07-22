using System;
using DeepLearning;

namespace Template
{
    public class TemplateInference : IDLWindowsModelV3
    {
        private Model model;

        public override void Initialize(ISystemContext sysContext, IExecutionContext exeContext)
        {
            model = new Model(sysContext, exeContext);
        }

        public override string ExecuteString(string input, ISystemContext sysContext, IExecutionContext exeContext) => model.Predict(input);

        public override ArraySegment<byte> ExecuteBinary(ArraySegment<byte> input, ISystemContext sysContext, IExecutionContext exeContext) => throw new NotImplementedException();
    }
}
