using System;
using System.IO;
using System.Threading;

using Template;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Collections.Generic;
using System.Text;
using System.Linq;

namespace UnitTest
{
    [TestClass]
    public class ModelTest
    {
        private const string PredictionFileName = "predictions.txt";
        private static readonly char[] Seperators = new char[] { '\t' };
        private static Model model;

        [ClassInitialize]
        public static void Initialize(TestContext context)
        {
            var systemContext = new LocalSystemContext();
            var executionContext = new LocalExecutionContext();
            model = new Model(systemContext, executionContext);
        }

        private static IEnumerable<string[]> Predictions
        {
            get
            {
                var predictions = new List<string[]>();
                using (var file = new StreamReader(PredictionFileName))
                {
                    string line;
                    while ((line = file.ReadLine()) != null)
                    {
                        predictions.Add(line.Split(Seperators));
                    }
                }

                return predictions;
            }
        }

        [DataTestMethod]
        [DynamicData(nameof(Predictions))]
        public void TestPredictions(string input, string expected)
        {
            string predicted = model.Predict(input);
            Console.Out.WriteLine(String.Format("Predicted: {0}", predicted));
            Console.Out.WriteLine(String.Format("Expected: {0}", expected));
            Assert.AreEqual(expected, predicted);
        }

        [TestMethod]
        public void TestBinaryPredictions()
        {
            // Replace with a meaningful test with Predict with binary input data is implemented.
            try
            {
                var predicted = model.Predict(new ArraySegment<byte>(new byte[] { })).Array;
                Assert.Fail();
            }
            catch (NotImplementedException)
            {
                return;
            }
            catch(Exception)
            {
                Assert.Fail();
            }
        }
    }
}
