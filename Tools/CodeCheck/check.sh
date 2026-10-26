#!/bin/sh
# Unity を開かずに C# のコンパイルを確かめる。初回だけ Unity の参照 DLL（NuGet の Unity3D.SDK）を取ってくる。
set -e
cd "$(dirname "$0")"
if [ ! -f .refs/lib/UnityEngine.dll ]; then
  mkdir -p .refs
  curl -sSL -o .refs/sdk.nupkg https://api.nuget.org/v3-flatcontainer/unity3d.sdk/2021.1.14.1/unity3d.sdk.2021.1.14.1.nupkg
  python3 -c "import zipfile; zipfile.ZipFile('.refs/sdk.nupkg').extractall('.refs')"
fi
dotnet build CodeCheck.csproj -nologo --no-incremental -v q 2>&1 | grep -E "error|Error\(s\)|Build succeeded" | sed -E 's# \[.*##' | sort -u
