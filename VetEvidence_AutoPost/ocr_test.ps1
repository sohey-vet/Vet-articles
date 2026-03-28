param (
    [string]$ImagePath = "C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\①月_下痢_犬の急性下痢_最新エビデンス\note_thumbnail.png"
)

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$code = @"
using System;
using System.IO;
using System.Threading.Tasks;
using Windows.Graphics.Imaging;
using Windows.Media.Ocr;
using Windows.Storage;

public class OcrHelper {
    public static async Task<string> ExtractText(string path) {
        StorageFile file = await StorageFile.GetFileFromPathAsync(path);
        using (var stream = await file.OpenAsync(FileAccessMode.Read)) {
            var decoder = await BitmapDecoder.CreateAsync(stream);
            var bitmap = await decoder.GetSoftwareBitmapAsync();
            var engine = OcrEngine.TryCreateFromUserProfileLanguages();
            var result = await engine.RecognizeAsync(bitmap);
            return result.Text;
        }
    }
}
"@

try {
    Add-Type -TypeDefinition $code -Language CSharp -IgnoreWarnings -ReferencedAssemblies @("System.Runtime.WindowsRuntime", "C:\Windows\System32\WinMetadata\Windows.Foundation.winmd", "C:\Windows\System32\WinMetadata\Windows.Graphics.winmd", "C:\Windows\System32\WinMetadata\Windows.Media.winmd", "C:\Windows\System32\WinMetadata\Windows.Storage.winmd")
} catch {
    Write-Host "Compile Error: $_"
    exit
}

$text = [OcrHelper]::ExtractText($ImagePath).GetAwaiter().GetResult()
Write-Host "OCR Result:"
Write-Host $text
