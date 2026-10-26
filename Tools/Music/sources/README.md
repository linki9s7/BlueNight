# 環境音の素材（録音）

`ambience.py` が素材として使う録音。どれも商用利用できるライセンスで、このリポジトリに同梱してよい。
入手経路：Ubuntu の `supertuxkart-data` パッケージと `0ad-data` パッケージ（ライセンスは各パッケージの
`/usr/share/doc/<パッケージ名>/copyright` に記載）。

| ファイル | 内容 | 作者 | ライセンス | 元の出典 |
| --- | --- | --- | --- | --- |
| `rain_mike_koenig.ogg` | 雨の録音（3.8 秒、ステレオ） | Mike Koenig（2014 年に Dawid Gan が切り出し） | CC BY 3.0（**表記が必要**） | soundbible.com の雨の録音（SuperTuxKart 経由） |
| `river_adam_newns.ogg` | 川の流れ（15.6 秒、モノラル） | Adam Newns（vennaudio.com） | CC0（表記不要） | freesound.org/people/Adam_N/sounds/166310/ |
| `waterfall_leonard_graf.ogg` | 滝（14.9 秒、モノラル） | Leonard "VKProduktion" Graf | CC0（表記不要） | freesound.org/people/VKProduktion/sounds/215711/ |
| `wind_0ad.ogg` | 風（167.6 秒、ステレオ。無音部分を含む） | Wildfire Games（0 A.D.） | **CC BY-SA 3.0**（表記が必要・継承あり） | 0 A.D. `audio/ambient/weather/wind_11.ogg` |
| `windleaves_0ad_1.ogg` / `windleaves_0ad_2.ogg` | 風で葉がそよぐ音（各 4.7 秒、モノラル） | Wildfire Games（0 A.D.） | **CC BY-SA 3.0**（表記が必要・継承あり） | 0 A.D. `audio/ambient/weather/windleaves_10.ogg` / `_11.ogg` |

### CC BY-SA の素材について

- 0 A.D. の素材を混ぜた環境音（`ambient_highway.ogg`、`ambient_crickets.ogg`）は、**CC BY-SA 3.0 で配布する必要がある**
  （作者表記をし、その音声ファイルを同じライセンスで提供する）。ゲーム本体のプログラムや、ほかの素材には影響しない。
- ユーザーの許可：遠くのハイウェイと夜の虫に限って使ってよい（雨と波には使わない）。

- 短い録音を、ランダムな位置から切り出した断片をなめらかに重ね合わせて、繰り返しに聞こえない長い音にして使う（`ambience.py` の `texture`）。
- 表記が必要なものは `docs/CREDITS.md` にも書く。
