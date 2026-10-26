# 環境音の素材（録音）

`ambience.py` が素材として使う録音。どれも商用利用できるライセンスで、このリポジトリに同梱してよい。
入手経路：Ubuntu の `supertuxkart-data` パッケージ（各ファイルのライセンスは同パッケージの
`/usr/share/doc/supertuxkart-data/copyright` に記載）。

| ファイル | 内容 | 作者 | ライセンス | 元の出典 |
| --- | --- | --- | --- | --- |
| `rain_mike_koenig.ogg` | 雨の録音（3.8 秒、ステレオ） | Mike Koenig（2014 年に Dawid Gan が切り出し） | CC BY 3.0（**表記が必要**） | soundbible.com の雨の録音（SuperTuxKart 経由） |
| `river_adam_newns.ogg` | 川の流れ（15.6 秒、モノラル） | Adam Newns（vennaudio.com） | CC0（表記不要） | freesound.org/people/Adam_N/sounds/166310/ |
| `waterfall_leonard_graf.ogg` | 滝（14.9 秒、モノラル） | Leonard "VKProduktion" Graf | CC0（表記不要） | freesound.org/people/VKProduktion/sounds/215711/ |

- 短い録音を、ランダムな位置から切り出した断片をなめらかに重ね合わせて、繰り返しに聞こえない長い音にして使う（`ambience.py` の `texture`）。
- 表記が必要なものは `docs/CREDITS.md` にも書く。
