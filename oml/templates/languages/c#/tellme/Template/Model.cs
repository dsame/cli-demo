using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using Microsoft.ML.Scoring;

namespace Template
{
    public class Model : BaseModel, IDisposable
    {
        private ModelManager m_manager;
        private Dictionary<int, int> m_input_TCID_to_index;
        private Dictionary<int, int> m_output_index_to_TCID;
        private bool m_disposed = false;
        private int m_seqLen = -1;

        public Model()
        {
            string seq_fpath = Path.Combine(dataDir, @"sequenceLength.txt");
            using (StreamReader input = new StreamReader(seq_fpath))
            {
                m_seqLen = Int32.Parse(input.ReadLine());
            }

            m_input_TCID_to_index = new Dictionary<int, int>();
            string input_index_fpath = Path.Combine(dataDir, @"inputIndex.txt");
            using (StreamReader input = new StreamReader(input_index_fpath))
            {
                String line;
                while ((line = input.ReadLine()) != null)
                {
                    String[] value = line.Split('\t');
                    if (value.Length != 2)
                    {
                        throw new Exception("ERROR: inputIndex.txt does not have 2 tab-delimited columns");
                    }
                    m_input_TCID_to_index[Int32.Parse(value[0])] = Int32.Parse(value[1]);
                }
            }
            m_output_index_to_TCID = new Dictionary<int, int>();
            string output_index_fpath = Path.Combine(dataDir, @"outputIndex.txt");
            using (StreamReader input = new StreamReader(output_index_fpath))
            {
                String line;
                while ((line = input.ReadLine()) != null)
                {
                    String[] value = line.Split('\t');
                    if (value.Length != 2)
                    {
                        throw new Exception("ERROR: outputIndex.txt does not have 2 tab-delimited columns");
                    }
                    m_output_index_to_TCID[Int32.Parse(value[1])] = Int32.Parse(value[0]);
                }
            }
            m_manager = new ModelManager(dataDir, true);
            m_manager.InitModel("TellMe", Int32.MaxValue);
            Predict("{\"CommandClickedEvents\":[{\"Id\":1,\"TimeElapsedSinceClick\":0.5},{\"Id\":3,\"TimeElapsedSinceClick\":1.0},{\"Id\":17,\"TimeElapsedSinceClick\":1.5},{\"Id\":19,\"TimeElapsedSinceClick\":2.0},{\"Id\":21,\"TimeElapsedSinceClick\":2.5},{\"Id\":22,\"TimeElapsedSinceClick\":3.0},{\"Id\":25,\"TimeElapsedSinceClick\":3.5},{\"Id\":106,\"TimeElapsedSinceClick\":4.0},{\"Id\":108,\"TimeElapsedSinceClick\":4.5},{\"Id\":113,\"TimeElapsedSinceClick\":5.0},{\"Id\":114,\"TimeElapsedSinceClick\":5.5},{\"Id\":115,\"TimeElapsedSinceClick\":6.0},{\"Id\":120,\"TimeElapsedSinceClick\":6.5},{\"Id\":121,\"TimeElapsedSinceClick\":7.0},{\"Id\":122,\"TimeElapsedSinceClick\":7.5},{\"Id\":128,\"TimeElapsedSinceClick\":8.0},{\"Id\":129,\"TimeElapsedSinceClick\":8.5},{\"Id\":150,\"TimeElapsedSinceClick\":9.0},{\"Id\":151,\"TimeElapsedSinceClick\":9.5},{\"Id\":186,\"TimeElapsedSinceClick\":10.0}]}");
        }

        public override string Predict(string data)
        {
            Stopwatch stopwatch = new Stopwatch();
            stopwatch.Start();
            List<int> observedIndexList = new List<int>();
            List<float> observedTimingList = new List<float>();
            if (!String.IsNullOrEmpty(data))
            {
                QueryContext events = Newtonsoft.Json.JsonConvert.DeserializeObject<QueryContext>(data);
                if ((events != null) && (events.CommandClickedEvents != null))
                {
                    foreach (CommandInfo command in events.CommandClickedEvents.Reverse<CommandInfo>())
                    {
                        int sparseIndex = command.Id;
                        if (m_input_TCID_to_index.ContainsKey(sparseIndex))
                        {
                            observedIndexList.Add(m_input_TCID_to_index[sparseIndex]);
                        }
                        else
                        {
                            observedIndexList.Add(2);
                        }
                        observedTimingList.Add((float)Math.Pow(10.0, -command.TimeElapsedSinceClick / 600.0));
                    }
                }
            }
            int totalCount = observedIndexList.Count;
            int ignoreCount = 0;
            if (totalCount > m_seqLen)
            {
                ignoreCount = totalCount - m_seqLen;
            }
            int observedCount = totalCount - ignoreCount;
            List<int> indexList = new List<int>();
            List<float> timingList = new List<float>();
            int paddingCount = m_seqLen - observedCount;
            if (paddingCount > 0)
            {
                for (int i = 0; i < (paddingCount - 1); i++)
                {
                    indexList.Add(0);
                    timingList.Add(0.0f);
                }
                indexList.Add(1);
                timingList.Add(0.0f);
            }
            if (observedCount > 0)
            {
                indexList.AddRange(observedIndexList.GetRange(ignoreCount, observedCount));
                timingList.AddRange(observedTimingList.GetRange(ignoreCount, observedCount));
            }
            List<long> shape = new List<long>() { 1, m_seqLen };
            List<Tensor> inputs = new List<Tensor>();
            Tensor tensor1 = new Tensor(indexList, shape);
            inputs.Add(tensor1);
            Tensor tensor2 = new Tensor(timingList, shape);
            inputs.Add(tensor2);
            List<string> inputNames = new List<string> { "input1", "input2" };
            List<string> outputNames = new List<string> { "index", "probability" };
            List<Tensor> result = m_manager.RunModel("TellMe", Int32.MaxValue, inputNames, inputs, outputNames);
            List<int> index = new List<int>();
            result[0].CopyTo(index);
            List<float> probability = new List<float>();
            result[1].CopyTo(probability);
            String output =
                "\"CommandList\":[" +
                    m_output_index_to_TCID[index[0]] + "," +
                    m_output_index_to_TCID[index[1]] + "," +
                    m_output_index_to_TCID[index[2]] + "," +
                    m_output_index_to_TCID[index[3]] + "," +
                    m_output_index_to_TCID[index[4]] + "," +
                    m_output_index_to_TCID[index[5]] + "," +
                    m_output_index_to_TCID[index[6]] + "," +
                    m_output_index_to_TCID[index[7]] + "," +
                    m_output_index_to_TCID[index[8]] + "," +
                    m_output_index_to_TCID[index[9]] + "]," +
                "\"ProbabilityList\":[" +
                    probability[0] + "," +
                    probability[1] + "," +
                    probability[2] + "," +
                    probability[3] + "," +
                    probability[4] + "," +
                    probability[5] + "," +
                    probability[6] + "," +
                    probability[7] + "," +
                    probability[8] + "," +
                    probability[9] + "]";
            stopwatch.Stop();
            return "{" + output + ",\"SecondsElapsed\":" + stopwatch.Elapsed.TotalSeconds + "}";
        }

        public override void Eval()
        {
            PublishScore(0, 0);
        }

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        protected virtual void Dispose(bool disposing)
        {
            if (!m_disposed)
            {
                if (disposing)
                {
                    m_manager.Dispose();
                }
                m_disposed = true;
            }
        }
    }
}
