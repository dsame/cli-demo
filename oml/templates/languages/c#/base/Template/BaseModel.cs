using System;
using System.IO;
using DeepLearning;

namespace Template
{
    public abstract class BaseModel
    {
        protected string baseDir;
        protected string dataDir;
        protected string modelDir;

        protected IExecutionContext executionContext;
        protected ISystemContext systemContext;

        protected BaseModel(ISystemContext systemContext, IExecutionContext executionContext)
        {
            this.baseDir = AppDomain.CurrentDomain.BaseDirectory;
            this.dataDir = Path.Combine(baseDir, @"data");
            this.modelDir = Path.Combine(dataDir, @"model");
            this.executionContext = executionContext;
            this.systemContext = systemContext;
        }

        public abstract string Predict(string data);

        public abstract ArraySegment<byte> Predict(ArraySegment<byte> binaryData);

        public abstract void Eval();

        protected void PublishScore(float precision, float recall)
        {
            string precisionStr = $"precision: {precision}";
            string recallStr = $"recall: {recall}";
            string scoreFile = Path.Combine(baseDir, @".score");

            if (File.Exists(scoreFile))
            {
                File.Delete(scoreFile);
            }

            using (FileStream fs = File.Create(scoreFile))
            {
                TextWriter tw = new StreamWriter(fs);
                tw.WriteLine(precisionStr);
                tw.WriteLine(recallStr);
                tw.Close();
            }

            Console.WriteLine("-----------Result-----------");
            Console.WriteLine(precisionStr);
            Console.WriteLine(recallStr);
            Console.WriteLine("----------------------------");
        }
    }
}
