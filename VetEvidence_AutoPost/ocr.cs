using System;
using System.IO;
using System.Threading.Tasks;
using Windows.Graphics.Imaging;
using Windows.Media.Ocr;
using Windows.Storage;

namespace OcrTest {
    class Program {
        static async Task Main(string[] args) {
            if (args.Length == 0) { Console.WriteLine("No file provided"); return; }
            string path = Path.GetFullPath(args[0]);
            try {
                StorageFile file = await StorageFile.GetFileFromPathAsync(path);
                using (var stream = await file.OpenAsync(FileAccessMode.Read)) {
                    var decoder = await BitmapDecoder.CreateAsync(stream);
                    var bitmap = await decoder.GetSoftwareBitmapAsync();
                    var engine = OcrEngine.TryCreateFromUserProfileLanguages();
                    if (engine == null) { Console.WriteLine("Engine null"); return; }
                    var result = await engine.RecognizeAsync(bitmap);
                    Console.WriteLine("SUCCESS|" + result.Text.Replace("\n", " ").Replace("\r", ""));
                }
            } catch (Exception ex) {
                Console.WriteLine("ERROR|" + ex.Message);
            }
        }
    }
}
