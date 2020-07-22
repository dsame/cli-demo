using System;
using System.IO;

using Template;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace UnitTest
{
    [TestClass]
    public class ModelTest
    {
        private static readonly char[] Seperators = new char[] { '\t' };
        private static Model model;

        [ClassInitialize]
        public static void Initialize(TestContext context)
        {
            model = new Model();
        }

        private static IEnumerable<string[]> Predictions
        {
            get
            {
                var predictions = new List<string[]>();
                using (var file = new StreamReader("predictions.txt"))
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

        struct Probability
        {
            public List<int> CommandList { get; set; }
            public List<double> ProbabilityList { get; set; }
            public double SecondsElapsed { get; set; }
        }

        [DataTestMethod]
        [DynamicData(nameof(Predictions))]
        public void TestPredictions(string input, string expected)
        {
            string predicted = model.Predict(input);
            var expectedProbability = JsonConvert.DeserializeObject<Probability>(expected);
            var predictedProbability = JsonConvert.DeserializeObject<Probability>(predicted);
            CollectionAssert.AreEqual(expectedProbability.ProbabilityList, predictedProbability.ProbabilityList);
        }
    }
}
