param (
    [string]$ScriptPath
)

$fso = New-Object -ComObject Scripting.FileSystemObject
$pythonPath = $fso.GetFile(".\.venv\Scripts\python.exe").ShortPath
$env:PYSPARK_PYTHON = $pythonPath
$env:PYSPARK_DRIVER_PYTHON = $pythonPath
$env:SPARK_HOME = $fso.GetFolder(".\.venv\Lib\site-packages\pyspark").ShortPath

$hadoop_dir = "C:\Users\rayha\OneDrive\Documents\SEMESTER 4\2. Big Data & Lake House\SmartBudget Platform Lakehouse untuk Deteksi Anomali & Transparansi APBD Kota\hadoop"
$bin_dir = "$hadoop_dir\bin"
$env:HADOOP_HOME = $hadoop_dir
$env:PATH = "$bin_dir;" + $env:PATH

& $pythonPath $ScriptPath
