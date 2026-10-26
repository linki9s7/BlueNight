# クレジットと使用素材のライセンス

ゲームのスタッフロール・配布物に、以下の表記を入れること。

## 音源

| 素材 | 作者 | ライセンス | 使っている場所 |
| --- | --- | --- | --- |
| MuseScore General SoundFont | S. Christian Collins | MIT | すべての BGM の楽器 |
| 雨の録音 | Mike Koenig（soundbible.com。2014 年に Dawid Gan が切り出し） | CC BY 3.0（表記が必要） | 環境音「雨」 |
| 川の録音 | Adam Newns（vennaudio.com） | CC0（表記不要） | 環境音「雨」「波」 |
| 滝の録音 | Leonard "VKProduktion" Graf | CC0（表記不要） | 環境音「波」「遠くのハイウェイ」、効果音（影） |
| 金属を打つ録音 | dADDoiT、Mike Koenig、Marianne Gagnon | CC BY 3.0（表記が必要） | 効果音（ランタン、影を捕まえた） |
| 木を叩く録音 | "Stephan"（Marianne Gagnon が編集） | パブリックドメイン | 効果音（足音、影を捕まえた） |
| 時計の秒針の録音 | Natalie | パブリックドメイン | 効果音（ランタン、街灯のスイッチ） |
| 水に落ちる音の録音 | pacomav | CC0 | 効果音（濡れた路面の足音） |
| UI SFX（dreamy セット） | romainsimon/uisfx | CC0 | 効果音（決定・キャンセル・文字送りなどの UI 音） |

- 環境音の録音は Ubuntu の `supertuxkart-data` パッケージから取り出した（同パッケージの copyright ファイルにライセンス記載）。
  詳細は `Tools/Music/sources/README.md`。
- 表記例：`Rain recording by Mike Koenig (soundbible.com), licensed under CC BY 3.0`
- 表記例：`Metal clang recording by dADDoiT, Mike Koenig and Marianne Gagnon, licensed under CC BY 3.0`

## フォント

| 素材 | 作者 | ライセンス |
| --- | --- | --- |
| DotGothic16 | The DotGothic16 Project Authors（Fontworks） | SIL Open Font License 1.1（`Assets/008_Fonts/DotGothic16-OFL.txt` を同梱） |
| DejaVu Serif Bold（タイトルのロゴ画像 `Title/title_logo.png` のみ。アンチエイリアス無しで描いた画像で、フォントファイルは同梱しない） | DejaVu fonts team（Bitstream Vera を元にした書体） | Bitstream Vera Fonts のライセンス（自由に使用・改変可）。表記例：`Logo lettering based on DejaVu Serif Bold (DejaVu fonts, Bitstream Vera license)` |

## 使わないと判断したもの

| 素材 | 理由 |
| --- | --- |
| tonejs-instruments（npm の `tonejs-instrument-*`） | 録音の出どころとライセンスが記載されておらず、商用での利用可否を確認できないため |
| Salamander Grand Piano V3（Alexander Holm、CC BY 3.0） | ライセンスは問題ないが、リズムに合わせて低音が「ドシン」と響くのが不快とのユーザー判断 |
| 0 A.D. の環境音（Wildfire Games、CC BY-SA 3.0） | ユーザーの判断で使わない（一度ハイウェイと虫の背景に風・葉の音を使ったが、取りやめた） |
