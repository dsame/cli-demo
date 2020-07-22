using System;
using System.IO;

namespace Template
{
    public abstract class BaseModel
    {
        protected string baseDir;
        protected string dataDir;
        protected string modelDir;

        protected BaseModel()
        {
            baseDir = AppDomain.CurrentDomain.BaseDirectory;
            dataDir = Path.Combine(baseDir, @"data");
            modelDir = Path.Combine(dataDir, @"model");
        }

        public abstract string Predict(string data);

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
