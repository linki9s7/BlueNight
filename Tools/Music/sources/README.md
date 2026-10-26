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

## 効果音の素材（`sfx.py` が使う）

| ファイル | 内容 | 作者 | ライセンス | 元の出典 |
| --- | --- | --- | --- | --- |
| `knock_wood_stephan.ogg` | 木を叩く音（0.5 秒） | "Stephan"（2010 年に Marianne Gagnon が編集） | パブリックドメイン | pdsounds.org「knocking on wood or door」（SuperTuxKart の `wooden_bridge.ogg`） |
| `clock_ticking_natalie.ogg` | 時計の秒針の音（6.8 秒） | Natalie | パブリックドメイン | pdsounds.org「clock ticking」（SuperTuxKart の `clock.ogg`） |
| `metal_clang.ogg` | 金属を打つ音（5.2 秒） | dADDoiT、Mike Koenig、Marianne Gagnon | CC BY 3.0（**表記が必要**） | SuperTuxKart の `metal_clang.ogg` |
| `plop_pacomav.ogg` | 水に落ちる「ぽちゃ」（0.4 秒） | pacomav | CC0 | freesound.org/people/pacomav/sounds/273792/ |
| `uisfx_dreamy/*.ogg` | UI の効果音（dreamy セット） | UI SFX（romainsimon/uisfx） | CC0（`uisfx_dreamy/LICENSE-AUDIO.txt`） | npm パッケージ `uisfx` 0.4.0 |

