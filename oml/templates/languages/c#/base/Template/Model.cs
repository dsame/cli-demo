using System;
using System.Collections.Generic;
using System.Text;
using DeepLearning;

namespace Template
{
    public class Model : BaseModel
    {
        /// <summary>
        /// Class for OfficeML C# models. Streamlines the workflow for testing and pushing models into production
        /// </summary>
        public Model(ISystemContext systemContext, IExecutionContext executionContext) : base(systemContext, executionContext)
        {
            /// <summary>
            /// Model constructor is used to create a representation of the desired model and load other 
            /// static files necessary for deployment
            /// </summary>

        }

        public override string Predict(string data)
        {
            /// <summary>
            /// Predicts a given value that the trained model would return based on the data input value
            /// </summary>
            /// <returns>
            /// The trained model's prediction
            /// </returns>
            return $"Hello {data}!";
        }

        public override ArraySegment<byte> Predict(ArraySegment<byte> binaryData)
        {
            /// <summary>
            /// Predicts a given value that the trained model would return based on binary serialized 
            /// input data value
            /// </summary>
            /// <returns>
            /// The trained model's prediction serialized with a binary serializer
            /// </returns>
            throw new NotImplementedException();
        }

        public override void Eval()
        {
            /// <summary>
            /// Outputs the batch precision and recall on the trained model
            /// </summary>
            PublishScore(0, 0);
        }
    }
}
